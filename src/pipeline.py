"""
End-to-End Pipeline Runner for SupeRR Selector.
Orchestrates:
1. Data cleaning & trap reconciliation
2. Match state derivation
3. Win probability modeling & leverage index
4. Contextual outcome baselines
5. Player pressure ratings & empirical Bayes shrinkage
"""
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np

from src.config import OUTPUT_DIR, RANDOM_SEED
from src.data_loader import clean_and_merge_data
from src.state_derivation import derive_match_states
from src.win_prob_model import WinProbabilityModel
from src.baseline_models import ContextualBaselineModels
from src.ratings import compute_batter_ratings, compute_bowler_ratings

def run_pipeline(force_recompute: bool = False):
    start_time = time.time()
    print("=" * 70, flush=True)
    print("Rajasthan Royals SupeRR Selector: Running Pipeline (Milestones 1-4)", flush=True)
    print("=" * 70, flush=True)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = OUTPUT_DIR / "enriched_ball_by_ball.parquet"
    
    if cache_path.exists() and not force_recompute:
        print(f"Loading cached enriched ball-by-ball dataset from {cache_path}...", flush=True)
        df_enriched = pd.read_parquet(cache_path)
    else:
        # Milestone 1: Data Ingestion & State Derivation
        print("\n[Milestone 1] Ingesting data and reconciling known traps...", flush=True)
        merged, matches_comp, comps, teams, playing_eleven, mapping = clean_and_merge_data()
        print(f"Loaded {len(merged):,} deliveries across {merged['match_id'].nunique()} matches.", flush=True)
        
        print("Deriving cumulative running states, balls remaining, target, RRR...", flush=True)
        df_state = derive_match_states(merged)
        print("State derivation complete.", flush=True)
        
        # Milestone 2: Win Probability & Leverage Index
        print("\n[Milestone 2] Training calibrated Win Probability models and calculating Leverage Index...", flush=True)
        wp_model = WinProbabilityModel()
        wp_model.fit(df_state)
        
        print("Computing ball-by-ball leverage index and alternative pressure metrics...", flush=True)
        df_with_pressure = wp_model.compute_ball_leverage(df_state)
        
        num_press_balls = df_with_pressure['is_high_pressure_wpli'].sum()
        print(f"High pressure deliveries identified: {num_press_balls:,} ({num_press_balls/len(df_with_pressure):.1%})", flush=True)
        
        # Milestone 3: Contextual Baselines
        print("\n[Milestone 3] Training contextual expected outcome models...", flush=True)
        baseline_models = ContextualBaselineModels()
        baseline_models.fit(df_with_pressure)
        
        print("Calculating context-adjusted expected runs and dismissal/wicket probabilities...", flush=True)
        df_enriched = baseline_models.transform(df_with_pressure)
        
        # Save enriched dataset to fast parquet for dashboard & downstream analysis
        print(f"Caching enriched ball-by-ball data to {cache_path}...", flush=True)
        df_enriched.to_parquet(cache_path, index=False)
    
    # Milestone 4: Player Pressure Ratings
    print("\n[Milestone 4] Computing player pressure ratings and Empirical Bayes shrinkage...")
    batter_ratings = compute_batter_ratings(df_enriched)
    bowler_ratings = compute_bowler_ratings(df_enriched)
    
    print(f"Eligible batters rated: {len(batter_ratings)}")
    print(f"Eligible bowlers rated: {len(bowler_ratings)}")
    
    # Save full rating tables
    batter_ratings.to_csv(OUTPUT_DIR / "all_batters_rated.csv", index=False)
    bowler_ratings.to_csv(OUTPUT_DIR / "all_bowlers_rated.csv", index=False)
    
    elapsed = time.time() - start_time
    print(f"\nPipeline Milestones 1-4 completed in {elapsed:.1f}s.")
    
    return df_enriched, batter_ratings, bowler_ratings

if __name__ == '__main__':
    run_pipeline()
