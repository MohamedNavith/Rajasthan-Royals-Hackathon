"""
Player Pressure Performance & Rating Calculation Module.
Computes:
- Pressure vs Normal performance metrics for batters and bowlers.
- Contextual metrics: Runs Over Expected (ROE), Wickets Over Expected (WOE), WPA.
- Elevating metrics: Delta Strike Rate, Delta Economy, Delta Dismissal, Boundary Control.
- Match-level consistency (% of pressure matches with positive net impact).
- Empirical Bayes shrinkage towards league baseline to handle sample size variations fairly.
- Composite Pressure Reliability Index (0 - 100 normalized score).
"""
import numpy as np
import pandas as pd
from src.config import (
    MIN_PRESSURE_BALLS_BATTER, MIN_PRESSURE_BALLS_BOWLER,
    MIN_TOTAL_BALLS_BATTER, MIN_TOTAL_BALLS_BOWLER,
    EB_BATTER_PRIOR_WEIGHT, EB_BOWLER_PRIOR_WEIGHT
)

def compute_batter_ratings(
    df: pd.DataFrame,
    pressure_col: str = 'is_high_pressure',
    min_pressure_balls: int = MIN_PRESSURE_BALLS_BATTER,
    min_total_balls: int = MIN_TOTAL_BALLS_BATTER,
    prior_k: float = EB_BATTER_PRIOR_WEIGHT
) -> pd.DataFrame:
    """
    Computes comprehensive pressure rating for all eligible batters.
    """
    # Only legal balls faced count towards balls faced
    legal_df = df[df['is_legal_ball']].copy()
    
    # Aggregations per batter
    # Total stats
    total_agg = legal_df.groupby('striker_id').agg(
        total_balls=('batter_runs', 'count'),
        total_runs=('batter_runs', 'sum'),
        total_dismissals=('is_wicket', 'sum'),
        player_name=('striker_name', 'last'),
        total_matches=('match_id', 'nunique'),
        ipl_balls=('is_ipl', lambda x: x.sum())
    )
    
    # Split: Pressure deliveries vs Normal deliveries
    press_df = legal_df[legal_df[pressure_col]]
    norm_df = legal_df[~legal_df[pressure_col]]
    
    press_agg = press_df.groupby('striker_id').agg(
        press_balls=('batter_runs', 'count'),
        press_runs=('batter_runs', 'sum'),
        press_dismissals=('is_wicket', 'sum'),
        press_dots=('batter_runs', lambda x: (x == 0).sum()),
        press_fours=('is_four', 'sum'),
        press_sixes=('is_six', 'sum'),
        press_roe=('runs_over_expected_batter', 'sum'),
        press_doe=('dismissal_over_expected_batter', 'sum'),
        press_wpa=('wpa_batting_team', 'sum'),
        press_matches=('match_id', 'nunique')
    )
    
    norm_agg = norm_df.groupby('striker_id').agg(
        norm_balls=('batter_runs', 'count'),
        norm_runs=('batter_runs', 'sum'),
        norm_dismissals=('is_wicket', 'sum')
    )
    
    # Match-level consistency under pressure:
    # In each match where batter faced >= 3 pressure balls, was their net pressure impact (ROE or WPA) > 0?
    match_press = press_df.groupby(['striker_id', 'match_id']).agg(
        m_balls=('batter_runs', 'count'),
        m_roe=('runs_over_expected_batter', 'sum'),
        m_wpa=('wpa_batting_team', 'sum')
    ).reset_index()
    match_press = match_press[match_press['m_balls'] >= 3]
    match_press['is_positive_impact'] = (match_press['m_roe'] > 0) | (match_press['m_wpa'] > 0)
    consistency = match_press.groupby('striker_id')['is_positive_impact'].agg(
        press_matches_considered='count',
        positive_matches='sum'
    )
    consistency['consistency_pct'] = np.where(
        consistency['press_matches_considered'] > 0,
        consistency['positive_matches'] / consistency['press_matches_considered'] * 100.0,
        50.0
    )
    
    # Combine tables
    batters = total_agg.join(press_agg, how='inner').join(norm_agg, how='left').join(consistency, how='left')
    batters['consistency_pct'] = batters['consistency_pct'].fillna(50.0)
    
    # Filter eligibility
    eligible = batters[
        (batters['press_balls'] >= min_pressure_balls) & 
        (batters['total_balls'] >= min_total_balls)
    ].copy()
    
    # Calculate rates
    # Normal strike rate & dismissal rate
    eligible['norm_sr'] = np.where(eligible['norm_balls'] > 0, (eligible['norm_runs'] / eligible['norm_balls']) * 100.0, 130.0)
    eligible['norm_dismissal_rate'] = np.where(eligible['norm_balls'] > 0, eligible['norm_dismissals'] / eligible['norm_balls'], 0.05)
    
    # Pressure strike rate & dismissal rate
    eligible['press_sr'] = (eligible['press_runs'] / eligible['press_balls']) * 100.0
    eligible['press_dismissal_rate'] = eligible['press_dismissals'] / eligible['press_balls']
    
    # Deltas (Pressure vs Normal)
    eligible['sr_delta'] = eligible['press_sr'] - eligible['norm_sr']
    # Negative dismissal delta means batter gets dismissed LESS often under pressure than normal
    eligible['dismissal_rate_delta'] = eligible['press_dismissal_rate'] - eligible['norm_dismissal_rate']
    
    # Per-ball contextual metrics under pressure
    eligible['roe_per_ball'] = eligible['press_roe'] / eligible['press_balls']
    eligible['wpa_per_ball'] = eligible['press_wpa'] / eligible['press_balls']
    
    # Competition strength adjustment factor (IPL vs T20I ratio)
    ipl_ratio = eligible['ipl_balls'] / eligible['total_balls']
    eligible['comp_factor'] = 0.90 + 0.20 * ipl_ratio  # 0.90 to 1.10 multiplier
    
    # Raw Composite Score:
    # 35% ROE per ball + 35% WPA per ball (scaled) + 15% SR Delta (scaled) + 15% Consistency
    # Standardize components across eligible cohort
    z_roe = (eligible['roe_per_ball'] - eligible['roe_per_ball'].mean()) / (eligible['roe_per_ball'].std() + 1e-6)
    z_wpa = (eligible['wpa_per_ball'] - eligible['wpa_per_ball'].mean()) / (eligible['wpa_per_ball'].std() + 1e-6)
    z_sr_delta = (eligible['sr_delta'] - eligible['sr_delta'].mean()) / (eligible['sr_delta'].std() + 1e-6)
    z_cons = (eligible['consistency_pct'] - eligible['consistency_pct'].mean()) / (eligible['consistency_pct'].std() + 1e-6)
    
    raw_z = (0.35 * z_roe + 0.35 * z_wpa + 0.15 * z_sr_delta + 0.15 * z_cons) * eligible['comp_factor']
    eligible['raw_score'] = raw_z
    
    # Empirical Bayes Shrinkage
    # Weight on player evidence: w = N / (N + K)
    shrinkage_weight = eligible['press_balls'] / (eligible['press_balls'] + prior_k)
    eligible['shrinkage_weight'] = shrinkage_weight
    eligible['shrunk_score'] = shrinkage_weight * eligible['raw_score'] + (1.0 - shrinkage_weight) * 0.0
    
    # Scale final score to intuitive 0 - 100 rating (with 50 = replacement level / average under pressure)
    # 50 + 15 * shrunk_score
    eligible['pressure_rating'] = np.clip(50.0 + 15.0 * eligible['shrunk_score'], 0.0, 100.0)
    
    # Sort descending
    eligible = eligible.sort_values('pressure_rating', ascending=False).reset_index()
    eligible['rank'] = eligible.index + 1
    
    return eligible

def compute_bowler_ratings(
    df: pd.DataFrame,
    pressure_col: str = 'is_high_pressure',
    min_pressure_balls: int = MIN_PRESSURE_BALLS_BOWLER,
    min_total_balls: int = MIN_TOTAL_BALLS_BOWLER,
    prior_k: float = EB_BOWLER_PRIOR_WEIGHT
) -> pd.DataFrame:
    """
    Computes comprehensive pressure rating for all eligible bowlers.
    """
    legal_df = df[df['is_legal_ball']].copy()
    legal_df['is_boundary'] = legal_df['is_four'] | legal_df['is_six']
    
    # Total bowling stats
    total_agg = legal_df.groupby('bowler_id').agg(
        total_balls=('bowler_runs_conceded', 'count'),
        total_runs_conceded=('bowler_runs_conceded', 'sum'),
        total_wickets=('is_bowler_wicket', 'sum'),
        player_name=('bowler_name', 'last'),
        total_matches=('match_id', 'nunique'),
        ipl_balls=('is_ipl', lambda x: x.sum())
    )
    
    press_df = legal_df[legal_df[pressure_col]]
    norm_df = legal_df[~legal_df[pressure_col]]
    
    press_agg = press_df.groupby('bowler_id').agg(
        press_balls=('bowler_runs_conceded', 'count'),
        press_runs_conceded=('bowler_runs_conceded', 'sum'),
        press_wickets=('is_bowler_wicket', 'sum'),
        press_dots=('bowler_runs_conceded', lambda x: (x == 0).sum()),
        press_boundaries=('is_boundary', 'sum'),
        press_runs_saved=('runs_saved_bowler', 'sum'),
        press_woe=('wickets_over_expected_bowler', 'sum'),
        press_wpa=('wpa_bowling_team', 'sum'),
        press_matches=('match_id', 'nunique')
    )
    
    norm_agg = norm_df.groupby('bowler_id').agg(
        norm_balls=('bowler_runs_conceded', 'count'),
        norm_runs_conceded=('bowler_runs_conceded', 'sum'),
        norm_wickets=('is_bowler_wicket', 'sum'),
        norm_dots=('bowler_runs_conceded', lambda x: (x == 0).sum()),
        norm_boundaries=('is_boundary', 'sum')
    )
    
    # Match-level consistency under pressure:
    match_press = press_df.groupby(['bowler_id', 'match_id']).agg(
        m_balls=('bowler_runs_conceded', 'count'),
        m_saved=('runs_saved_bowler', 'sum'),
        m_wpa=('wpa_bowling_team', 'sum')
    ).reset_index()
    match_press = match_press[match_press['m_balls'] >= 3]
    match_press['is_positive_impact'] = (match_press['m_saved'] > 0) | (match_press['m_wpa'] > 0)
    consistency = match_press.groupby('bowler_id')['is_positive_impact'].agg(
        press_matches_considered='count',
        positive_matches='sum'
    )
    consistency['consistency_pct'] = np.where(
        consistency['press_matches_considered'] > 0,
        consistency['positive_matches'] / consistency['press_matches_considered'] * 100.0,
        50.0
    )
    
    bowlers = total_agg.join(press_agg, how='inner').join(norm_agg, how='left').join(consistency, how='left')
    bowlers['consistency_pct'] = bowlers['consistency_pct'].fillna(50.0)
    
    # Filter eligibility
    eligible = bowlers[
        (bowlers['press_balls'] >= min_pressure_balls) & 
        (bowlers['total_balls'] >= min_total_balls)
    ].copy()
    
    # Rates
    eligible['norm_economy'] = np.where(eligible['norm_balls'] > 0, (eligible['norm_runs_conceded'] / eligible['norm_balls']) * 6.0, 8.5)
    eligible['press_economy'] = (eligible['press_runs_conceded'] / eligible['press_balls']) * 6.0
    # Economy delta: normal - pressure (positive means economy improved/lower under pressure)
    eligible['economy_delta'] = eligible['norm_economy'] - eligible['press_economy']
    
    eligible['norm_dot_pct'] = np.where(eligible['norm_balls'] > 0, (eligible['norm_dots'] / eligible['norm_balls']) * 100.0, 35.0)
    eligible['press_dot_pct'] = (eligible['press_dots'] / eligible['press_balls']) * 100.0
    eligible['dot_pct_delta'] = eligible['press_dot_pct'] - eligible['norm_dot_pct']
    
    eligible['runs_saved_per_ball'] = eligible['press_runs_saved'] / eligible['press_balls']
    eligible['woe_per_ball'] = eligible['press_woe'] / eligible['press_balls']
    eligible['wpa_per_ball'] = eligible['press_wpa'] / eligible['press_balls']
    
    # Competition multiplier
    ipl_ratio = eligible['ipl_balls'] / eligible['total_balls']
    eligible['comp_factor'] = 0.90 + 0.20 * ipl_ratio
    
    # Standardize components
    z_saved = (eligible['runs_saved_per_ball'] - eligible['runs_saved_per_ball'].mean()) / (eligible['runs_saved_per_ball'].std() + 1e-6)
    z_woe = (eligible['woe_per_ball'] - eligible['woe_per_ball'].mean()) / (eligible['woe_per_ball'].std() + 1e-6)
    z_wpa = (eligible['wpa_per_ball'] - eligible['wpa_per_ball'].mean()) / (eligible['wpa_per_ball'].std() + 1e-6)
    z_econ_delta = (eligible['economy_delta'] - eligible['economy_delta'].mean()) / (eligible['economy_delta'].std() + 1e-6)
    z_cons = (eligible['consistency_pct'] - eligible['consistency_pct'].mean()) / (eligible['consistency_pct'].std() + 1e-6)
    
    raw_z = (0.30 * z_saved + 0.25 * z_woe + 0.25 * z_wpa + 0.10 * z_econ_delta + 0.10 * z_cons) * eligible['comp_factor']
    eligible['raw_score'] = raw_z
    
    shrinkage_weight = eligible['press_balls'] / (eligible['press_balls'] + prior_k)
    eligible['shrinkage_weight'] = shrinkage_weight
    eligible['shrunk_score'] = shrinkage_weight * eligible['raw_score'] + (1.0 - shrinkage_weight) * 0.0
    
    eligible['pressure_rating'] = np.clip(50.0 + 15.0 * eligible['shrunk_score'], 0.0, 100.0)
    
    eligible = eligible.sort_values('pressure_rating', ascending=False).reset_index()
    eligible['rank'] = eligible.index + 1
    
    return eligible
