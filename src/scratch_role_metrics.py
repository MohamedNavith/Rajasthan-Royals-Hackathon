import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
df = pd.read_parquet('outputs/enriched_ball_by_ball.parquet')

# Helper function to get detailed stats for batter
def batter_metrics(name):
    b = df[df['striker_name'].str.contains(name, case=False, na=False)]
    if len(b) == 0:
        return None
    tot_b = len(b)
    press_b = b[b['is_high_pressure'] == 1]
    pb = len(press_b)
    psr = (press_b['runs'].sum() / pb * 100) if pb > 0 else 0
    proe = press_b['runs_over_expected_batter'].sum() if pb > 0 else 0
    
    # Recent seasons (2024-2026)
    rec = b[b['season'].isin(['2024', '2025', '2026'])]
    rec_b = len(rec)
    rec_press = rec[rec['is_high_pressure'] == 1]
    r_pb = len(rec_press)
    r_psr = (rec_press['runs'].sum() / r_pb * 100) if r_pb > 0 else 0
    r_roe = rec_press['runs_over_expected_batter'].sum() if r_pb > 0 else 0
    
    # Jaipur (venue 6)
    jb = b[b['venue_id'] == 6]
    jballs = len(jb)
    jsr = (jb['runs'].sum() / jballs * 100) if jballs > 0 else 0
    
    # Death
    db = b[b['phase'] == 'Death']
    dballs = len(db)
    dsr = (db['runs'].sum() / dballs * 100) if dballs > 0 else 0
    
    return {
        'name': name,
        'tot_b': tot_b,
        'press_b': pb,
        'press_sr': round(psr, 1),
        'press_roe': round(proe, 1),
        'rec_press_b': r_pb,
        'rec_press_sr': round(r_psr, 1),
        'rec_press_roe': round(r_roe, 1),
        'death_b': dballs,
        'death_sr': round(dsr, 1),
        'jaipur_b': jballs,
        'jaipur_sr': round(jsr, 1)
    }

# Helper function to get detailed stats for bowler
def bowler_metrics(name):
    bw = df[df['bowler_name'].str.contains(name, case=False, na=False)]
    if len(bw) == 0:
        return None
    tot_bw = bw['is_legal_ball'].sum()
    press_bw = bw[bw['is_high_pressure'] == 1]
    pbw = press_bw['is_legal_ball'].sum()
    pruns = press_bw['bowler_runs_conceded'].sum()
    pecon = (pruns / (pbw / 6.0)) if pbw > 0 else 0
    psaved = press_bw['runs_saved_bowler'].sum() if pbw > 0 else 0
    pwkts = press_bw['is_bowler_wicket'].sum()
    
    # Recent (2024-2026)
    rec = bw[bw['season'].isin(['2024', '2025', '2026'])]
    r_pbw = rec[rec['is_high_pressure'] == 1]['is_legal_ball'].sum()
    r_pruns = rec[rec['is_high_pressure'] == 1]['bowler_runs_conceded'].sum()
    r_pecon = (r_pruns / (r_pbw / 6.0)) if r_pbw > 0 else 0
    r_psaved = rec[rec['is_high_pressure'] == 1]['runs_saved_bowler'].sum() if r_pbw > 0 else 0
    r_pwkts = rec[rec['is_high_pressure'] == 1]['is_bowler_wicket'].sum()
    
    # Jaipur
    jbw = bw[bw['venue_id'] == 6]
    jballs = jbw['is_legal_ball'].sum()
    jruns = jbw['bowler_runs_conceded'].sum()
    jecon = (jruns / (jballs / 6.0)) if jballs > 0 else 0
    jwkts = jbw['is_bowler_wicket'].sum()
    
    return {
        'name': name,
        'tot_bw': tot_bw,
        'press_bw': pbw,
        'press_econ': round(pecon, 2),
        'press_saved': round(psaved, 1),
        'press_wkts': pwkts,
        'rec_press_bw': r_pbw,
        'rec_press_econ': round(r_pecon, 2),
        'rec_press_saved': round(r_psaved, 1),
        'rec_press_wkts': r_pwkts,
        'jaipur_bw': jballs,
        'jaipur_econ': round(jecon, 2),
        'jaipur_wkts': jwkts
    }

print("Loaded helper functions.")

# 1. OVERSEAS FINISHERS (#6/#7)
ov_finishers = [
    "Ferreira", "Zak Foulkes", "Matthew Breetzke", "Ben Duckett", "Jacob Bethell", 
    "Matt Short", "George Linde", "Pretorius", "Shanaka", "Luke Wood"
]
print("\n--- 1. OVERSEAS FINISHERS ---")
f_res = [batter_metrics(p) for p in ov_finishers if batter_metrics(p)]
print(pd.DataFrame(f_res).to_string(index=False))

# 2. OVERSEAS MIDDLE-ORDER SPIN DESTROYERS (#4/#5)
ov_middle = [
    "Kamindu Mendis", "Rachin Ravindra", "Pathum Nissanka", "Ben Duckett", "Jacob Bethell",
    "Matt Short", "Matthew Breetzke", "Pretorius", "George Linde", "Zak Foulkes"
]
print("\n--- 2. OVERSEAS MIDDLE-ORDER DESTROYERS ---")
m_res = [batter_metrics(p) for p in ov_middle if batter_metrics(p)]
print(pd.DataFrame(m_res).to_string(index=False))

# 3. OVERSEAS MYSTERY / STRIKE SPIN CHOKE
ov_spinners = [
    "Wanindu Hasaranga", "Sufiyan Muqeem", "Ehsan Khan", "Rehan Ahmed", "Keshav Maharaj",
    "AM Ghazanfar", "George Linde", "Kamindu Mendis", "Matt Short", "Rachin Ravindra"
]
print("\n--- 3. OVERSEAS SPIN CHOKE ---")
s_res = [bowler_metrics(p) for p in ov_spinners if bowler_metrics(p)]
print(pd.DataFrame(s_res).to_string(index=False))

# 4. OVERSEAS EXPRESS SEAMERS & DEATH ENFORCERS
ov_seamers = [
    "Pathirana", "Trent Boult", "Gerald Coetzee", "Lockie Ferguson", "Mustafizur Rahman",
    "Anrich Nortje", "Spencer Johnson", "Matt Henry", "Adam Milne", "Luke Wood"
]
print("\n--- 4. OVERSEAS EXPRESS SEAMERS ---")
p_res = [bowler_metrics(p) for p in ov_seamers if bowler_metrics(p)]
print(pd.DataFrame(p_res).to_string(index=False))
