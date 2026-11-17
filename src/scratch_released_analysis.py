import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np

# Load enriched data
df = pd.read_parquet('outputs/enriched_ball_by_ball.parquet')

# Released players from all teams based on comparing Full Squads vs Official Retention Images
RELEASED_BY_TEAMS = {
    "CSK": ["Matt Short", "Spencer Johnson", "Matt Henry", "Zak Foulkes", "Dian Forrester", "Akash Madhwal", "Aman Khan", "Macneil Noronha", "Prashant Veer", "Kuldip Yadav"],
    "DC": ["Mitchell Starc", "Ben Duckett", "Pathum Nissanka", "Rehan Ahmed", "Dushmantha Chameera", "Nitish Rana", "Karun Nair", "Abishek Porel", "Sahil Parakh", "Ajay Mandal"],
    "GT": ["Shahrukh Khan", "Ishant Sharma", "Luke Wood", "Connor Esterhuizen", "Kulwant Khejroliya", "Yarra Prithviraj"],
    "KKR": ["Rachin Ravindra", "Matheesha Pathirana", "Mustafizur Rahman", "Blessing Muzarabani", "Ajinkya Rahane", "Rahul Tripathi", "Akash Deep", "Umran Malik", "Navdeep Saini", "Daksh Kamra", "Tejasvi Dahiya", "Luvnith Sisodia"],
    "LSG": ["Wanindu Hasaranga", "Anrich Nortje", "Matthew Breetzke", "George Linde", "Avesh Khan", "Himmat Singh", "Naman Tiwari"],
    "MI": ["Trent Boult", "Keshav Maharaj", "AM Ghazanfar", "Deepak Chahar", "Mahipal Lomror", "Robin Minz", "Mayank Markande", "Atharva Ankolekar", "Krish Bhagat", "Danish Malewar", "Mayank Rawat", "Ruchit Ahir", "Mohammed Izhar"],
    "PBKS": ["Lockie Ferguson", "Nehal Wadhera", "Pravin Dubey", "Avinash Pyla", "Vishal Nishad"],
    "RR": ["Shimron Hetmyer", "Adam Milne", "Kwena Maphaka", "Tushar Deshpande", "Kuldeep Sen", "Yudhvir Singh Charak", "Vignesh Puthur", "Ravi Singh", "Emanjot Singh Chahal"],
    "RCB": ["Jacob Bethell", "Richard Gleeson", "Swapnil Singh", "Vihaan Malhotra", "Satvik Deswal", "Mangesh Yadav"],
    "SRH": ["Travis Head", "Gerald Coetzee", "Kamindu Mendis", "Dilshan Madushanka", "David Payne", "Jaydev Unadkat", "Shivam Mavi", "RS Ambrish", "Amit Kumar", "Onkar Tarmale"]
}

# Collect all released players
all_released = []
for team, players in RELEASED_BY_TEAMS.items():
    for p in players:
        all_released.append({'player': p, 'released_by': team})

rel_df = pd.DataFrame(all_released)
print(f"Total Released Players: {len(rel_df)}")

# Check their stats in the dataset
stats = []
for idx, r in rel_df.iterrows():
    p = r['player']
    last_name = p.split()[-1]
    
    # Batting
    b = df[df['striker_name'].str.contains(last_name, case=False, na=False)]
    pb = len(b[b['is_high_pressure'] == 1])
    psr = (b[b['is_high_pressure'] == 1]['runs'].sum() / pb * 100) if pb > 0 else 0
    proe = b[b['is_high_pressure'] == 1]['runs_over_expected_batter'].sum() if pb > 0 else 0
    jb = len(b[b['venue_id'] == 6])
    jsr = (b[b['venue_id'] == 6]['runs'].sum() / jb * 100) if jb > 0 else 0
    
    # Bowling
    bw = df[df['bowler_name'].str.contains(last_name, case=False, na=False)]
    pbw = bw[bw['is_high_pressure'] == 1]['is_legal_ball'].sum()
    pecon = (bw[bw['is_high_pressure'] == 1]['bowler_runs_conceded'].sum() / (pbw / 6.0)) if pbw > 0 else 0
    psaved = bw[bw['is_high_pressure'] == 1]['runs_saved_bowler'].sum() if pbw > 0 else 0
    pwkts = bw[bw['is_high_pressure'] == 1]['is_bowler_wicket'].sum()
    
    stats.append({
        'player': p,
        'released_by': r['released_by'],
        'press_balls_bat': pb,
        'press_sr': round(psr, 1),
        'press_roe': round(proe, 1),
        'jaipur_balls_bat': jb,
        'jaipur_sr': round(jsr, 1),
        'press_balls_bowl': pbw,
        'press_econ': round(pecon, 2),
        'press_saved': round(psaved, 1),
        'press_wkts': pwkts
    })

stat_df = pd.DataFrame(stats)
print("\n--- TOP RELEASED BATTERS BY PRESSURE ROE ---")
print(stat_df[stat_df['press_balls_bat'] >= 25].sort_values('press_roe', ascending=False).head(20).to_string(index=False))

print("\n--- TOP RELEASED BOWLERS BY RUNS SAVED ---")
print(stat_df[stat_df['press_balls_bowl'] >= 25].sort_values('press_saved', ascending=False).head(20).to_string(index=False))
