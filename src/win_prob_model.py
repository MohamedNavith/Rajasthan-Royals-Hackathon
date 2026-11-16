"""
Win Probability & Leverage Index (Pressure) Modeling Module.
Implements:
1. Calibrated LightGBM models for Innings 1 and Innings 2.
2. Expected Leverage Index (WPLI) based on transition swings.
3. Win Probability Added (WPA) for batter and bowler.
4. Two alternative pressure definitions (Contextual Tension Index CTI, and Late Close Filter LCF).
"""
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, log_loss
from src.config import RANDOM_SEED, LEVERAGE_QUANTILE_THRESHOLD

class WinProbabilityModel:
    def __init__(self):
        self.inn1_model = None
        self.inn2_model = None
        self.venue_pars = {}
        self.overall_par = 165.0
        
        # Empirical outcome transition probabilities for T20 cricket:
        # (outcome_name, run_delta, wicket_delta, legal_ball_delta, prior_prob)
        self.transitions = [
            ('dot', 0, 0, 1, 0.36),
            ('single', 1, 0, 1, 0.38),
            ('two', 2, 0, 1, 0.07),
            ('four', 4, 0, 1, 0.10),
            ('six', 6, 0, 1, 0.05),
            ('wicket', 0, 1, 1, 0.04)
        ]
        
    def _compute_venue_pars(self, df: pd.DataFrame):
        """Compute average 1st innings par score per venue."""
        inn1_matches = df[(df['innings'] == 1) & (~df['is_super_over']) & (~df['is_abandoned_or_no_result'])]
        match_scores = inn1_matches.groupby(['match_id', 'venue_id'])['delivery_runs'].sum().reset_index()
        venue_means = match_scores.groupby('venue_id')['delivery_runs'].mean().to_dict()
        self.venue_pars = venue_means
        if len(match_scores) > 0:
            self.overall_par = match_scores['delivery_runs'].mean()

    def _get_inn1_features(self, df: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame(index=df.index)
        features['current_score'] = df['current_score']
        features['legal_balls_bowled'] = df['legal_balls_bowled']
        features['balls_remaining'] = df['balls_remaining']
        features['wickets_in_hand'] = df['wickets_in_hand']
        features['current_run_rate'] = df['current_run_rate']
        
        # Venue par
        v_par = df['venue_id'].map(self.venue_pars).fillna(self.overall_par)
        features['venue_par'] = v_par
        
        # Projected score vs par
        # Projected: current + (balls_remaining / 6) * baseline_rate
        # Rate blends current run rate with par rate based on overs remaining
        rem_overs = df['balls_remaining'] / 6.0
        bowled_overs = df['legal_balls_bowled'] / 6.0
        weight_crr = np.clip(bowled_overs / 20.0, 0.1, 0.9)
        blended_rate = weight_crr * df['current_run_rate'] + (1 - weight_crr) * (v_par / 20.0)
        projected = df['current_score'] + rem_overs * blended_rate
        features['projected_score_diff'] = projected - v_par
        features['is_ipl'] = df['is_ipl'].astype(int)
        
        return features

    def _get_inn2_features(self, df: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame(index=df.index)
        features['current_score'] = df['current_score']
        features['legal_balls_bowled'] = df['legal_balls_bowled']
        features['balls_remaining'] = df['balls_remaining']
        features['wickets_in_hand'] = df['wickets_in_hand']
        features['target'] = df['target'].fillna(165)
        features['runs_needed'] = df['runs_needed'].fillna(100)
        features['required_run_rate'] = np.clip(df['required_run_rate'].fillna(8.0), 0, 36)
        features['current_run_rate'] = df['current_run_rate']
        
        v_par = df['venue_id'].map(self.venue_pars).fillna(self.overall_par)
        features['venue_par'] = v_par
        features['is_ipl'] = df['is_ipl'].astype(int)
        
        return features

    def fit(self, df: pd.DataFrame):
        """Train and calibrate Innings 1 and Innings 2 win probability models."""
        # Filter valid matches
        train_df = df[
            (~df['is_super_over']) & 
            (~df['is_abandoned_or_no_result']) & 
            (df['win_team_id'].notna())
        ].copy()
        
        # Compute venue pars
        self._compute_venue_pars(train_df)
        
        # Target: did batting team win?
        train_df['batting_team_won'] = (train_df['batting_team_id'] == train_df['win_team_id']).astype(int)
        
        # 1. Fit Innings 1 model
        inn1_data = train_df[train_df['innings'] == 1]
        X1 = self._get_inn1_features(inn1_data)
        y1 = inn1_data['batting_team_won']
        
        base_lgbm1 = LGBMClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.05,
            random_state=RANDOM_SEED, min_child_samples=30, verbose=-1
        )
        self.inn1_model = CalibratedClassifierCV(estimator=base_lgbm1, method='isotonic', cv=3)
        self.inn1_model.fit(X1, y1)
        
        # 2. Fit Innings 2 model
        inn2_data = train_df[train_df['innings'] == 2]
        X2 = self._get_inn2_features(inn2_data)
        y2 = inn2_data['batting_team_won']
        
        base_lgbm2 = LGBMClassifier(
            n_estimators=120, max_depth=5, learning_rate=0.05,
            random_state=RANDOM_SEED, min_child_samples=30, verbose=-1
        )
        self.inn2_model = CalibratedClassifierCV(estimator=base_lgbm2, method='isotonic', cv=3)
        self.inn2_model.fit(X2, y2)
        
        print("Win Probability models successfully trained and calibrated.")

    def predict_win_prob_inn1(self, state_df: pd.DataFrame) -> np.ndarray:
        """Predict win prob for batting team in 1st innings."""
        X = self._get_inn1_features(state_df)
        return self.inn1_model.predict_proba(X)[:, 1]

    def predict_win_prob_inn2(self, state_df: pd.DataFrame) -> np.ndarray:
        """Predict win prob for batting team in 2nd innings."""
        # Boundary logic for completed chases:
        probs = np.zeros(len(state_df))
        
        # If target reached: WP = 1.0
        reached = state_df['runs_needed'] <= 0
        # If all out (wickets in hand == 0) and runs needed > 0: WP = 0.0
        all_out = (state_df['wickets_in_hand'] <= 0) & (state_df['runs_needed'] > 0)
        # If balls remaining == 0 and runs needed > 0: WP = 0.0
        balls_out = (state_df['balls_remaining'] <= 0) & (state_df['runs_needed'] > 0)
        
        active_mask = (~reached) & (~all_out) & (~balls_out)
        if active_mask.any():
            X_active = self._get_inn2_features(state_df[active_mask])
            pred_active = self.inn2_model.predict_proba(X_active)[:, 1]
            probs[active_mask.values] = pred_active
            
        probs[reached.values] = 1.0
        probs[all_out.values] = 0.0
        probs[balls_out.values] = 0.0
        return np.clip(probs, 0.0, 1.0)

    def compute_ball_leverage(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes Leverage Index for each ball:
        Expected swing in win probability across potential immediate outcomes.
        Also calculates actual delivery WPA.
        """
        df = df.copy()
        
        # 1. Base Win Probability before delivery
        df['wp_batting_team'] = np.nan
        
        mask_inn1 = df['innings'] == 1
        mask_inn2 = df['innings'] == 2
        
        if mask_inn1.any():
            df.loc[mask_inn1, 'wp_batting_team'] = self.predict_win_prob_inn1(df[mask_inn1])
        if mask_inn2.any():
            df.loc[mask_inn2, 'wp_batting_team'] = self.predict_win_prob_inn2(df[mask_inn2])
            
        # Post-ball Win Probability
        # Create post-state slice to predict post WP
        post_df = df.copy()
        post_df['current_score'] = df['post_score']
        post_df['current_wickets'] = df['post_wickets']
        post_df['wickets_in_hand'] = np.maximum(0, 10 - post_df['current_wickets'])
        post_df['legal_balls_bowled'] = df['post_legal_balls_bowled']
        post_df['balls_remaining'] = df['post_balls_remaining']
        post_df['runs_needed'] = df['post_runs_needed']
        
        rem_overs = post_df['balls_remaining'] / 6.0
        post_df['required_run_rate'] = np.where(
            post_df['balls_remaining'] > 0,
            post_df['runs_needed'] / rem_overs,
            post_df['runs_needed'] * 6.0
        )
        bowled_overs = post_df['legal_balls_bowled'] / 6.0
        post_df['current_run_rate'] = np.where(
            bowled_overs > 0,
            post_df['current_score'] / bowled_overs,
            0.0
        )
        
        df['post_wp_batting_team'] = np.nan
        if mask_inn1.any():
            df.loc[mask_inn1, 'post_wp_batting_team'] = self.predict_win_prob_inn1(post_df[mask_inn1])
        if mask_inn2.any():
            df.loc[mask_inn2, 'post_wp_batting_team'] = self.predict_win_prob_inn2(post_df[mask_inn2])
            
        # Win Probability Added (WPA)
        df['wpa_batting_team'] = df['post_wp_batting_team'] - df['wp_batting_team']
        df['wpa_bowling_team'] = -df['wpa_batting_team']
        
        # 2. Expected Leverage Index (WPLI) across transition tree
        leverage_scores = np.zeros(len(df))
        base_wp = df['wp_batting_team'].fillna(0.5).values
        
        # We compute expected absolute swing: sum(P(outcome) * |WP(outcome) - base_WP|)
        # For efficiency and precision, compute for each transition branch
        for _, runs_d, wkt_d, ball_d, prob in self.transitions:
            temp_df = df.copy()
            temp_df['current_score'] = df['current_score'] + runs_d
            temp_df['current_wickets'] = df['current_wickets'] + wkt_d
            temp_df['wickets_in_hand'] = np.maximum(0, 10 - temp_df['current_wickets'])
            temp_df['legal_balls_bowled'] = df['legal_balls_bowled'] + ball_d
            temp_df['balls_remaining'] = np.maximum(0, df['innings_total_legal_balls'] - temp_df['legal_balls_bowled'])
            temp_df['runs_needed'] = np.maximum(0, df['target'] - temp_df['current_score'])
            
            t_rem_overs = temp_df['balls_remaining'] / 6.0
            temp_df['required_run_rate'] = np.where(
                temp_df['balls_remaining'] > 0,
                temp_df['runs_needed'] / t_rem_overs,
                temp_df['runs_needed'] * 6.0
            )
            t_bowled_overs = temp_df['legal_balls_bowled'] / 6.0
            temp_df['current_run_rate'] = np.where(
                t_bowled_overs > 0,
                temp_df['current_score'] / t_bowled_overs,
                0.0
            )
            
            temp_wp = np.zeros(len(df))
            if mask_inn1.any():
                temp_wp[mask_inn1.values] = self.predict_win_prob_inn1(temp_df[mask_inn1])
            if mask_inn2.any():
                temp_wp[mask_inn2.values] = self.predict_win_prob_inn2(temp_df[mask_inn2])
                
            swing = np.abs(temp_wp - base_wp)
            leverage_scores += prob * swing
            
        df['leverage_index'] = leverage_scores
        
        # Scale leverage index so league mean = 1.0 (standard LI interpretation)
        mean_li = df['leverage_index'].mean()
        if mean_li > 0:
            df['normalized_leverage'] = df['leverage_index'] / mean_li
        else:
            df['normalized_leverage'] = df['leverage_index']
            
        # 3. High Pressure Flag (Primary: Top 25% quantile of leverage)
        cutoff = df['leverage_index'].quantile(LEVERAGE_QUANTILE_THRESHOLD)
        df['is_high_pressure_wpli'] = df['leverage_index'] >= cutoff
        
        # 4. Alternative Pressure Definition 1: Contextual Tension Index (CTI)
        # Combines RRR pressure, late death overs, and wickets lost
        # High pressure if in Death overs (overs 15-19) with WP between 0.20 and 0.80,
        # OR 2nd inn RRR >= 10.0 and balls remaining <= 60,
        # OR 1st inn with 4+ wickets down in Powerplay/Middle.
        cond_cti = (
            (mask_inn2 & (df['required_run_rate'] >= 9.5) & (df['balls_remaining'] <= 60)) |
            ((df['overid'] >= 15) & (df['wp_batting_team'] >= 0.20) & (df['wp_batting_team'] <= 0.80)) |
            (mask_inn1 & (df['current_wickets'] >= 4) & (df['overid'] <= 12))
        )
        df['is_high_pressure_cti'] = cond_cti
        
        # 5. Alternative Pressure Definition 2: Late Close Filter (LCF)
        # Strictly close matches in the last 8 overs (balls remaining <= 48 and WP in [0.25, 0.75])
        cond_lcf = (df['balls_remaining'] <= 48) & (df['wp_batting_team'] >= 0.25) & (df['wp_batting_team'] <= 0.75)
        df['is_high_pressure_lcf'] = cond_lcf
        
        # Default primary pressure definition
        df['is_high_pressure'] = df['is_high_pressure_wpli']
        
        return df
