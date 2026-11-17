import pandas as pd
import numpy as np

# Load data
df = pd.read_parquet('outputs/enriched_ball_by_ball.parquet')
matches = pd.read_csv('Data Pack/matches.csv')
comps = pd.read_csv('Data Pack/competitions.csv')
m = matches.merge(comps, on='comp_id', how='left')

rr_matches = m[((m['home_team_id'] == 3) | (m['away_team_id'] == 3)) & (m['season'].isin(['2025', '2026']))].copy()
rr_matches = rr_matches.sort_values(['season', 'match_date'])

rr_m_ids = set(rr_matches['match_id'])
df_rr = df[df['match_id'].isin(rr_m_ids)].copy()

# Focus on RR batting
rr_bat = df_rr[df_rr['batting_team_id'] == 3].copy()
print("\n=======================================================")
print("--- RR BATTERS (2025-2026) IN PRESSURE vs NORMAL ---")
print("=======================================================")
bat_summary = []
for p, g in rr_bat.groupby('striker_name'):
    tot_balls = len(g)
    if tot_balls < 20:
        continue
    press_g = g[g['is_high_pressure'] == 1]
    norm_g = g[g['is_high_pressure'] == 0]
    
    p_balls = len(press_g)
    p_runs = press_g['runs'].sum()
    p_sr = (p_runs / p_balls * 100) if p_balls > 0 else 0
    p_roe = press_g['runs_over_expected_batter'].sum() if p_balls > 0 else 0
    p_wpa = press_g['wpa_batting_team'].sum() if p_balls > 0 else 0
    p_outs = press_g['is_wicket'].sum()
    
    n_balls = len(norm_g)
    n_runs = norm_g['runs'].sum()
    n_sr = (n_runs / n_balls * 100) if n_balls > 0 else 0
    
    bat_summary.append({
        'Player': p,
        'Tot Balls': tot_balls,
        'Press Balls': p_balls,
        'Norm SR': round(n_sr, 1),
        'Press SR': round(p_sr, 1),
        'SR Delta': round(p_sr - n_sr, 1),
        'Press ROE': round(p_roe, 1),
        'Press Outs': p_outs,
        'Press WPA': round(p_wpa, 2)
    })

bat_df = pd.DataFrame(bat_summary).sort_values('Press Balls', ascending=False)
print(bat_df.to_string(index=False))

# Focus on RR bowling
rr_bowl = df_rr[df_rr['bowling_team_id'] == 3].copy()
print("\n=======================================================")
print("--- RR BOWLERS (2025-2026) IN PRESSURE vs NORMAL ---")
print("=======================================================")
bowl_summary = []
for p, g in rr_bowl.groupby('bowler_name'):
    tot_balls = g['is_legal_ball'].sum()
    if tot_balls < 20:
        continue
    press_g = g[g['is_high_pressure'] == 1]
    norm_g = g[g['is_high_pressure'] == 0]
    
    p_balls = press_g['is_legal_ball'].sum()
    p_runs = press_g['bowler_runs_conceded'].sum()
    p_econ = (p_runs / (p_balls / 6.0)) if p_balls > 0 else 0
    p_wkts = press_g['is_bowler_wicket'].sum()
    p_saved = press_g['runs_saved_bowler'].sum() if p_balls > 0 else 0
    p_wpa = press_g['wpa_bowling_team'].sum() if p_balls > 0 else 0
    
    n_balls = norm_g['is_legal_ball'].sum()
    n_runs = norm_g['bowler_runs_conceded'].sum()
    n_econ = (n_runs / (n_balls / 6.0)) if n_balls > 0 else 0
    
    bowl_summary.append({
        'Bowler': p,
        'Tot Balls': tot_balls,
        'Press Balls': p_balls,
        'Norm Econ': round(n_econ, 2),
        'Press Econ': round(p_econ, 2),
        'Econ Delta': round(n_econ - p_econ, 2),
        'Press Wkts': p_wkts,
        'Press Saved': round(p_saved, 1),
        'Press WPA': round(p_wpa, 2)
    })

bowl_df = pd.DataFrame(bowl_summary).sort_values('Press Balls', ascending=False)
print(bowl_df.to_string(index=False))

# Look specifically at Sandeep Sharma across all IPL (2022-2026)
print("\n=======================================================")
print("--- SANDEEP SHARMA CAREER AUDIT (2022-2026) ---")
print("=======================================================")
sandeep_balls = df[df['bowler_name'].str.contains('Sandeep Sharma', case=False, na=False)].copy()
print(f"Total legal balls bowled by Sandeep Sharma: {sandeep_balls['is_legal_ball'].sum()}")
print(f"By match phase:")
for phase, pg in sandeep_balls.groupby('phase'):
    balls = pg['is_legal_ball'].sum()
    runs = pg['bowler_runs_conceded'].sum()
    econ = runs / (balls / 6.0) if balls > 0 else 0
    wkts = pg['is_bowler_wicket'].sum()
    press_b = pg[pg['is_high_pressure'] == 1]['is_legal_ball'].sum()
    print(f"  Phase {phase:<12}: {balls:>4} balls | Econ: {econ:.2f} | Wkts: {wkts} | Press Balls: {press_b}")

# Look at Shimron Hetmyer career audit (2022-2026)
print("\n=======================================================")
print("--- SHIMRON HETMYER CAREER AUDIT (2022-2026) ---")
print("=======================================================")
het_balls = df[df['striker_name'].str.contains('Hetmyer', case=False, na=False)].copy()
print(f"Total balls faced by Hetmyer: {len(het_balls)}")
for season, sg in het_balls.groupby('season'):
    tot_b = len(sg)
    p_g = sg[sg['is_high_pressure'] == 1]
    pb = len(p_g)
    pruns = p_g['runs'].sum()
    psr = (pruns / pb * 100) if pb > 0 else 0
    proe = p_g['runs_over_expected_batter'].sum() if pb > 0 else 0
    pwpa = p_g['wpa_batting_team'].sum() if pb > 0 else 0
    print(f"  Season {season}: {tot_b:>3} balls | Press: {pb:>2}b | Press SR: {psr:>5.1f} | ROE: {proe:>+5.1f} | WPA: {pwpa:>+4.2f}")

# Look at Yashasvi Jaiswal career audit (2022-2026)
print("\n=======================================================")
print("--- YASHASVI JAISWAL CAREER AUDIT (2022-2026) ---")
print("=======================================================")
jais_balls = df[df['striker_name'].str.contains('Jaiswal', case=False, na=False)].copy()
print(f"Total balls faced by Jaiswal: {len(jais_balls)}")
for season, sg in jais_balls.groupby('season'):
    tot_b = len(sg)
    p_g = sg[sg['is_high_pressure'] == 1]
    pb = len(p_g)
    pruns = p_g['runs'].sum()
    psr = (pruns / pb * 100) if pb > 0 else 0
    proe = p_g['runs_over_expected_batter'].sum() if pb > 0 else 0
    pwpa = p_g['wpa_batting_team'].sum() if pb > 0 else 0
    print(f"  Season {season}: {tot_b:>3} balls | Press: {pb:>2}b | Press SR: {psr:>5.1f} | ROE: {proe:>+5.1f} | WPA: {pwpa:>+4.2f}")

# Look at Ravi Bishnoi career audit (2022-2026)
print("\n=======================================================")
print("--- RAVI BISHNOI CAREER AUDIT (2022-2026) ---")
print("=======================================================")
bish_balls = df[df['bowler_name'].str.contains('Bishnoi', case=False, na=False)].copy()
print(f"Total legal balls bowled by Bishnoi: {bish_balls['is_legal_ball'].sum()}")
for season, sg in bish_balls.groupby('season'):
    tot_b = sg['is_legal_ball'].sum()
    p_g = sg[sg['is_high_pressure'] == 1]
    pb = p_g['is_legal_ball'].sum()
    pruns = p_g['bowler_runs_conceded'].sum()
    pecon = (pruns / (pb / 6.0)) if pb > 0 else 0
    pwkts = p_g['is_bowler_wicket'].sum()
    psaved = p_g['runs_saved_bowler'].sum() if pb > 0 else 0
    pwpa = p_g['wpa_bowling_team'].sum() if pb > 0 else 0
    print(f"  Season {season}: {tot_b:>3} balls | Press: {pb:>2}b | Press Econ: {pecon:>5.2f} | Wkts: {pwkts} | Saved: {psaved:>+5.1f} | WPA: {pwpa:>+4.2f}")

# Analyze all RR losses in 2025 and 2026
print("\n=======================================================")
print("--- RR LOSSES DEEP-DIVE (2025 & 2026) ---")
print("=======================================================")
rr_losses = m[((m['home_team_id'] == 3) | (m['away_team_id'] == 3)) & (m['win_team_id'] != 3) & (m['season'].isin(['2025', '2026']))].copy()
for idx, r in rr_losses.sort_values(['season', 'match_date']).iterrows():
    opp = r['away_team'] if r['home_team_id'] == 3 else r['home_team']
    m_id = r['match_id']
    m_balls = df[df['match_id'] == m_id]
    
    # Check batting first vs chasing
    inn1_bat = m_balls[m_balls['innings'] == 1]['batting_team_id'].iloc[0]
    rr_batted_first = (inn1_bat == 3)
    
    # Check score
    inn1_runs = m_balls[m_balls['innings'] == 1]['delivery_runs'].sum()
    inn2_runs = m_balls[m_balls['innings'] == 2]['delivery_runs'].sum()
    
    # Check pressure balls in the match
    press_b = m_balls[m_balls['is_high_pressure'] == 1]
    rr_press_bat = press_b[press_b['batting_team_id'] == 3]
    rr_press_bowl = press_b[press_b['bowling_team_id'] == 3]
    
    bat_sr = (rr_press_bat['runs'].sum() / len(rr_press_bat) * 100) if len(rr_press_bat) > 0 else 0
    bowl_econ = (rr_press_bowl['bowler_runs_conceded'].sum() / (rr_press_bowl['is_legal_ball'].sum() / 6.0)) if rr_press_bowl['is_legal_ball'].sum() > 0 else 0
    
    print(f"Season {r['season']} | M#{r['match_number']:>2} vs {opp:<28} | RR {'Batted 1st' if rr_batted_first else 'Chased   '} | {r['result']}")
    print(f"    Inn1: {inn1_runs} | Inn2: {inn2_runs} | RR Press Bat SR: {bat_sr:>5.1f} | RR Press Bowl Econ: {bowl_econ:>5.2f}")
