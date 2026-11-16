"""
Export Top-10 Batters and Bowlers CSVs with full metrics and confidence intervals.
Outputs:
- outputs/top10_batters.csv
- outputs/top10_bowlers.csv
"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
from src.config import OUTPUT_DIR
from src.reliability import compute_bootstrap_cis

def export_top10():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(OUTPUT_DIR / "enriched_ball_by_ball.parquet")
    
    print("Computing final Top 10 Batters with Bootstrap CIs...")
    batters = compute_bootstrap_cis(df, role='batter', n_bootstrap=500, min_balls=60)
    top10_batters = batters.head(10).copy()
    top10_batters['rank'] = range(1, 11)
    
    b_export_cols = [
        'rank', 'player_name', 'pressure_rating', 'ci_lower', 'ci_upper',
        'press_balls', 'total_balls', 'press_sr', 'norm_sr', 'sr_delta',
        'press_roe', 'press_wpa', 'consistency_pct'
    ]
    top10_batters_clean = top10_batters[b_export_cols].round({
        'pressure_rating': 2, 'ci_lower': 2, 'ci_upper': 2,
        'press_sr': 1, 'norm_sr': 1, 'sr_delta': 1,
        'press_roe': 1, 'press_wpa': 2, 'consistency_pct': 1
    })
    top10_batters_clean.to_csv(OUTPUT_DIR / "top10_batters.csv", index=False)
    print("Saved outputs/top10_batters.csv")
    
    print("\nComputing final Top 10 Bowlers with Bootstrap CIs...")
    bowlers = compute_bootstrap_cis(df, role='bowler', n_bootstrap=500, min_balls=60)
    top10_bowlers = bowlers.head(10).copy()
    top10_bowlers['rank'] = range(1, 11)
    
    bw_export_cols = [
        'rank', 'player_name', 'pressure_rating', 'ci_lower', 'ci_upper',
        'press_balls', 'total_balls', 'press_economy', 'norm_economy', 'economy_delta',
        'press_wickets', 'press_runs_saved', 'press_wpa', 'consistency_pct'
    ]
    top10_bowlers_clean = top10_bowlers[bw_export_cols].round({
        'pressure_rating': 2, 'ci_lower': 2, 'ci_upper': 2,
        'press_economy': 2, 'norm_economy': 2, 'economy_delta': 2,
        'press_runs_saved': 1, 'press_wpa': 2, 'consistency_pct': 1
    })
    top10_bowlers_clean.to_csv(OUTPUT_DIR / "top10_bowlers.csv", index=False)
    print("Saved outputs/top10_bowlers.csv")

if __name__ == '__main__':
    export_top10()
