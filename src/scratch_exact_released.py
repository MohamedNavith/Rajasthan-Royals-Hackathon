import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np

df = pd.read_parquet('outputs/enriched_ball_by_ball.parquet')

# Player exact name lookup in df
unique_batters = df['striker_name'].unique()
unique_bowlers = df['bowler_name'].unique()

def search_name(query, name_list):
    q_parts = query.lower().split()
    matches = []
    for n in name_list:
        n_low = n.lower()
        if all(part in n_low for part in q_parts):
            matches.append(n)
    return matches

target_released = [
    # Batters / All-Rounders
    "Shahrukh Khan", "Nehal Wadhera", "Karun Nair", "Nitish Rana", "Abishek Porel", 
    "Mahipal Lomror", "Rahul Tripathi", "Ajinkya Rahane", "Travis Head", "Kamindu Mendis",
    "Jacob Bethell", "Ben Duckett", "Pathum Nissanka", "Matt Short", "Matthew Breetzke",
    "Rachin Ravindra", "Shimron Hetmyer", "Zak Foulkes", "George Linde", "Aman Khan",
    # Bowlers
    "Matheesha Pathirana", "Trent Boult", "Akash Deep", "Deepak Chahar", "Avesh Khan",
    "Mustafizur Rahman", "Gerald Coetzee", "Lockie Ferguson", "Anrich Nortje", "Wanindu Hasaranga",
    "Spencer Johnson", "Matt Henry", "Adam Milne", "Tushar Deshpande", "Ishant Sharma",
    "Mayank Markande", "Akash Madhwal", "Umran Malik", "Rehan Ahmed", "Jaydev Unadkat", "Shivam Mavi"
]

results = []
for p in target_released:
    b_matches = search_name(p, unique_batters)
    bw_matches = search_name(p, unique_bowlers)
    
    b_name = b_matches[0] if b_matches else None
    bw_name = bw_matches[0] if bw_matches else None
    
    row = {'player': p}
    
    # Batting stats
    if b_name:
        b_df = df[df['striker_name'] == b_name]
        tot_b = len(b_df)
        pb_df = b_df[b_df['is_high_pressure'] == 1]
        pb = len(pb_df)
        psr = (pb_df['runs'].sum() / pb * 100) if pb > 0 else 0
        proe = pb_df['runs_over_expected_batter'].sum() if pb > 0 else 0
        
        jb_df = b_df[b_df['venue_id'] == 6]
        jb = len(jb_df)
        jsr = (jb_df['runs'].sum() / jb * 100) if jb > 0 else 0
        
        row.update({
            'tot_b': tot_b, 'press_b': pb, 'press_sr': round(psr, 1), 
            'press_roe': round(proe, 1), 'jaipur_b': jb, 'jaipur_sr': round(jsr, 1)
        })
    else:
        row.update({'tot_b': 0, 'press_b': 0, 'press_sr': 0, 'press_roe': 0, 'jaipur_b': 0, 'jaipur_sr': 0})
        
    # Bowling stats
    if bw_name:
        bw_df = df[df['bowler_name'] == bw_name]
        tot_bw = bw_df['is_legal_ball'].sum()
        pbw_df = bw_df[bw_df['is_high_pressure'] == 1]
        pbw = pbw_df['is_legal_ball'].sum()
        pruns = pbw_df['bowler_runs_conceded'].sum()
        pecon = (pruns / (pbw / 6.0)) if pbw > 0 else 0
        psaved = pbw_df['runs_saved_bowler'].sum() if pbw > 0 else 0
        pwkts = pbw_df['is_bowler_wicket'].sum()
        
        jbw_df = bw_df[bw_df['venue_id'] == 6]
        jbw = jbw_df['is_legal_ball'].sum()
        jruns = jbw_df['bowler_runs_conceded'].sum()
        jecon = (jruns / (jbw / 6.0)) if jbw > 0 else 0
        jwkts = jbw_df['is_bowler_wicket'].sum()
        
        row.update({
            'tot_bw': tot_bw, 'press_bw': pbw, 'press_econ': round(pecon, 2),
            'press_saved': round(psaved, 1), 'press_wkts': pwkts,
            'jaipur_bw': jbw, 'jaipur_econ': round(jecon, 2), 'jaipur_wkts': jwkts
        })
    else:
        row.update({
            'tot_bw': 0, 'press_bw': 0, 'press_econ': 0, 'press_saved': 0, 'press_wkts': 0,
            'jaipur_bw': 0, 'jaipur_econ': 0, 'jaipur_wkts': 0
        })
        
    results.append(row)

res_df = pd.DataFrame(results)
print("=== EXACT STATS FOR RELEASED AUCTION TARGETS ===")
print(res_df.to_string(index=False))
