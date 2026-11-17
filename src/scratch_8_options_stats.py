import pandas as pd
import numpy as np

df = pd.read_parquet('outputs/enriched_ball_by_ball.parquet')
v6 = df[df['venue_id'] == 6]

def get_batter_stats(name):
    b = df[df['striker_name'].str.contains(name, case=False, na=False)]
    if len(b) == 0:
        return None
    tot_balls = len(b)
    press_b = b[b['is_high_pressure'] == 1]
    pb = len(press_b)
    psr = (press_b['runs'].sum() / pb * 100) if pb > 0 else 0
    proe = press_g_roe = press_b['runs_over_expected_batter'].sum() if pb > 0 else 0
    pwpa = press_b['wpa_batting_team'].sum() if pb > 0 else 0
    
    # Jaipur
    jb = b[b['venue_id'] == 6]
    jballs = len(jb)
    jsr = (jb['runs'].sum() / jballs * 100) if jballs > 0 else 0
    
    # Death phase
    db = b[b['phase'] == 'Death']
    dballs = len(db)
    dsr = (db['runs'].sum() / dballs * 100) if dballs > 0 else 0
    
    return {
        'name': name,
        'tot_balls': tot_balls,
        'press_balls': pb,
        'press_sr': round(psr, 1),
        'press_roe': round(proe, 1),
        'press_wpa': round(pwpa, 2),
        'death_balls': dballs,
        'death_sr': round(dsr, 1),
        'jaipur_balls': jballs,
        'jaipur_sr': round(jsr, 1)
    }

def get_bowler_stats(name):
    bw = df[df['bowler_name'].str.contains(name, case=False, na=False)]
    if len(bw) == 0:
        return None
    tot_balls = bw['is_legal_ball'].sum()
    press_bw = bw[bw['is_high_pressure'] == 1]
    pb = press_bw['is_legal_ball'].sum()
    pruns = press_bw['bowler_runs_conceded'].sum()
    pecon = (pruns / (pb / 6.0)) if pb > 0 else 0
    pwkts = press_bw['is_bowler_wicket'].sum()
    psaved = press_bw['runs_saved_bowler'].sum() if pb > 0 else 0
    pwpa = press_bw['wpa_bowling_team'].sum() if pb > 0 else 0
    
    # Jaipur
    jbw = bw[bw['venue_id'] == 6]
    jballs = jbw['is_legal_ball'].sum()
    jruns = jbw['bowler_runs_conceded'].sum()
    jecon = (jruns / (jballs / 6.0)) if jballs > 0 else 0
    jwkts = jbw['is_bowler_wicket'].sum()
    
    return {
        'name': name,
        'tot_balls': tot_balls,
        'press_balls': pb,
        'press_econ': round(pecon, 2),
        'press_wkts': pwkts,
        'press_saved': round(psaved, 1),
        'press_wpa': round(pwpa, 2),
        'jaipur_balls': jballs,
        'jaipur_econ': round(jecon, 2),
        'jaipur_wkts': jwkts
    }

# 1. Overseas Finishers Candidates
print("=== 1. OVERSEAS FINISHERS ===")
ov_finishers = ['Ferreira', 'Phillips', 'Shepherd', 'Rutherford', 'Pretorius', 'Connolly', 'Corbin Bosch', 'Shanaka', 'Breetzke', 'Stoinis', 'Overton', 'Zak Foulkes']
res1 = [get_batter_stats(p) for p in ov_finishers if get_batter_stats(p)]
print(pd.DataFrame(res1).to_string(index=False))

# 2. Indian Middle Order Candidates
print("\n=== 2. INDIAN MIDDLE ORDER ===")
ind_middle = ['Rizvi', 'Shubham Dubey', 'Wadhera', 'Shashank Singh', 'Naman Dhir', 'Ashutosh Sharma', 'Karun Nair', 'Lomror', 'Shahrukh Khan', 'Abdul Samad', 'Badoni', 'Ramandeep Singh', 'Musheer Khan']
res2 = [get_batter_stats(p) for p in ind_middle if get_batter_stats(p)]
print(pd.DataFrame(res2).to_string(index=False))

# 3. Spin Choke Candidates
print("\n=== 3. SPIN CHOKE ===")
spinners = ['Siddharth', 'Sufiyan Muqeem', 'Sai Kishore', 'Shreyas Gopal', 'Ehsan Khan', 'Suyash Sharma', 'Rahul Chahar', 'Markande', 'Akeal Hosein', 'Noor Ahmad', 'Sundar', 'Kartikeya', 'Shahbaz Ahmed']
res3 = [get_bowler_stats(p) for p in spinners if get_bowler_stats(p)]
print(pd.DataFrame(res3).to_string(index=False))

# 4. Wicketkeepers Candidates
print("\n=== 4. WICKETKEEPERS ===")
keepers = ['Ferreira', 'Urvil Patel', 'Porel', 'Rickelton', 'Pretorius', 'Kushagra', 'Robin Minz', 'Anuj Rawat', 'Vishnu Vinod', 'Seifert', 'Salil Arora']
res4 = [get_batter_stats(p) for p in keepers if get_batter_stats(p)]
print(pd.DataFrame(res4).to_string(index=False))
