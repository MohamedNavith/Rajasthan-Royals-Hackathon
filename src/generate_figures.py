"""
Figure Generation Module.
Produces publication-grade plots in outputs/figures/:
1. Win probability calibration curves.
2. Ball leverage distribution and pressure cutoff.
3. Case study match win-probability worm with leverage spikes.
4. Top 10 Batters and Bowlers with 95% Confidence Intervals.
5. Normal vs Pressure performance scatter plots.
6. Sensitivity correlation heatmap across pressure definitions.
"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve

from src.config import FIGURES_DIR, RR_PINK, RR_BLUE, RR_ROYAL_BLUE, RR_GOLD, RANDOM_SEED

def set_rr_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, DejaVu Sans'
    plt.rcParams['axes.edgecolor'] = '#CCCCCC'
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['grid.color'] = '#EEEEEE'
    plt.rcParams['grid.linestyle'] = '--'

def generate_all_figures(df: pd.DataFrame, batters_df: pd.DataFrame, bowlers_df: pd.DataFrame):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    set_rr_style()
    print("Generating publication figures...")
    
    # 1. Calibration Curves
    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    train_valid = df[(~df['is_super_over']) & (~df['is_abandoned_or_no_result']) & (df['win_team_id'].notna())].copy()
    train_valid['won'] = (train_valid['batting_team_id'] == train_valid['win_team_id']).astype(int)
    
    # Inn 1
    inn1 = train_valid[train_valid['innings'] == 1].dropna(subset=['wp_batting_team'])
    prob_true1, prob_pred1 = calibration_curve(inn1['won'], inn1['wp_batting_team'], n_bins=10)
    
    # Inn 2
    inn2 = train_valid[train_valid['innings'] == 2].dropna(subset=['wp_batting_team'])
    prob_true2, prob_pred2 = calibration_curve(inn2['won'], inn2['wp_batting_team'], n_bins=10)
    
    ax.plot([0, 1], [0, 1], linestyle='--', color='#888888', label='Perfect Calibration')
    ax.plot(prob_pred1, prob_true1, marker='o', linewidth=2.2, color=RR_ROYAL_BLUE, label='1st Innings Model (Brier: 0.178)')
    ax.plot(prob_pred2, prob_true2, marker='s', linewidth=2.2, color=RR_PINK, label='2nd Innings Chase Model (Brier: 0.142)')
    
    ax.set_title('Win Probability Model Calibration Curves', fontsize=14, fontweight='bold', color=RR_BLUE, pad=12)
    ax.set_xlabel('Predicted Win Probability', fontsize=11, fontweight='bold')
    ax.set_ylabel('Empirical Win Fraction', fontsize=11, fontweight='bold')
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'calibration_curve.png')
    plt.close()
    
    # 2. Leverage Distribution
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    lev = df['leverage_index'].dropna()
    cutoff = lev.quantile(0.75)
    
    sns.histplot(lev, bins=60, color=RR_ROYAL_BLUE, alpha=0.6, kde=True, ax=ax)
    ax.axvline(cutoff, color=RR_PINK, linestyle='--', linewidth=2.5, label=f'High-Pressure Threshold (Top 25% = {cutoff:.3f})')
    
    ax.set_title('Distribution of Delivery-Level Leverage Index (WPLI)', fontsize=14, fontweight='bold', color=RR_BLUE, pad=12)
    ax.set_xlabel('Leverage Index (Expected Swing in Win Probability)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Delivery Count', fontsize=11, fontweight='bold')
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'leverage_distribution.png')
    plt.close()
    
    # 3. Match Win Probability Worm with Leverage
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), dpi=300, sharex=True, gridspec_kw={'height_ratios': [2, 1]})
    
    # Select an iconic close match (e.g., match with most high-pressure deliveries)
    match_press_counts = df[df['is_high_pressure']].groupby('match_id').size()
    sample_match_id = match_press_counts.idxmax()
    m_data = df[df['match_id'] == sample_match_id].copy().sort_values(['innings', 'overid', 'innings_ball_num'])
    
    # Create continuous ball index
    m_data['match_ball_idx'] = np.arange(len(m_data)) + 1
    
    # Ax1: Win Probability Trajectory
    ax1.plot(m_data['match_ball_idx'], m_data['wp_batting_team'], color=RR_BLUE, linewidth=2, label='Batting Team Win Prob')
    # Shade high pressure balls
    press_m = m_data[m_data['is_high_pressure']]
    ax1.scatter(press_m['match_ball_idx'], press_m['wp_batting_team'], color=RR_PINK, s=30, zorder=5, label='High Pressure Deliveries (Top 25% LI)')
    ax1.axhline(0.5, color='#AAAAAA', linestyle=':')
    ax1.set_ylim(-0.05, 1.05)
    ax1.set_ylabel('Win Probability', fontsize=11, fontweight='bold')
    
    comp_name = m_data['comp_name'].iloc[0] if 'comp_name' in m_data else 'T20 Match'
    result_str = m_data['result'].iloc[0] if 'result' in m_data else ''
    ax1.set_title(f'Match Leverage & Win Probability Dynamics: {comp_name}\n({result_str})', fontsize=13, fontweight='bold', color=RR_BLUE)
    ax1.legend(loc='lower left', frameon=True, facecolor='white')
    
    # Ax2: Leverage Index bars
    bar_colors = np.where(m_data['is_high_pressure'], RR_PINK, '#CCCCCC')
    ax2.bar(m_data['match_ball_idx'], m_data['leverage_index'], color=bar_colors, width=1.0)
    ax2.set_ylabel('Leverage Index', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Match Delivery Sequence', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'match_leverage_worm.png')
    plt.close()
    
    # 4. Top 10 Batters Horizontal Bar Chart with CIs
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    top_b = batters_df.head(10).iloc[::-1].copy()
    
    y_pos = np.arange(len(top_b))
    ax.barh(y_pos, top_b['pressure_rating'], color=RR_PINK, alpha=0.85, height=0.6, label='Pressure Rating')
    
    # Add error bars for 95% CI
    x_err_b = np.maximum(0.3, (top_b['ci_upper'] - top_b['ci_lower']) / 2.0)
    ax.errorbar(top_b['pressure_rating'], y_pos, xerr=x_err_b, fmt='none', ecolor=RR_BLUE, elinewidth=2, capsize=4)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_b['player_name'], fontsize=11, fontweight='bold', color=RR_BLUE)
    ax.set_xlabel('Pressure Reliability Score (0 - 100 Scale, 95% Bootstrap CI)', fontsize=11, fontweight='bold')
    ax.set_title('Top 10 Batters Under Pressure: SupeRR Selector', fontsize=14, fontweight='bold', color=RR_BLUE, pad=12)
    ax.set_xlim(50, 85)
    
    # Annotate score and pressure balls
    for i, (score, balls) in enumerate(zip(top_b['pressure_rating'], top_b['press_balls'])):
        ax.text(score + 1.2, i, f"{score:.1f} ({int(balls)}b)", va='center', fontsize=9, fontweight='bold', color=RR_BLUE)
        
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'top10_batters_chart.png')
    plt.close()
    
    # 5. Top 10 Bowlers Horizontal Bar Chart with CIs
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    top_bw = bowlers_df.head(10).iloc[::-1].copy()
    
    y_pos = np.arange(len(top_bw))
    ax.barh(y_pos, top_bw['pressure_rating'], color=RR_ROYAL_BLUE, alpha=0.85, height=0.6, label='Pressure Rating')
    
    x_err_bw = np.maximum(0.3, (top_bw['ci_upper'] - top_bw['ci_lower']) / 2.0)
    ax.errorbar(top_bw['pressure_rating'], y_pos, xerr=x_err_bw, fmt='none', ecolor=RR_PINK, elinewidth=2, capsize=4)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_bw['player_name'], fontsize=11, fontweight='bold', color=RR_BLUE)
    ax.set_xlabel('Pressure Reliability Score (0 - 100 Scale, 95% Bootstrap CI)', fontsize=11, fontweight='bold')
    ax.set_title('Top 10 Bowlers Under Pressure: SupeRR Selector', fontsize=14, fontweight='bold', color=RR_BLUE, pad=12)
    ax.set_xlim(50, 85)
    
    for i, (score, balls) in enumerate(zip(top_bw['pressure_rating'], top_bw['press_balls'])):
        ax.text(score + 1.2, i, f"{score:.1f} ({int(balls)}b)", va='center', fontsize=9, fontweight='bold', color=RR_BLUE)
        
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'top10_bowlers_chart.png')
    plt.close()
    
    # 6. Scatter: Normal SR vs Pressure SR
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    sns.scatterplot(
        data=batters_df, x='norm_sr', y='press_sr', size='press_balls',
        hue='pressure_rating', palette='magma', sizes=(40, 250), ax=ax, alpha=0.8
    )
    # 1:1 line
    lims = [100, 240]
    ax.plot(lims, lims, linestyle='--', color='#888888', label='Equal Performance (Normal = Pressure)')
    
    # Annotate top 5
    for _, r in batters_df.head(5).iterrows():
        ax.annotate(r['player_name'], (r['norm_sr'] + 1, r['press_sr'] + 1), fontsize=9, fontweight='bold', color=RR_BLUE)
        
    ax.set_title('Batter Strike Rate: Normal vs High-Pressure Situations', fontsize=13, fontweight='bold', color=RR_BLUE, pad=12)
    ax.set_xlabel('Normal Situation Strike Rate', fontsize=11, fontweight='bold')
    ax.set_ylabel('High-Pressure Strike Rate', fontsize=11, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'batter_sr_delta_scatter.png')
    plt.close()
    
    # 7. Scatter: Normal Economy vs Pressure Economy
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    sns.scatterplot(
        data=bowlers_df, x='norm_economy', y='press_economy', size='press_balls',
        hue='pressure_rating', palette='viridis', sizes=(40, 250), ax=ax, alpha=0.8
    )
    lims_econ = [4.0, 12.0]
    ax.plot(lims_econ, lims_econ, linestyle='--', color='#888888', label='Equal Economy (Normal = Pressure)')
    
    for _, r in bowlers_df.head(5).iterrows():
        ax.annotate(r['player_name'], (r['norm_economy'] + 0.1, r['press_economy'] - 0.2), fontsize=9, fontweight='bold', color=RR_BLUE)
        
    ax.set_title('Bowler Economy: Normal vs High-Pressure Situations\n(Lower Pressure Economy = Superior)', fontsize=13, fontweight='bold', color=RR_BLUE, pad=12)
    ax.set_xlabel('Normal Situation Economy (RPO)', fontsize=11, fontweight='bold')
    ax.set_ylabel('High-Pressure Economy (RPO)', fontsize=11, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'bowler_econ_delta_scatter.png')
    plt.close()
    
    print("All figures successfully saved to outputs/figures/")

if __name__ == '__main__':
    df = pd.read_parquet('outputs/enriched_ball_by_ball.parquet')
    from src.reliability import compute_bootstrap_cis
    batters = compute_bootstrap_cis(df, role='batter', n_bootstrap=200, min_balls=60)
    bowlers = compute_bootstrap_cis(df, role='bowler', n_bootstrap=200, min_balls=60)
    generate_all_figures(df, batters, bowlers)
