"""
Data loading and raw data trap reconciliation module.
Handles:
1. Loading all CSVs from Data Pack.
2. Reconciling the 10,881 vs 10,892 wicket mismatch.
3. Classifying bowler vs non-bowler wickets.
4. Parsing legal deliveries and extras (wides, oversteps, byes, legbyes).
5. Tagging super overs, washed out / no-result matches, and DLS revisions.
6. Enriching with competition type (IPL vs T20I).
"""
import pandas as pd
import numpy as np
from pathlib import Path
from src.config import DATA_DIR

def load_raw_data(data_dir: Path = DATA_DIR):
    """Load all raw CSVs from the specified data directory."""
    bbb = pd.read_csv(data_dir / "ball_by_ball.csv", low_memory=False)
    matches = pd.read_csv(data_dir / "matches.csv")
    comps = pd.read_csv(data_dir / "competitions.csv")
    teams = pd.read_csv(data_dir / "teams.csv")
    playing_eleven = pd.read_csv(data_dir / "playing_eleven.csv")
    mapping = pd.read_csv(data_dir / "competition_team_player_mapping.csv")
    
    return bbb, matches, comps, teams, playing_eleven, mapping

def reconcile_wickets(bbb: pd.DataFrame) -> pd.DataFrame:
    """
    Trap 5 Reconciliation:
    - 12 rows have is_wicket=False, dismissal_type=NaN, but a non-null dismissed_player_id
      accompanying standard run scoring shots (0, 1, 4, 6).
    - 1 row (match 40709, inn 2) has is_wicket=True, dismissal_type='Retire Out', but NaN dismissed_player_id.
    - Fix typos like 'Obstracting the field' -> 'Obstructing the field'.
    - Separate bowler-credited wickets from non-bowler dismissals.
    """
    df = bbb.copy()
    
    # Standardize typo
    df['dismissal_type'] = df['dismissal_type'].replace({
        'Obstracting the field': 'Obstructing the field'
    })
    
    # 1. Fix the 12 false dismissed_player_id entries
    false_dismissal_mask = (~df['is_wicket']) & (df['dismissal_type'].isna()) & (df['dismissed_player_id'].notna())
    df.loc[false_dismissal_mask, 'dismissed_player_id'] = np.nan
    
    # 2. Fix the 1 Retire Out row where dismissed_player_id is NaN
    retire_out_mask = (df['is_wicket']) & (df['dismissal_type'] == 'Retire Out') & (df['dismissed_player_id'].isna())
    df.loc[retire_out_mask, 'dismissed_player_id'] = df.loc[retire_out_mask, 'striker_id']
    
    # Ensure is_wicket boolean consistency with dismissal_type
    df['is_wicket'] = df['is_wicket'].fillna(False).astype(bool)
    
    # Bowler credited wickets (Caught, Bowled, LBW, Stump, Hit Wicket)
    bowler_wicket_types = {'Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket'}
    df['is_bowler_wicket'] = df['is_wicket'] & df['dismissal_type'].isin(bowler_wicket_types)
    
    # Non-bowler dismissals (RunOut, Retire Out, Obstructing the field)
    df['is_non_bowler_dismissal'] = df['is_wicket'] & (~df['is_bowler_wicket'])
    
    return df

def process_extras_and_legal_deliveries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trap 2 Reconciliation:
    - extras_type values: 'wide', 'Overstep', 'legbyes', 'byes', 'other', 'Penalty'
    - Legal delivery: False if wide or Overstep (or Penalty), True otherwise.
    - Total runs on delivery: runs + extras1_runs + extras_2_runs.
    - Batter runs: credited with 'runs' unless extras_type == 'wide'.
    - Bowler runs: runs + extras1_runs if wide or Overstep;
                   runs if legbyes, byes, other (fielding extras are not charged to bowler).
    """
    df = df.copy()
    
    df['runs'] = df['runs'].fillna(0).astype(int)
    df['extras1_runs'] = df['extras1_runs'].fillna(0).astype(int)
    df['extras_2_runs'] = df['extras_2_runs'].fillna(0).astype(int)
    
    # Total runs scored on the delivery
    df['delivery_runs'] = df['runs'] + df['extras1_runs'] + df['extras_2_runs']
    
    # Legal ball definition: wides, oversteps (no-balls) and penalty are illegal balls
    illegal_extras = {'wide', 'Overstep', 'Penalty'}
    df['is_legal_ball'] = ~df['extras_type'].isin(illegal_extras)
    
    # Batter runs: batters do not get runs on wides; on overstep, 'runs' is off the bat
    df['batter_runs'] = np.where(df['extras_type'] == 'wide', 0, df['runs'])
    
    # Bowler runs conceded:
    # Charged: all bat runs, plus bowling extras (wides, oversteps).
    # Not charged: byes, legbyes, penalty.
    df['bowler_runs_conceded'] = df['runs'] + np.where(
        df['extras_type'].isin(['wide', 'Overstep']), df['extras1_runs'], 0
    )
    
    return df

def clean_and_merge_data(data_dir: Path = DATA_DIR):
    """
    Full pipeline to load, clean, reconcile traps, and merge ball-by-ball with match metadata.
    """
    bbb, matches, comps, teams, playing_eleven, mapping = load_raw_data(data_dir)
    
    # Step 1: Trap 5 Wicket reconciliation
    df = reconcile_wickets(bbb)
    
    # Step 2: Trap 2 Extras & legal deliveries
    df = process_extras_and_legal_deliveries(df)
    
    # Step 3: Trap 3 Tag super overs
    df['is_super_over'] = df['innings'] >= 3
    
    # Step 4: Merge competitions
    matches_comp = matches.merge(comps[['comp_id', 'comp_name', 'match_format', 'season']], on='comp_id', how='left')
    
    # Add competition classification (IPL vs T20I)
    matches_comp['is_ipl'] = matches_comp['comp_name'].str.contains('IPL', case=False, na=False)
    matches_comp['comp_tier'] = np.where(
        matches_comp['is_ipl'], 'IPL',
        np.where(matches_comp['match_format'] == 'T20I', 'T20I', 'Other_T20')
    )
    
    # Merge match metadata into ball-by-ball
    match_cols = [
        'match_id', 'comp_id', 'comp_name', 'match_format', 'season', 'comp_tier', 'is_ipl',
        'match_date', 'stage', 'venue_id', 'venue_country',
        'home_team_id', 'away_team_id', 'toss_win_team_id', 'toss_opted',
        'first_inn_revised_overs', 'second_inn_revised_overs', 'revised_target',
        'knock_out', 'win_team_id', 'result'
    ]
    
    merged = df.merge(matches_comp[match_cols], on='match_id', how='left')
    
    # Trap 4: Washed out / Abandoned flag
    merged['is_abandoned_or_no_result'] = (
        merged['win_team_id'].isna() | 
        merged['result'].astype(str).str.contains('No Result|Match Abandoned|Tie', case=False, na=False)
    )
    
    return merged, matches_comp, comps, teams, playing_eleven, mapping
