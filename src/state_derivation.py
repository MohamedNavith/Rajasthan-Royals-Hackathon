"""
Match state derivation module.
Derives cumulative match state ball-by-ball:
- Cumulative runs and cumulative wickets (prior to delivery)
- Legal balls bowled and legal balls remaining
- Target, runs needed, and required run rate (RRR) for 2nd innings chases
- Match phase (Powerplay, Middle, Death)
- Outcome of the current delivery (runs, wickets, post-delivery state)
"""
import pandas as pd
import numpy as np

def derive_match_states(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derives running score, wickets, balls remaining, target, RRR, and match phase.
    Must be executed on clean ball-by-ball data sorted chronologically.
    """
    df = df.copy()
    
    # Ensure deterministic sort order within match and innings
    df = df.sort_values(
        by=['match_id', 'innings', 'overid', 'innings_ball_num', 'over_ball_num']
    ).reset_index(drop=True)
    
    # 1. Total innings overs allocated (default 20, or revised overs from DLS)
    df['innings_overs_limit'] = 20.0
    
    # Check DLS revisions
    mask_inn1_rev = (df['innings'] == 1) & (df['first_inn_revised_overs'].notna())
    df.loc[mask_inn1_rev, 'innings_overs_limit'] = df.loc[mask_inn1_rev, 'first_inn_revised_overs']
    
    mask_inn2_rev = (df['innings'] == 2) & (df['second_inn_revised_overs'].notna())
    df.loc[mask_inn2_rev, 'innings_overs_limit'] = df.loc[mask_inn2_rev, 'second_inn_revised_overs']
    
    df['innings_total_legal_balls'] = (df['innings_overs_limit'] * 6).astype(int)
    
    # 2. Cumulative state prior to each ball within the innings
    grouped = df.groupby(['match_id', 'innings'], sort=False)
    
    # Pre-ball cumulative legal balls
    df['legal_balls_bowled'] = grouped['is_legal_ball'].cumsum() - df['is_legal_ball'].astype(int)
    df['balls_remaining'] = np.maximum(0, df['innings_total_legal_balls'] - df['legal_balls_bowled'])
    
    # Pre-ball cumulative runs
    df['current_score'] = grouped['delivery_runs'].cumsum() - df['delivery_runs']
    
    # Pre-ball cumulative wickets
    df['current_wickets'] = grouped['is_wicket'].cumsum() - df['is_wicket'].astype(int)
    df['wickets_in_hand'] = np.maximum(0, 10 - df['current_wickets'])
    
    # Current Run Rate (CRR)
    overs_bowled_fraction = df['legal_balls_bowled'] / 6.0
    df['current_run_rate'] = np.where(
        overs_bowled_fraction > 0,
        df['current_score'] / overs_bowled_fraction,
        0.0
    )
    
    # 3. Target and Required Run Rate (RRR) for Innings 2
    # Compute Innings 1 total runs per match
    inn1_totals = df[df['innings'] == 1].groupby('match_id')['delivery_runs'].sum().rename('inn1_total_runs')
    df = df.merge(inn1_totals, on='match_id', how='left')
    
    # Target derivation: revised_target if available, else inn1_total_runs + 1
    df['target'] = np.nan
    mask_inn2 = df['innings'] == 2
    
    # If revised target exists in match metadata
    has_rev_target = mask_inn2 & df['revised_target'].notna() & (df['revised_target'] > 0)
    df.loc[has_rev_target, 'target'] = df.loc[has_rev_target, 'revised_target']
    
    # Otherwise standard target is inn1_total_runs + 1
    has_std_target = mask_inn2 & ~has_rev_target & df['inn1_total_runs'].notna()
    df.loc[has_std_target, 'target'] = df.loc[has_std_target, 'inn1_total_runs'] + 1
    
    # Runs needed in chase
    df['runs_needed'] = np.nan
    df.loc[mask_inn2, 'runs_needed'] = np.maximum(0, df.loc[mask_inn2, 'target'] - df.loc[mask_inn2, 'current_score'])
    
    # Required Run Rate
    df['required_run_rate'] = np.nan
    rem_overs_inn2 = df.loc[mask_inn2, 'balls_remaining'] / 6.0
    df.loc[mask_inn2, 'required_run_rate'] = np.where(
        df.loc[mask_inn2, 'balls_remaining'] > 0,
        df.loc[mask_inn2, 'runs_needed'] / rem_overs_inn2,
        df.loc[mask_inn2, 'runs_needed'] * 6.0
    )
    
    # 4. Match Phase definition
    # Powerplay: overs 0-5 (legal balls 0-35)
    # Middle: overs 6-14 (legal balls 36-89)
    # Death: overs 15-19 (legal balls 90-119)
    # Use overid (0-indexed: 0..19)
    conditions = [
        df['overid'] < 6,
        (df['overid'] >= 6) & (df['overid'] < 15),
        df['overid'] >= 15
    ]
    choices = ['Powerplay', 'Middle', 'Death']
    df['phase'] = np.select(conditions, choices, default='Middle')
    
    # 5. Delivery outcome post-ball values (useful for win probability transitions)
    df['post_score'] = df['current_score'] + df['delivery_runs']
    df['post_wickets'] = df['current_wickets'] + df['is_wicket'].astype(int)
    df['post_legal_balls_bowled'] = df['legal_balls_bowled'] + df['is_legal_ball'].astype(int)
    df['post_balls_remaining'] = np.maximum(0, df['innings_total_legal_balls'] - df['post_legal_balls_bowled'])
    df['post_runs_needed'] = np.nan
    df.loc[mask_inn2, 'post_runs_needed'] = np.maximum(0, df.loc[mask_inn2, 'target'] - df.loc[mask_inn2, 'post_score'])
    
    return df
