"""
Unit tests for delivery extras and legal ball accounting.
Tests:
- Wides: 0 bat runs, bowler conceded runs, legal_ball is False.
- Overstep (no-ball): bat runs from 'runs', 1 extra in extras1_runs, legal_ball is False.
- Byes & Leg-byes: 0 bat runs, 0 bowler runs conceded, legal_ball is True.
- Total delivery runs: runs + extras1_runs + extras_2_runs.
"""
import pandas as pd
import numpy as np
import pytest
from src.data_loader import process_extras_and_legal_deliveries

def test_wides():
    raw = pd.DataFrame([{
        'runs': 0, 'extras1_runs': 1, 'extras_2_runs': 0, 'extras_type': 'wide'
    }])
    res = process_extras_and_legal_deliveries(raw).iloc[0]
    assert res['delivery_runs'] == 1
    assert res['is_legal_ball'] == False
    assert res['batter_runs'] == 0
    assert res['bowler_runs_conceded'] == 1

def test_overstep_with_bat_runs():
    raw = pd.DataFrame([{
        'runs': 4, 'extras1_runs': 1, 'extras_2_runs': 0, 'extras_type': 'Overstep'
    }])
    res = process_extras_and_legal_deliveries(raw).iloc[0]
    assert res['delivery_runs'] == 5
    assert res['is_legal_ball'] == False
    assert res['batter_runs'] == 4
    assert res['bowler_runs_conceded'] == 5

def test_legbyes_and_byes():
    raw = pd.DataFrame([
        {'runs': 0, 'extras1_runs': 1, 'extras_2_runs': 0, 'extras_type': 'legbyes'},
        {'runs': 0, 'extras1_runs': 4, 'extras_2_runs': 0, 'extras_type': 'byes'}
    ])
    res = process_extras_and_legal_deliveries(raw)
    
    # Leg-bye: legal ball, 0 batter runs, 0 bowler runs
    assert res.loc[0, 'delivery_runs'] == 1
    assert res.loc[0, 'is_legal_ball'] == True
    assert res.loc[0, 'batter_runs'] == 0
    assert res.loc[0, 'bowler_runs_conceded'] == 0
    
    # Bye 4: legal ball, 0 batter runs, 0 bowler runs
    assert res.loc[1, 'delivery_runs'] == 4
    assert res.loc[1, 'is_legal_ball'] == True
    assert res.loc[1, 'batter_runs'] == 0
    assert res.loc[1, 'bowler_runs_conceded'] == 0

def test_standard_boundary():
    raw = pd.DataFrame([{
        'runs': 6, 'extras1_runs': 0, 'extras_2_runs': 0, 'extras_type': np.nan
    }])
    res = process_extras_and_legal_deliveries(raw).iloc[0]
    assert res['delivery_runs'] == 6
    assert res['is_legal_ball'] == True
    assert res['batter_runs'] == 6
    assert res['bowler_runs_conceded'] == 6
