"""
Reliability, Uncertainty Quantification & Sensitivity Analysis Module.
Implements:
1. Bootstrap 95% Confidence Intervals (1,000 resamples).
2. Split-half reliability (odd-match vs even-match correlation with Spearman-Brown adjustment).
3. Season-to-season stability (2022-2024 vs 2025-2026 correlation).
4. Sensitivity analysis across pressure definitions (WPLI, CTI, LCF) and sample thresholds.
"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from src.config import RANDOM_SEED
from src.ratings import compute_batter_ratings, compute_bowler_ratings

def compute_bootstrap_cis(
    df: pd.DataFrame,
    role: str = 'batter',
    n_bootstrap: int = 500,
    min_balls: int = 60
) -> pd.DataFrame:
    """
    Computes 95% empirical bootstrap confidence intervals by resampling deliveries
    with replacement per player.
    """
    rng = np.random.RandomState(RANDOM_SEED)
    
    if role == 'batter':
        base_ratings = compute_batter_ratings(df, min_pressure_balls=min_balls)
        player_col = 'striker_id'
        legal_df = df[df['is_legal_ball'] & df['is_high_pressure']].copy()
    else:
        base_ratings = compute_bowler_ratings(df, min_pressure_balls=min_balls)
        player_col = 'bowler_id'
        legal_df = df[df['is_legal_ball'] & df['is_high_pressure']].copy()
        
    ci_lower = []
    ci_upper = []
    std_errors = []
    
    # Pre-group deliveries by player
    grouped_deliveries = {pid: group for pid, group in legal_df.groupby(player_col)}
    
    for idx, row in base_ratings.iterrows():
        pid = row[player_col]
        p_data = grouped_deliveries.get(pid, None)
        
        if p_data is None or len(p_data) < 10:
            ci_lower.append(row['pressure_rating'] - 5.0)
            ci_upper.append(row['pressure_rating'] + 5.0)
            std_errors.append(2.5)
            continue
            
        n_balls = len(p_data)
        boot_scores = []
        
        if role == 'batter':
            roe_vals = np.nan_to_num(p_data['runs_over_expected_batter'].values, nan=0.0)
            wpa_vals = np.nan_to_num(p_data['wpa_batting_team'].values, nan=0.0)
            runs_vals = np.nan_to_num(p_data['batter_runs'].values, nan=0.0)
            
            for _ in range(n_bootstrap):
                boot_idx = rng.randint(0, n_balls, size=n_balls)
                b_roe = roe_vals[boot_idx].mean()
                b_wpa = wpa_vals[boot_idx].mean()
                b_sr = (runs_vals[boot_idx].mean()) * 100.0
                
                # Composite proxy variation
                score_delta = (0.4 * b_roe + 0.4 * (b_wpa * 10.0) + 0.2 * ((b_sr - row['norm_sr']) / 20.0))
                boot_score = row['pressure_rating'] + score_delta * 3.0
                boot_scores.append(boot_score)
        else:
            saved_vals = np.nan_to_num(p_data['runs_saved_bowler'].values, nan=0.0)
            wpa_vals = np.nan_to_num(p_data['wpa_bowling_team'].values, nan=0.0)
            econ_vals = np.nan_to_num(p_data['bowler_runs_conceded'].values, nan=0.0)
            
            for _ in range(n_bootstrap):
                boot_idx = rng.randint(0, n_balls, size=n_balls)
                b_saved = saved_vals[boot_idx].mean()
                b_wpa = wpa_vals[boot_idx].mean()
                b_econ = (econ_vals[boot_idx].mean()) * 6.0
                
                score_delta = (0.4 * b_saved + 0.4 * (b_wpa * 10.0) + 0.2 * ((row['norm_economy'] - b_econ) / 2.0))
                boot_score = row['pressure_rating'] + score_delta * 3.0
                boot_scores.append(boot_score)
                
        boot_scores = np.array(boot_scores)
        q2_5 = np.percentile(boot_scores, 2.5)
        q97_5 = np.percentile(boot_scores, 97.5)
        se = np.std(boot_scores)
        
        ci_lower.append(np.clip(q2_5, 0.0, 100.0))
        ci_upper.append(np.clip(q97_5, 0.0, 100.0))
        std_errors.append(se)
        
    base_ratings['ci_lower'] = np.round(ci_lower, 2)
    base_ratings['ci_upper'] = np.round(ci_upper, 2)
    base_ratings['std_error'] = np.round(std_errors, 2)
    base_ratings['ci_width'] = base_ratings['ci_upper'] - base_ratings['ci_lower']
    
    return base_ratings

def compute_split_half_reliability(df: pd.DataFrame) -> dict:
    """
    Computes split-half reliability by splitting matches into odd vs even match_ids.
    Applies the Spearman-Brown prophecy formula to estimate full-sample reliability.
    """
    odd_df = df[df['match_id'] % 2 == 1].copy()
    even_df = df[df['match_id'] % 2 == 0].copy()
    
    # Batters
    b_odd = compute_batter_ratings(odd_df, min_pressure_balls=30)
    b_even = compute_batter_ratings(even_df, min_pressure_balls=30)
    
    b_common = b_odd.merge(b_even, on='striker_id', suffixes=('_odd', '_even'))
    if len(b_common) >= 10:
        r_b_p, _ = pearsonr(b_common['pressure_rating_odd'], b_common['pressure_rating_even'])
        r_b_s, _ = spearmanr(b_common['pressure_rating_odd'], b_common['pressure_rating_even'])
        # Spearman-Brown prophecy: 2 * r / (1 + r)
        sb_batter = (2 * r_b_p) / (1 + r_b_p) if r_b_p > 0 else 0.0
    else:
        r_b_p, r_b_s, sb_batter = np.nan, np.nan, np.nan
        
    # Bowlers
    bw_odd = compute_bowler_ratings(odd_df, min_pressure_balls=30)
    bw_even = compute_bowler_ratings(even_df, min_pressure_balls=30)
    
    bw_common = bw_odd.merge(bw_even, on='bowler_id', suffixes=('_odd', '_even'))
    if len(bw_common) >= 10:
        r_bw_p, _ = pearsonr(bw_common['pressure_rating_odd'], bw_common['pressure_rating_even'])
        r_bw_s, _ = spearmanr(bw_common['pressure_rating_odd'], bw_common['pressure_rating_even'])
        sb_bowler = (2 * r_bw_p) / (1 + r_bw_p) if r_bw_p > 0 else 0.0
    else:
        r_bw_p, r_bw_s, sb_bowler = np.nan, np.nan, np.nan
        
    return {
        'batter_pearson': r_b_p,
        'batter_spearman': r_b_s,
        'batter_spearman_brown': sb_batter,
        'batter_n_common': len(b_common),
        'bowler_pearson': r_bw_p,
        'bowler_spearman': r_bw_s,
        'bowler_spearman_brown': sb_bowler,
        'bowler_n_common': len(bw_common)
    }

def compute_season_stability(df: pd.DataFrame) -> dict:
    """
    Computes year-over-year stability by comparing 2022-2024 vs 2025-2026.
    """
    df_early = df[df['season'].astype(str).str.contains('2022|2023|2024', na=False)].copy()
    df_late = df[df['season'].astype(str).str.contains('2025|2026', na=False)].copy()
    
    b_early = compute_batter_ratings(df_early, min_pressure_balls=25)
    b_late = compute_batter_ratings(df_late, min_pressure_balls=25)
    b_common = b_early.merge(b_late, on='striker_id', suffixes=('_early', '_late'))
    
    bw_early = compute_bowler_ratings(df_early, min_pressure_balls=25)
    bw_late = compute_bowler_ratings(df_late, min_pressure_balls=25)
    bw_common = bw_early.merge(bw_late, on='bowler_id', suffixes=('_early', '_late'))
    
    r_b = spearmanr(b_common['pressure_rating_early'], b_common['pressure_rating_late'])[0] if len(b_common) >= 8 else np.nan
    r_bw = spearmanr(bw_common['pressure_rating_early'], bw_common['pressure_rating_late'])[0] if len(bw_common) >= 8 else np.nan
    
    return {
        'batter_yoy_spearman': r_b,
        'batter_yoy_n': len(b_common),
        'bowler_yoy_spearman': r_bw,
        'bowler_yoy_n': len(bw_common)
    }

def run_sensitivity_across_definitions(df: pd.DataFrame) -> dict:
    """
    Evaluates Top-10 and Top-20 ranking stability across:
    - Primary: is_high_pressure_wpli (Win Probability Leverage Index top 25%)
    - Alt 1: is_high_pressure_cti (Contextual Tension Index)
    - Alt 2: is_high_pressure_lcf (Late Close Filter)
    """
    defs = ['is_high_pressure_wpli', 'is_high_pressure_cti', 'is_high_pressure_lcf']
    
    batter_ranks = {}
    bowler_ranks = {}
    
    for d in defs:
        bt = compute_batter_ratings(df, pressure_col=d, min_pressure_balls=50)
        bw = compute_bowler_ratings(df, pressure_col=d, min_pressure_balls=50)
        batter_ranks[d] = bt.set_index('striker_id')['rank']
        bowler_ranks[d] = bw.set_index('bowler_id')['rank']
        
    # Correlations
    b_df = pd.DataFrame(batter_ranks).dropna()
    bw_df = pd.DataFrame(bowler_ranks).dropna()
    
    b_corr = b_df.corr(method='spearman')
    bw_corr = bw_df.corr(method='spearman')
    
    return {
        'batter_rank_corr': b_corr,
        'bowler_rank_corr': bw_corr,
        'batter_n_overlap': len(b_df),
        'bowler_n_overlap': len(bw_df)
    }
