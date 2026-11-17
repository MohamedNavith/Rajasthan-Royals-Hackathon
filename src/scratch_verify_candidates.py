import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
df = pd.read_parquet('outputs/enriched_ball_by_ball.parquet')

# Let's inspect potential released candidates and uncontracted auction players
print("Checking specific released and uncontracted players...")
candidates = [
    # Overseas Finishers
    "Matheesha Pathirana", "Trent Boult", "Deepak Chahar", "Wanindu Hasaranga", "Mustafizur Rahman",
    "Gerald Coetzee", "Lockie Ferguson", "Anrich Nortje", "Spencer Johnson", "Matt Henry", "Adam Milne",
    "Ishant Sharma", "Akash Deep", "Avesh Khan", "Rehan Ahmed", "Matt Short", "Zak Foulkes", "George Linde",
    "Shahrukh Khan", "Nehal Wadhera", "Karun Nair", "Nitish Rana", "Abishek Porel", "Mahipal Lomror",
    "Rahul Tripathi", "Ajinkya Rahane", "Travis Head", "Kamindu Mendis", "Jacob Bethell", "Ben Duckett",
    "Pathum Nissanka", "Matthew Breetzke", "Rachin Ravindra", "Shimron Hetmyer",
    # Global uncontracted
    "Riley Meredith", "Sufiyan Muqeem", "Ehsan Khan", "Jake Fraser-McGurk", "Corbin Bosch"
]

print("Done checking.")
