"""
Unit tests for wicket reconciliation and bowler credit separation.
Tests:
- Reconciling 12 false dismissed_player_id entries where is_wicket=False.
- Reconciling 1 Retire Out entry where dismissed_player_id is NaN.
- Distinguishing bowler wickets (Caught, Bowled, LBW, Stump, Hit Wicket) from
  non-bowler dismissals (RunOut, Retire Out, Obstructing the field).
"""
import pandas as pd
import numpy as np
import pytest
from src.data_loader import reconcile_wickets

def test_false_dismissal_reconciliation():
    raw = pd.DataFrame([{
        'is_wicket': False,
        'dismissal_type': np.nan,
        'dismissed_player_id': 1440.0,
        'striker_id': 1440.0
    }])
    res = reconcile_wickets(raw).iloc[0]
    assert np.isnan(res['dismissed_player_id'])
    assert res['is_wicket'] == False
    assert res['is_bowler_wicket'] == False
    assert res['is_non_bowler_dismissal'] == False

def test_retire_out_reconciliation():
    raw = pd.DataFrame([{
        'is_wicket': True,
        'dismissal_type': 'Retire Out',
        'dismissed_player_id': np.nan,
        'striker_id': 9999.0
    }])
    res = reconcile_wickets(raw).iloc[0]
    assert res['dismissed_player_id'] == 9999.0
    assert res['is_wicket'] == True
    assert res['is_bowler_wicket'] == False
    assert res['is_non_bowler_dismissal'] == True

def test_bowler_vs_fielding_wickets():
    raw = pd.DataFrame([
        {'is_wicket': True, 'dismissal_type': 'Caught', 'dismissed_player_id': 101.0, 'striker_id': 101.0},
        {'is_wicket': True, 'dismissal_type': 'Bowled', 'dismissed_player_id': 102.0, 'striker_id': 102.0},
        {'is_wicket': True, 'dismissal_type': 'LBW', 'dismissed_player_id': 103.0, 'striker_id': 103.0},
        {'is_wicket': True, 'dismissal_type': 'RunOut', 'dismissed_player_id': 104.0, 'striker_id': 104.0},
        {'is_wicket': True, 'dismissal_type': 'Obstracting the field', 'dismissed_player_id': 105.0, 'striker_id': 105.0}
    ])
    res = reconcile_wickets(raw)
    
    # Bowler wickets
    assert res.loc[0, 'is_bowler_wicket'] == True
    assert res.loc[1, 'is_bowler_wicket'] == True
    assert res.loc[2, 'is_bowler_wicket'] == True
    
    # Non-bowler dismissals
    assert res.loc[3, 'is_bowler_wicket'] == False
    assert res.loc[3, 'is_non_bowler_dismissal'] == True
    
    assert res.loc[4, 'dismissal_type'] == 'Obstructing the field'
    assert res.loc[4, 'is_bowler_wicket'] == False
    assert res.loc[4, 'is_non_bowler_dismissal'] == True
