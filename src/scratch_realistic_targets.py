import pandas as pd
import numpy as np

# Load datasets
df = pd.read_parquet('outputs/enriched_ball_by_ball.parquet')
matches = pd.read_csv('Data Pack/matches.csv')
comps = pd.read_csv('Data Pack/competitions.csv')
player_map = pd.read_csv('Data Pack/competition_team_player_mapping.csv')
teams = pd.read_csv('Data Pack/teams.csv')

print("Loaded datasets.")

# Let's inspect potential finishers in the dataset
# Criteria: batted in phase Death or Middle, strike rate, pressure stats, and Jaipur performance
jaipur_balls = df[df['venue_id'] == 6]

# Batters with high pressure balls or death balls
finishers = []
for p, g in df.groupby('striker_name'):
    tot_b = len(g)
    if tot_b < 50:
        continue
    press_g = g[g['is_high_pressure'] == 1]
    pb = len(press_g)
    if pb < 25:
        continue
    
    death_g = g[g['phase'] == 'Death']
    db = len(death_g)
    
    # Jaipur specific
    j_g = g[g['venue_id'] == 6]
    jb = len(j_g)
    j_sr = (j_g['runs'].sum() / jb * 100) if jb > 0 else 0
    
    psr = (press_g['runs'].sum() / pb * 100)
    proe = press_g['runs_over_expected_batter'].sum()
    pwpa = press_g['wpa_batting_team'].sum()
    
    finishers.append({
        'player': p,
        'tot_balls': tot_b,
        'press_balls': pb,
        'press_sr': round(psr, 1),
        'press_roe': round(proe, 1),
        'press_wpa': round(pwpa, 2),
        'death_balls': db,
        'jaipur_balls': jb,
        'jaipur_sr': round(j_sr, 1)
    })

fin_df = pd.DataFrame(finishers)
print("Top 30 Pressure Batters by Pressure ROE:")
print(fin_df.sort_values('press_roe', ascending=False).head(30).to_string(index=False))
