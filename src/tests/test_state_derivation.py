"""
Unit tests for cumulative match state derivation:
- Running score and running wickets.
- Legal balls remaining calculation.
- Target and RRR calculation in 2nd innings.
"""
import pandas as pd
import numpy as np
import pytest
from src.state_derivation import derive_match_states

def test_cumulative_state_derivation():
    # Construct a minimal 2-innings match
    # Innings 1: 3 balls (1 run, 4 runs, wicket)
    # Innings 2: 3 balls (wide, 6 runs, 1 run)
    rows = [
        # Innings 1
        {'match_id': 1, 'innings': 1, 'overid': 0, 'innings_ball_num': 1, 'over_ball_num': 1,
         'is_legal_ball': True, 'delivery_runs': 1, 'is_wicket': False,
         'first_inn_revised_overs': np.nan, 'second_inn_revised_overs': np.nan, 'revised_target': np.nan},
        {'match_id': 1, 'innings': 1, 'overid': 0, 'innings_ball_num': 2, 'over_ball_num': 2,
         'is_legal_ball': True, 'delivery_runs': 4, 'is_wicket': False,
         'first_inn_revised_overs': np.nan, 'second_inn_revised_overs': np.nan, 'revised_target': np.nan},
        {'match_id': 1, 'innings': 1, 'overid': 0, 'innings_ball_num': 3, 'over_ball_num': 3,
         'is_legal_ball': True, 'delivery_runs': 0, 'is_wicket': True,
         'first_inn_revised_overs': np.nan, 'second_inn_revised_overs': np.nan, 'revised_target': np.nan},
        # Innings 2 (chasing target of 5 + 1 = 6)
        {'match_id': 1, 'innings': 2, 'overid': 0, 'innings_ball_num': 1, 'over_ball_num': 1,
         'is_legal_ball': False, 'delivery_runs': 1, 'is_wicket': False,
         'first_inn_revised_overs': np.nan, 'second_inn_revised_overs': np.nan, 'revised_target': np.nan},
        {'match_id': 1, 'innings': 2, 'overid': 0, 'innings_ball_num': 2, 'over_ball_num': 1,
         'is_legal_ball': True, 'delivery_runs': 4, 'is_wicket': False,
         'first_inn_revised_overs': np.nan, 'second_inn_revised_overs': np.nan, 'revised_target': np.nan},
        {'match_id': 1, 'innings': 2, 'overid': 0, 'innings_ball_num': 3, 'over_ball_num': 2,
         'is_legal_ball': True, 'delivery_runs': 1, 'is_wicket': False,
         'first_inn_revised_overs': np.nan, 'second_inn_revised_overs': np.nan, 'revised_target': np.nan},
    ]
    df = pd.DataFrame(rows)
    res = derive_match_states(df)
    
    # Check Innings 1 states
    # Ball 1: score before is 0, wickets 0, balls bowled 0
    assert res.loc[0, 'current_score'] == 0
    assert res.loc[0, 'current_wickets'] == 0
    assert res.loc[0, 'legal_balls_bowled'] == 0
    assert res.loc[0, 'balls_remaining'] == 120
    
    # Ball 2: score before is 1
    assert res.loc[1, 'current_score'] == 1
    assert res.loc[1, 'legal_balls_bowled'] == 1
    
    # Ball 3: score before is 5, wickets before is 0
    assert res.loc[2, 'current_score'] == 5
    assert res.loc[2, 'current_wickets'] == 0
    assert res.loc[2, 'legal_balls_bowled'] == 2
    
    # Check Innings 2 states
    # Target should be 5 + 1 = 6
    assert res.loc[3, 'target'] == 6
    assert res.loc[3, 'runs_needed'] == 6
    assert res.loc[3, 'legal_balls_bowled'] == 0
    
    # Ball 4 is a wide: adds 1 run, but 0 legal balls bowled!
    assert res.loc[4, 'current_score'] == 1
    assert res.loc[4, 'legal_balls_bowled'] == 0
    assert res.loc[4, 'runs_needed'] == 5
    
    # Ball 5: 1 legal ball bowled, 5 runs scored so far (1 wide + 4)
    assert res.loc[5, 'current_score'] == 5
    assert res.loc[5, 'legal_balls_bowled'] == 1
    assert res.loc[5, 'runs_needed'] == 1
