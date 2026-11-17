# 👑 SupeRR Selector Season 2 – Round 1
### Identify the Most Reliable Players Under Pressure in T20 Cricket
**Rajasthan Royals Hackathon | Quantitative Sports Data Science & Analytics**

---

## 📌 Problem Overview
T20 cricket is defined by fluctuating match states where a single delivery can decide victory or defeat. The **SupeRR Selector Season 2 (Round 1)** challenge asks us to:
1. Define **"Pressure"** objectively from the historical ball-by-ball data (2022–2026, 867 matches, ~201k deliveries).
2. Measure how batters and bowlers perform in high-pressure situations versus their own usual level and contextual expectations.
3. Produce:
   - Ordered **Top-10 Batters Under Pressure**
   - Ordered **Top-10 Bowlers Under Pressure**
   - Comprehensive **Methodology Report** (`outputs/report.docx` and `outputs/report.pdf`)
   - Interactive **Streamlit Presentation Dashboard** (`app.py`)

---

## 🏆 Final Top-10 Rankings

### 🏏 Top 10 Batters Under Pressure

| Rank | Player Name | Pressure Rating | 95% Bootstrap CI | Pressure Balls | Total Balls | Pressure SR | Normal SR | SR Delta (Δ) | Runs Over Expected (ROE) | Win Prob Added (WPA) | Match Consistency |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **Tim David** | **76.74** | [76.87, 78.77] | 334 | 1,215 | 188.6 | 172.9 | **+15.8** | **+134.5** | **+2.53** | 73.0% |
| **2** | **Jake McGurk** | **73.88** | [73.37, 77.85] | 88 | 277 | 195.5 | 170.4 | **+25.1** | **+50.0** | +0.41 | 70.0% |
| **3** | **Vaibhav Sooryavanshi** | **73.40** | [72.40, 75.33] | 174 | 674 | 213.8 | 227.4 | -13.6 | **+111.7** | +0.61 | 66.7% |
| **4** | **Naman Dhir** | **73.01** | [72.80, 75.56] | 161 | 588 | 183.9 | 163.0 | **+20.9** | **+63.6** | +0.94 | 65.0% |
| **5** | **Josh Inglis** | **72.98** | [73.39, 75.51] | 243 | 903 | 183.5 | 154.4 | **+29.1** | **+98.8** | +0.65 | **81.5%** |
| **6** | **Karun Nair** | **70.76** | [70.55, 75.16] | 60 | 150 | 183.3 | 135.6 | **+47.8** | +22.7 | +0.23 | 75.0% |
| **7** | **Mohammad Nabi** | **69.23** | [69.59, 71.90] | 165 | 659 | 156.4 | 121.7 | **+34.7** | +43.2 | +0.95 | 71.4% |
| **8** | **Sameer Rizvi** | **68.96** | [68.49, 72.35] | 82 | 293 | 170.7 | 134.6 | **+36.1** | +19.2 | +0.47 | 66.7% |
| **9** | **Rashid Khan** | **68.27** | [67.54, 70.52] | 128 | 506 | 166.4 | 151.9 | **+14.6** | +24.5 | **+1.15** | 61.5% |
| **10** | **Najibullah Zadran** | **68.20** | [67.48, 70.91] | 80 | 304 | 157.5 | 130.4 | **+27.1** | +12.4 | +0.60 | **100.0%** |

### 🎯 Top 10 Bowlers Under Pressure

| Rank | Player Name | Pressure Rating | 95% Bootstrap CI | Pressure Balls | Total Balls | Pressure Econ (RPO) | Normal Econ (RPO) | Econ Delta (Δ) | Pressure Wickets | Runs Saved vs Context | Win Prob Added (WPA) | Match Consistency |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **Sunil Narine** | **77.46** | [78.07, 78.94] | 395 | 1,533 | **5.65** | 7.14 | **+1.49** | 29 | **+157.3** | **+4.81** | **100.0%** |
| **2** | **Sufiyan Muqeem** | **74.28** | [75.29, 76.45] | 130 | 518 | **3.74** | 6.65 | **+2.91** | 11 | **+62.3** | +1.91 | **100.0%** |
| **3** | **Riley Meredith** | **73.79** | [74.31, 76.55] | 72 | 310 | **6.08** | 9.28 | **+3.19** | 5 | +36.5 | +1.09 | **100.0%** |
| **4** | **Corbin Bosch** | **68.41** | [67.25, 69.94] | 88 | 368 | 8.45 | 8.27 | -0.18 | 11 | +4.6 | +1.43 | 87.5% |
| **5** | **Kuldeep Yadav** | **67.95** | [68.20, 69.07] | 478 | 1,914 | **7.04** | 8.11 | **+1.07** | **35** | **+101.0** | **+4.85** | 89.8% |
| **6** | **Ishant Sharma** | **67.23** | [67.14, 69.03] | 125 | 423 | **7.82** | 9.50 | **+1.68** | 8 | +23.4 | +1.72 | 89.5% |
| **7** | **Adam Milne** | **65.93** | [65.67, 67.89] | 100 | 545 | **7.50** | 9.26 | **+1.76** | 10 | +19.8 | +1.15 | 86.7% |
| **8** | **Ehsan Khan** | **65.74** | [65.76, 67.85] | 87 | 323 | **5.45** | 7.40 | **+1.95** | 6 | +32.7 | +1.16 | **100.0%** |
| **9** | **Mayank Yadav** | **65.63** | [65.27, 67.70] | 110 | 494 | **7.47** | 9.25 | **+1.78** | 10 | +13.4 | +1.17 | 83.3% |
| **10** | **Josh Hazlewood** | **64.54** | [64.28, 65.42] | 393 | 1,477 | **8.06** | 8.12 | +0.06 | **35** | **+51.4** | **+4.18** | 73.8% |

---

## 👑 Rajasthan Royals War Room: IPL 2027 Auction Strategy & Post-Trade Blueprint

Connecting empirical pressure analytics directly to Rajasthan Royals' tactical requirements following the **2026 IPL franchise rosters** and **verified blockbuster trade transactions**:

### 1. 2026 Blockbuster Trade Update & Fortified Bowling Arsenal
* **RR ⇄ LSG Blockbuster:** Rajasthan Royals traded all-rounder **Sam Curran** to Lucknow Super Giants in exchange for India premier fast bowler **Mohammad Shami** and left-arm orthodox spinner **Manimaran Siddharth**.
* **Bowling Arsenal Complete:** Shami and Siddharth join Jofra Archer, Sandeep Sharma, Adam Milne (#7 ranked pressure bowler), Ravi Bishnoi, Nandre Burger, and Ravindra Jadeja. **RR's bowling is now completely fortified across all phases**—zero need to spend high auction capital on overseas pacers.
* **Other Major Rival Trades:**
  * **DC ⇄ LSG:** Rishabh Pant traded to DC; Kuldeep Yadav traded to LSG.
  * **DC ⇄ SRH:** T Natarajan to SRH; Zeeshan Ansari to DC.
  * **SRH ⇄ CSK:** Liam Livingstone & Jack Edwards to CSK; Khaleel Ahmed & Nathan Ellis to SRH.
  * **MI ⇄ PBKS:** Hardik Pandya to PBKS; Arshdeep Singh to MI.
  * **SRH ➔ GT:** Harshal Patel transferred to GT.

### 2. Critical Remaining Voids in the RR Lineup
* **Death-Overs Power Finisher:** Shimron Hetmyer registered **-31.5 Runs Over Expected (ROE)** in high-pressure chases for RR. With Sam Curran traded away, RR experiences severe batting collapse risk in 10+ RRR chases.
* **Severe Wicketkeeping Vulnerability:** Sanju Samson is at CSK; **Dhruv Jurel is RR's sole specialist wicketkeeper**. Acquiring a dual-threat keeper-finisher is paramount.

### 3. Actionable Target Recommendations
* **⭐ Tier 1 Marquee Target (Batting): Tim David (Rank 1)** — Absolute top priority. 188.6 pressure SR, +134.5 ROE, +2.53 WPA, and 73.0% consistency. Directly solves RR's death chase deficit.
* **⭐ Tier 1 Marquee Target (Wicketkeeper): Josh Inglis (Rank 5)** — Dual-threat asset offering 183.5 pressure SR, +98.8 ROE, and an unmatched 81.5% consistency. Provides essential wicketkeeping depth behind Jurel and destroys middle-overs spin.
* **💎 Crown Jewel Retention: Vaibhav Sooryavanshi (Rank 3)** — RR's in-house prodigy delivered 213.8 pressure SR and +93.3 ROE specifically for RR. Strategic directive: Lock him in as primary opener alongside Yashasvi Jaiswal.
* **⚡ Tier 2 High-Value Specialists:** **Riley Meredith (Rank 3 Bowler)** (6.08 RPO, 100% consistency) and **Sufiyan Muqeem (Rank 2 Bowler)** (3.74 RPO).
* **💡 Tier 3 Domestic Steals:** **Naman Dhir (#4)**, **Sameer Rizvi (#8)**, and **Ashutosh Sharma (#11)** offer extreme purse efficiency.

### 4. Playing XI Evolution: 2026 Base vs 2027 Champion Lineup
* **2026 Post-Trade Probable XI:**
  1. Yashasvi Jaiswal (LH Opener, +53.8 ROE)
  2. Vaibhav Sooryavanshi (LH Opener, 213.8 SR - Rank #3)
  3. Riyan Parag (RH Anchor / Enforcer)
  4. Ravindra Jadeja (LH Spin All-Rounder)
  5. Dhruv Jurel (Wicketkeeper / Finisher, +9.3 ROE)
  6. Shimron Hetmyer (Overseas Finisher - Vulnerability: -31.5 ROE)
  7. Shubham Dubey / Donovan Ferreira (Impact Batter)
  8. Ravi Bishnoi (Right-Arm Wrist Spin)
  9. Mohammad Shami (**New Trade-In** - Pace Spearhead)
  10. Jofra Archer / Adam Milne (**Milne: Rank #7 Bowler**)
  11. Sandeep Sharma (Death Yorker & Knuckleballs)
  * *Impact Sub:* Manimaran Siddharth (**New Trade-In** - Left-Arm Orthodox Spin)

* **👑 Projected 2027 Champion Playing XI:**
  1. Yashasvi Jaiswal (LH Opener - Powerplay Dominance)
  2. Vaibhav Sooryavanshi (LH Opener - #3 Pressure Batter)
  3. Riyan Parag (RH Middle-Overs Aggressor)
  4. Ravindra Jadeja (LH Spin All-Rounder & Match Finisher)
  5. **Josh Inglis** (**Target #5** - Dual WK / 360° Spin Destroyer)
  6. **Tim David** (**Target #1** - 188.6 SR, +134.5 ROE, Elite Power Finisher)
  7. Dhruv Jurel (Clutch Pressure Finisher / Secondary WK)
  8. Ravi Bishnoi (Right-Arm Attacking Leg-Spin)
  9. Mohammad Shami (New Ball Swing & Reverse Yorker Spearhead)
  10. Jofra Archer / Adam Milne (Express 150 km/h Artillery)
  11. Sandeep Sharma (Death Over Deception Master)
  * *Impact Sub:* Manimaran Siddharth / Naman Dhir (**Target #4**)

---

## 🔬 Core Methodology

1. **Win Probability Leverage Index (WPLI)**:
   - Ball-by-ball win-probability model trained on 867 matches via calibrated LightGBM.
   - Leverage Index measures expected absolute win-probability swing across possible outcomes.
   - Deliveries in the top 25% quantile ($\text{cutoff} = 0.052$) are defined as **High Pressure** (50,250 deliveries).
2. **Contextual Baselines (xRuns, xDismissal, xWickets)**:
   - Evaluates performance against contextual expectations controlling for match phase, bowling discipline (pace/spin), venue scoring factor, competition tier, and batting order.
3. **Fair Comparison & Shrinkage**:
   - Empirical Bayes shrinkage ($K = 30$ balls prior) regresses small samples toward league mean.
   - Enforced eligibility threshold of $\ge 60$ pressure balls and $\ge 150$ total balls.
   - Competition adjustment factor (1.10x for IPL vs 0.90x for associate bilaterals).
4. **Reliability & Validation**:
   - 500-iteration bootstrap 95% confidence intervals.
   - Split-half (odd/even match) cross-validation and season stability testing.
   - Sensitivity analysis testing ranking robustness across 3 alternative pressure definitions.

---

## 🛠️ Project Structure
```text
Rajasthan-Royals-Hackathon/
├── outputs/
│   ├── top10_batters.csv              # Exact Top 10 Batters CSV
│   ├── top10_bowlers.csv              # Exact Top 10 Bowlers CSV
│   ├── report.docx                    # Comprehensive Methodology Report (Word)
│   ├── report.pdf                     # Publication-Grade Methodology Report (PDF)
│   ├── rr_auction_presentation.pptx   # Franchise War Room Executive Presentation (PPTX)
│   ├── enriched_ball_by_ball.parquet  # Precomputed metrics (14.6 MB)
│   └── figures/                       # Publication plots & charts
├── src/
│   ├── config.py                      # Constants & hyperparameters
│   ├── data_loader.py                 # Ingestion & data trap reconciliation
│   ├── state_derivation.py            # Cumulative match state derivation
│   ├── win_prob_model.py              # Calibrated LightGBM WP & Leverage
│   ├── baseline_models.py             # Contextual xRuns & xWickets models
│   ├── ratings.py                     # Performance rating & shrinkage
│   ├── reliability.py                 # Bootstrap CIs, split-half, stability
│   ├── generate_figures.py            # Figure generation
│   ├── generate_report.py             # Report compilation (docx & pdf)
│   ├── pipeline.py                    # Pipeline execution script
│   └── tests/                         # Unit tests
├── app.py                             # Interactive Streamlit dashboard
├── requirements.txt                   # Locked dependencies
├── Makefile                           # Command runner
└── run.ps1                            # Windows PowerShell runner
```

---

## 🚀 How to Run

### Quick Start: Launch Interactive Dashboard
```bash
streamlit run app.py
```
or via the virtual environment:
```powershell
.venv\Scripts\streamlit run app.py
```

### Run Full Pipeline & Test Suite
```bash
make all
```
or on Windows PowerShell:
```powershell
.\run.ps1
```
