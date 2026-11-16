"""
Global configuration, paths, constants, and hyperparameters for Rajasthan Royals SupeRR Selector.
"""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data Pack"
OUTPUT_DIR = BASE_DIR / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"

# Random Seed for complete reproducibility
RANDOM_SEED = 42

# Eligibility Thresholds
MIN_PRESSURE_BALLS_BATTER = 50   # Minimum high-pressure deliveries faced
MIN_PRESSURE_BALLS_BOWLER = 50   # Minimum high-pressure deliveries bowled
MIN_TOTAL_BALLS_BATTER = 150     # Overall sample threshold
MIN_TOTAL_BALLS_BOWLER = 150     # Overall sample threshold

# High-Pressure Thresholds
LEVERAGE_QUANTILE_THRESHOLD = 0.75  # Top 25% leverage balls defined as high pressure

# Empirical Bayes Shrinkage Prior Parameters
EB_BATTER_PRIOR_WEIGHT = 30.0  # Equivalent pseudo-balls of league mean prior
EB_BOWLER_PRIOR_WEIGHT = 30.0  # Equivalent pseudo-balls of league mean prior

# Color Palette (Rajasthan Royals official branding)
RR_PINK = "#E01B6B"
RR_BLUE = "#0B1B3D"
RR_ROYAL_BLUE = "#1B3B6F"
RR_GOLD = "#FFB81C"
RR_LIGHT_BG = "#F8F9FA"
RR_TEXT_DARK = "#1A1A2E"
RR_SUCCESS = "#00875A"
RR_DANGER = "#DE350B"
