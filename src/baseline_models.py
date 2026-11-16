"""
Contextual Expected Outcome Baselines Module.
Estimates:
- Batting: Expected Runs per ball (xRuns) and Expected Dismissal Probability (xDismissal)
- Bowling: Expected Runs Conceded (xRunsConceded) and Expected Wicket Probability (xWicket)
Controls for:
- Match Phase (Powerplay, Middle, Death)
- Bowling discipline (Pace vs Spin)
- Competition tier (IPL vs T20I)
- Venue scoring index
- Batter batting order
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
from src.config import RANDOM_SEED

class ContextualBaselineModels:
    def __init__(self):
        self.batter_runs_model = None
        self.batter_dismissal_model = None
        self.bowler_runs_model = None
        self.bowler_wicket_model = None
        
        self.phase_map = {'Powerplay': 0, 'Middle': 1, 'Death': 2}
        self.tier_map = {'IPL': 0, 'T20I': 1, 'Other_T20': 2}
        self.pace_spin_map = {'Pace': 0, 'Spin': 1}
        self.venue_means = {}
        self.overall_mean_rpo = 8.2

    def _prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        # Phase (0, 1, 2)
        phase_enc = df['phase'].map(self.phase_map).fillna(1).values
        # Competition tier (0, 1, 2)
        tier_enc = df['comp_tier'].map(self.tier_map).fillna(1).values
        # Pace vs Spin (0 for Pace, 1 for Spin)
        is_spin = df['pace_or_spin'].astype(str).str.contains('Spin', case=False, na=False).astype(int).values
        # Batting order (1..11)
        batting_order = df['batting_order'].fillna(4).clip(1, 11).values
        # Over number (0..19)
        over_num = df['overid'].fillna(10).clip(0, 19).values
        # Innings (1 or 2)
        innings = df['innings'].clip(1, 2).values
        
        # Venue score index (normalized relative to overall average)
        venue_idx = df['venue_id'].map(self.venue_means).fillna(self.overall_mean_rpo).values / self.overall_mean_rpo
        
        X = np.column_stack([
            phase_enc, tier_enc, is_spin, batting_order, over_num, innings, venue_idx
        ])
        return X

    def fit(self, df: pd.DataFrame):
        """Fit baseline expectation models across all historical legal deliveries."""
        # Train on regular legal deliveries
        train_df = df[
            (~df['is_super_over']) & 
            (~df['is_abandoned_or_no_result']) & 
            (df['is_legal_ball'])
        ].copy()
        
        # Compute venue scoring rates
        venue_rpo = train_df.groupby('venue_id')['bowler_runs_conceded'].mean() * 6.0
        self.venue_means = venue_rpo.to_dict()
        if len(train_df) > 0:
            self.overall_mean_rpo = train_df['bowler_runs_conceded'].mean() * 6.0
            
        X = self._prepare_features(train_df)
        
        # 1. Batter Expected Runs (per legal delivery)
        y_batter_runs = train_df['batter_runs'].values
        self.batter_runs_model = HistGradientBoostingRegressor(
            max_iter=80, max_depth=5, min_samples_leaf=50, random_state=RANDOM_SEED
        )
        self.batter_runs_model.fit(X, y_batter_runs)
        
        # 2. Batter Expected Dismissal Probability
        y_batter_dism = train_df['is_wicket'].astype(int).values
        self.batter_dismissal_model = HistGradientBoostingClassifier(
            max_iter=80, max_depth=5, min_samples_leaf=50, random_state=RANDOM_SEED
        )
        self.batter_dismissal_model.fit(X, y_batter_dism)
        
        # 3. Bowler Expected Runs Conceded
        y_bowler_runs = train_df['bowler_runs_conceded'].values
        self.bowler_runs_model = HistGradientBoostingRegressor(
            max_iter=80, max_depth=5, min_samples_leaf=50, random_state=RANDOM_SEED
        )
        self.bowler_runs_model.fit(X, y_bowler_runs)
        
        # 4. Bowler Expected Wicket Probability (bowler wickets only)
        y_bowler_wkt = train_df['is_bowler_wicket'].astype(int).values
        self.bowler_wicket_model = HistGradientBoostingClassifier(
            max_iter=80, max_depth=5, min_samples_leaf=50, random_state=RANDOM_SEED
        )
        self.bowler_wicket_model.fit(X, y_bowler_wkt)
        
        print("Contextual baseline models successfully trained.")

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add expected baseline metrics and deltas to every ball in the dataset."""
        df = df.copy()
        X = self._prepare_features(df)
        
        df['xRuns_batter'] = self.batter_runs_model.predict(X)
        df['xDismissal_batter'] = self.batter_dismissal_model.predict_proba(X)[:, 1]
        
        df['xRuns_bowler'] = self.bowler_runs_model.predict(X)
        df['xWicket_bowler'] = self.bowler_wicket_model.predict_proba(X)[:, 1]
        
        # Deltas
        # Batting: positive runs over expected is good
        df['runs_over_expected_batter'] = df['batter_runs'] - df['xRuns_batter']
        # Batting: negative dismissal over expected is good (survived difficult ball)
        df['dismissal_over_expected_batter'] = df['is_wicket'].astype(int) - df['xDismissal_batter']
        
        # Bowling: runs saved (expected - actual conceded) is positive/good
        df['runs_saved_bowler'] = df['xRuns_bowler'] - df['bowler_runs_conceded']
        # Bowling: wickets above expected (actual - expected) is positive/good
        df['wickets_over_expected_bowler'] = df['is_bowler_wicket'].astype(int) - df['xWicket_bowler']
        
        return df
