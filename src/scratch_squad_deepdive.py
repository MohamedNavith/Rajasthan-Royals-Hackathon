import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from src.squad_analysis import SQUADS_2026

df = pd.read_parquet('outputs/enriched_ball_by_ball.parquet')

print("--- OVERSEAS FINISHERS IN 2026 SQUADS & DATASET ---")
# Check all overseas batters/all-rounders across squads
for team, sq in SQUADS_2026.items():
    print(f"\n{team}:")
    for role in ['batters', 'all_rounders', 'wicket_keepers']:
        for p in sq.get(role, []):
            # check stats in df
            pdf = df[df['striker_name'].str.contains(p.split()[-1], case=False, na=False)]
            if len(pdf) > 30:
                press_b = pdf[pdf['is_high_pressure'] == 1]
                death_b = pdf[pdf['phase'] == 'Death']
                p_sr = (press_b['runs'].sum() / len(press_b) * 100) if len(press_b) > 0 else 0
                roe = press_b['runs_over_expected_batter'].sum()
                j_b = pdf[pdf['venue_id'] == 6]
                j_sr = (j_b['runs'].sum() / len(j_b) * 100) if len(j_b) > 0 else 0
                if len(press_b) >= 20 or len(death_b) >= 30:
                    print(f"  [{role[:3].upper()}] {p:<22} | Tot: {len(pdf):>4}b | Press: {len(press_b):>3}b (SR: {p_sr:>5.1f}, ROE: {roe:>+5.1f}) | Death: {len(death_b):>3}b | Jaipur: {len(j_b):>2}b (SR: {j_sr:>5.1f})")
