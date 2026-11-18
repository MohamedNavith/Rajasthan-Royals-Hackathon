"""
Rajasthan Royals SupeRR Selector: Interactive Analytics Dashboard.
Built with Streamlit and Plotly in official RR Pink and Navy Blue branding.
"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.config import RR_PINK, RR_BLUE, RR_ROYAL_BLUE, RR_GOLD, RR_SUCCESS, RR_DANGER
from src.ratings import compute_batter_ratings, compute_bowler_ratings
from src.squad_analysis import SQUADS_2026, TRADE_DEALS, get_rr_updated_squad, get_rr_tactical_evaluation

# Page Configuration
st.set_page_config(
    page_title="SupeRR Selector | Rajasthan Royals",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Rajasthan Royals Theme
st.markdown(f"""
<style>
    /* Global Styles */
    .stApp {{
        background-color: #FAFAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* Header & Branding */
    .rr-header {{
        background: linear-gradient(135deg, {RR_BLUE} 0%, #152A55 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        border-left: 8px solid {RR_PINK};
        box-shadow: 0 4px 14px rgba(11, 27, 61, 0.12);
    }}
    .rr-header h1 {{
        color: white !important;
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        padding: 0;
    }}
    .rr-header p {{
        color: #E2E8F0;
        font-size: 1.05rem;
        margin-top: 6px;
        margin-bottom: 0;
    }}
    
    /* Metric Cards */
    .metric-card {{
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        margin-bottom: 16px;
    }}
    .metric-title {{
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .metric-val {{
        color: {RR_BLUE};
        font-size: 1.8rem;
        font-weight: 700;
        margin: 4px 0;
    }}
    
    /* Badges */
    .badge-pink {{
        background-color: {RR_PINK};
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }}
    .badge-blue {{
        background-color: {RR_BLUE};
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    output_dir = Path("outputs")
    top_b = pd.read_csv(output_dir / "top10_batters.csv")
    top_bw = pd.read_csv(output_dir / "top10_bowlers.csv")
    all_b = pd.read_csv(output_dir / "all_batters_rated.csv")
    all_bw = pd.read_csv(output_dir / "all_bowlers_rated.csv")
    enriched_df = pd.read_parquet(output_dir / "enriched_ball_by_ball.parquet")
    return top_b, top_bw, all_b, all_bw, enriched_df

try:
    top_batters, top_bowlers, all_batters, all_bowlers, df_enriched = load_data()
except Exception as e:
    st.error(f"Error loading processed data: {e}. Please ensure the pipeline has run.")
    st.stop()

# Sidebar Navigation
with st.sidebar:
    st.markdown(f"<h2 style='color: {RR_PINK}; font-weight: 800; margin-bottom: 0;'>SupeRR Selector</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 0.9rem;'>Season 2 | Round 1</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        [
            "🏆 Home", "👑 RR War Room: IPL 2027 Strategy", "📈 What is Pressure?",
            "👤 Player Profile", "⚔️ Compare Players", "🛡️ Trust & Sensitivity"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("**Dataset Scope**")
    st.markdown("• 200,999 Deliveries\n• 867 Matches (2022–2026)\n• IPL & T20 Internationals")
    st.markdown("---")
    st.caption("Developed for Rajasthan Royals Hackathon")

# Header Banner
st.markdown(f"""
<div class="rr-header">
    <h1>Rajasthan Royals: SupeRR Selector</h1>
    <p>Data-Driven Pressure Analytics & Reliability System | Unbiased, Context-Adjusted Player Ratings</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# PAGE 1: HOME
# -------------------------------------------------------------
if page == "🏆 Home":
    st.markdown("### Defining Pressure in T20 Cricket")
    st.markdown("""
    > **What counts as pressure?** In T20 cricket, pressure is not just bowling the 20th over—it is any match situation where a single delivery can dramatically alter the outcome of the match. Using our calibrated ball-by-ball Win Probability model, we calculate the **Leverage Index (WPLI)** of each ball—measuring the expected swing in win probability between a dot ball, boundary, or wicket. Deliveries in the **top 25% of match leverage** are classified as high pressure. Players are rated by their ability to elevate their performance above expected contextual baselines and maintain positive match-level consistency, shrunk through Empirical Bayes to guarantee statistical fairness.
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Rank 1 Batter</div>
            <div class="metric-val">{top_batters.iloc[0]['player_name']}</div>
            <span class="badge-pink">{top_batters.iloc[0]['pressure_rating']} Rating</span> ({int(top_batters.iloc[0]['press_balls'])} Balls)
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Rank 1 Bowler</div>
            <div class="metric-val">{top_bowlers.iloc[0]['player_name']}</div>
            <span class="badge-blue">{top_bowlers.iloc[0]['pressure_rating']} Rating</span> ({int(top_bowlers.iloc[0]['press_balls'])} Balls)
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">High Pressure Deliveries</div>
            <div class="metric-val">50,250</div>
            <span style="color: #64748B; font-size: 0.85rem;">Top 25% Leverage Cutoff</span>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Eligibility Criteria</div>
            <div class="metric-val">≥ 60 Balls</div>
            <span style="color: #64748B; font-size: 0.85rem;">Min. 10 Crunch Overs</span>
        </div>
        """, unsafe_allow_html=True)

    tab_bat, tab_bowl = st.tabs(["🏏 Top 10 Batters Under Pressure", "🎯 Top 10 Bowlers Under Pressure"])
    
    with tab_bat:
        st.markdown("#### Top 10 Batters Leaderboard")
        st.caption("Ranked by composite Pressure Reliability Score (incorporating Runs Over Expected, Strike Rate Delta, Win Probability Added, and Consistency).")
        
        display_b = top_batters[[
            'rank', 'player_name', 'pressure_rating', 'ci_lower', 'ci_upper',
            'press_balls', 'total_balls', 'press_sr', 'norm_sr', 'sr_delta', 'press_roe', 'consistency_pct'
        ]].copy()
        
        display_b['95% Confidence Interval'] = display_b.apply(lambda r: f"[{r['ci_lower']:.1f} — {r['ci_upper']:.1f}]", axis=1)
        display_b = display_b.drop(columns=['ci_lower', 'ci_upper'])
        display_b = display_b.rename(columns={
            'rank': 'Rank',
            'player_name': 'Batter',
            'pressure_rating': 'Pressure Rating',
            'press_balls': 'Pressure Balls',
            'total_balls': 'Total Balls',
            'press_sr': 'Pressure SR',
            'norm_sr': 'Normal SR',
            'sr_delta': 'SR Delta (Δ)',
            'press_roe': 'Runs Over Expected',
            'consistency_pct': 'Consistency %'
        })
        
        st.dataframe(
            display_b.style.background_gradient(subset=['Pressure Rating', 'Runs Over Expected'], cmap='PuRd')
                           .format({'Pressure SR': '{:.1f}', 'Normal SR': '{:.1f}', 'SR Delta (Δ)': '{:+.1f}', 'Runs Over Expected': '{:+.1f}', 'Consistency %': '{:.1f}%'}),
            use_container_width=True,
            hide_index=True
        )
        
        # Plotly Forest Plot of Top 10 Batters
        fig_b = go.Figure()
        fig_b.add_trace(go.Scatter(
            x=top_batters['pressure_rating'],
            y=top_batters['player_name'],
            mode='markers',
            marker=dict(color=RR_PINK, size=12),
            error_x=dict(
                type='data',
                symmetric=False,
                array=top_batters['ci_upper'] - top_batters['pressure_rating'],
                arrayminus=top_batters['pressure_rating'] - top_batters['ci_lower'],
                color=RR_BLUE,
                thickness=2,
                width=5
            ),
            text=[f"Score: {s:.2f} [{l:.1f}, {u:.1f}]" for s, l, u in zip(top_batters['pressure_rating'], top_batters['ci_lower'], top_batters['ci_upper'])],
            hoverinfo='text+y'
        ))
        fig_b.update_layout(
            title="Top 10 Batters Under Pressure with 95% Bootstrap Confidence Intervals",
            xaxis_title="Pressure Rating (0 - 100 Scale)",
            yaxis_title="",
            yaxis=dict(autorange="reversed"),
            height=400,
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=30)
        )
        st.plotly_chart(fig_b, use_container_width=True)

    with tab_bowl:
        st.markdown("#### Top 10 Bowlers Leaderboard")
        st.caption("Ranked by composite Pressure Reliability Score (incorporating Runs Saved, Wickets Over Expected, Economy Delta, Boundary Control, and Consistency).")
        
        display_bw = top_bowlers[[
            'rank', 'player_name', 'pressure_rating', 'ci_lower', 'ci_upper',
            'press_balls', 'total_balls', 'press_economy', 'norm_economy', 'economy_delta', 'press_wickets', 'press_runs_saved', 'consistency_pct'
        ]].copy()
        display_bw['95% Confidence Interval'] = display_bw.apply(lambda r: f"[{r['ci_lower']:.1f} — {r['ci_upper']:.1f}]", axis=1)
        display_bw = display_bw.drop(columns=['ci_lower', 'ci_upper'])
        display_bw = display_bw.rename(columns={
            'rank': 'Rank',
            'player_name': 'Bowler',
            'pressure_rating': 'Pressure Rating',
            'press_balls': 'Pressure Balls',
            'total_balls': 'Total Balls',
            'press_economy': 'Pressure Economy',
            'norm_economy': 'Normal Economy',
            'economy_delta': 'Economy Delta (Δ)',
            'press_wickets': 'Pressure Wickets',
            'press_runs_saved': 'Runs Saved',
            'consistency_pct': 'Consistency %'
        })
        
        st.dataframe(
            display_bw.style.background_gradient(subset=['Pressure Rating', 'Runs Saved'], cmap='Blues')
                            .format({'Pressure Economy': '{:.2f}', 'Normal Economy': '{:.2f}', 'Economy Delta (Δ)': '{:+.2f}', 'Runs Saved': '{:+.1f}', 'Consistency %': '{:.1f}%'}),
            use_container_width=True,
            hide_index=True
        )
        
        fig_bw = go.Figure()
        fig_bw.add_trace(go.Scatter(
            x=top_bowlers['pressure_rating'],
            y=top_bowlers['player_name'],
            mode='markers',
            marker=dict(color=RR_BLUE, size=12),
            error_x=dict(
                type='data',
                symmetric=False,
                array=top_bowlers['ci_upper'] - top_bowlers['pressure_rating'],
                arrayminus=top_bowlers['pressure_rating'] - top_bowlers['ci_lower'],
                color=RR_PINK,
                thickness=2,
                width=5
            ),
            text=[f"Score: {s:.2f} [{l:.1f}, {u:.1f}]" for s, l, u in zip(top_bowlers['pressure_rating'], top_bowlers['ci_lower'], top_bowlers['ci_upper'])],
            hoverinfo='text+y'
        ))
        fig_bw.update_layout(
            title="Top 10 Bowlers Under Pressure with 95% Bootstrap Confidence Intervals",
            xaxis_title="Pressure Rating (0 - 100 Scale)",
            yaxis_title="",
            yaxis=dict(autorange="reversed"),
            height=400,
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=30)
        )
        st.plotly_chart(fig_bw, use_container_width=True)

# -------------------------------------------------------------
# PAGE: RR WAR ROOM (IPL 2027 AUCTION STRATEGY)
# -------------------------------------------------------------
elif page == "👑 RR War Room: IPL 2027 Strategy":
    st.markdown("### 👑 Rajasthan Royals War Room: IPL 2027 Strategy & Tactical Blueprint")
    st.markdown("""
    **Transforming Pressure Analytics into Silverware:** This command center equips the Director of Cricket, Head Coach, 
    and Scouting Analysts with an interactive war-room interface. Every recommendation is grounded in ball-by-ball empirical truth, 
    contextual leverage ($WPLI$), home-ground dynamics at Sawai Mansingh Stadium (Jaipur), real-world availability intelligence, 
    and disciplined auction economics.
    """)
    
    # ---------------------------------------------------------
    # 1. LIVE PURSE & SQUAD STATUS KPI BANNER
    # ---------------------------------------------------------
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric("Total Purse", "₹27.05 Cr", "Available Budget")
    with kpi2:
        st.metric("Retained Core", "8 Players", "Jaiswal, Parag, Jurel...")
    with kpi3:
        st.metric("Open Slots to Fill", "3 Key Slots", "2 OS + 1 Domestic")
    with kpi4:
        st.metric("Target Spend", "₹11.30–13.80 Cr", "Planned Outlay")
    with kpi5:
        st.metric("Emergency Buffer", "+₹13.25–15.75 Cr", "100% Solvent Cushion")
        
    st.markdown("---")
    
    # ---------------------------------------------------------
    # 2. ONE-CLICK INSTANT REPORT GENERATION & DOWNLOAD HUB
    # ---------------------------------------------------------
    st.markdown("#### 📥 Instant Report Generation & Download Hub")
    st.caption("Click to compile an up-to-the-minute publication-grade PDF report or download executive presentations.")
    
    rep_col1, rep_col2, rep_col3, rep_col4 = st.columns([1.5, 1.2, 1.2, 1.2])
    
    with rep_col1:
        if st.button("🔄 Recompile Fresh PDF Report", type="primary", use_container_width=True):
            with st.spinner("Compiling publication-grade PDF report via ReportLab..."):
                from src.generate_report import generate_reports
                generate_reports()
            st.success("✅ Official PDF & DOCX Dossiers Compiled!")
            
    with rep_col2:
        pdf_file = Path("outputs/report.pdf")
        if pdf_file.exists():
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="📄 Download Report (PDF)",
                    data=f,
                    file_name="RR_IPL2027_War_Room_Strategy.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.button("📄 PDF Not Ready", disabled=True, use_container_width=True)
            
    with rep_col3:
        docx_file = Path("outputs/report.docx")
        if docx_file.exists():
            with open(docx_file, "rb") as f:
                st.download_button(
                    label="📝 Download Report (DOCX)",
                    data=f,
                    file_name="RR_IPL2027_War_Room_Strategy.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
        else:
            st.button("📝 DOCX Not Ready", disabled=True, use_container_width=True)
            
    with rep_col4:
        pptx_file = Path("outputs/rr_auction_presentation.pptx")
        if pptx_file.exists():
            with open(pptx_file, "rb") as f:
                st.download_button(
                    label="📊 War Room Deck (PPTX)",
                    data=f,
                    file_name="RR_IPL2027_Executive_Deck.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True
                )
        else:
            st.button("📊 PPTX Not Ready", disabled=True, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # 3. INTERACTIVE WAR ROOM MODULE TABS
    # ---------------------------------------------------------
    subtab1, subtab2, subtab3, subtab4, subtab5 = st.tabs([
        "🔍 1. Forensic Loss Audit (2024–26)",
        "🎯 2. Target Slots & 10-Player Shortlists",
        "⏱️ 3. 20-Over Bowling Matrix",
        "💎 4. Tactical Luxury Permutations",
        "💰 5. Live Purse Simulator"
    ])
    
    # ---------------------------------------------------------
    # TAB 1: FORENSIC LOSS AUDIT
    # ---------------------------------------------------------
    with subtab1:
        st.markdown("#### 🔍 Ball-by-Ball Forensic Diagnosis of RR's 23 Defeats (2024–2026)")
        st.markdown("""
        *Note for Analysts:* Mohammad Shami was acquired ahead of 2026/27 via trade from LSG (*Curran for Shami + Siddharth*); 
        Jofra Archer was retained post-rehab. Neither bowled in RR's 2024–2025 defeats. The losses were driven by:
        """)
        
        loss_c1, loss_c2 = st.columns(2)
        
        with loss_c1:
            st.markdown("**1. Secondary Seam Collapse in Defeats**")
            bowler_losses_df = pd.DataFrame({
                "Bowler": ["Akash Madhwal", "FazalHaq Farooqi", "Tushar Deshpande", "Brijesh Sharma", "M. Theekshana", "Sandeep Sharma", "Trent Boult"],
                "Loss Economy": [12.45, 12.35, 11.52, 11.32, 10.63, 10.09, 9.57],
                "Wickets": [1, 0, 10, 7, 7, 10, 5],
                "Dot Ball %": [28.8, 27.5, 31.0, 32.3, 30.6, 33.6, 37.9]
            })
            
            fig_bowl_loss = px.bar(
                bowler_losses_df,
                x="Bowler",
                y="Loss Economy",
                color="Loss Economy",
                color_continuous_scale="Reds",
                text="Loss Economy",
                title="Bowler Economy in RR's 23 Defeats vs Target (< 9.00 RPO)"
            )
            fig_bowl_loss.add_hline(y=9.00, line_dash="dash", line_color=RR_BLUE, annotation_text="Target Ceiling (9.00 RPO)")
            fig_bowl_loss.update_layout(height=350, template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_bowl_loss, use_container_width=True)
            
        with loss_c2:
            st.markdown("**2. Finisher Breakdown vs Lone Warrior Dynamic**")
            batter_losses_df = pd.DataFrame({
                "Batter": ["Shimron Hetmyer", "Shubham Dubey", "Nitish Rana", "Sanju Samson", "Vaibhav Sooryavanshi"],
                "ROE (Runs Over Expected)": [-50.4, -18.2, -14.5, 4.2, 58.6],
                "Loss Strike Rate": [132.6, 146.7, 134.8, 147.9, 209.4],
                "Category": ["Finisher Collapse", "Finisher Collapse", "Middle Stall", "Anchor", "Lone Warrior Prodigy"]
            })
            
            fig_bat_loss = px.bar(
                batter_losses_df,
                x="Batter",
                y="ROE (Runs Over Expected)",
                color="ROE (Runs Over Expected)",
                color_continuous_scale="RdYlGn",
                text="ROE (Runs Over Expected)",
                title="Runs Over Expected (ROE) in RR Defeats"
            )
            fig_bat_loss.add_hline(y=0.0, line_dash="solid", line_color="#94A3B8")
            fig_bat_loss.update_layout(height=350, template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_bat_loss, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 🏛️ The 5-Year Championship Winning Formula Audit")
        champ_df = pd.DataFrame({
            "Season & Champion": ["2024 KKR", "2023 CSK", "2022 GT", "2021 CSK", "2025/26 RCB"],
            "Overseas Deployment (4 OS)": ["Narine, Salt, Russell, Starc", "Conway, Moeen, Theekshana, Pathirana", "Wade, Miller, Rashid, Ferguson/Joseph", "Faf du Plessis, Moeen, Bravo, Hazlewood", "Salt, David, Hazlewood, Shepherd/Thushara"],
            "Balance Architecture": ["2 Batters + 2 Bowlers", "2 Batters/AR + 2 Bowlers", "2 Batters + 2 Bowlers", "2 Batters + 2 Bowlers", "2 Batters + 2 Bowlers"],
            "Batting & Bowling Depth": ["Batting till #8; 6 bowling options", "Batting till #8 (Dhoni #8); 6 bowling options", "Batting till #7 (Tewatia/Rashid); 6 bowling options", "Batting till #8 (Bravo #8); 6 bowling options", "Batting till #8; 6 bowling options"]
        })
        st.dataframe(champ_df, hide_index=True, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 2: TARGET SLOTS & 10-PLAYER SHORTLISTS
    # ---------------------------------------------------------
    with subtab2:
        st.markdown("#### 🎯 Interactive Target Slot Explorer & 10-Player Shortlists")
        
        slot_selected = st.radio(
            "Select Tactical Slot to Inspect:",
            [
                "🔹 Slot 1: Overseas Middle Spin Enforcer (Batting #4)",
                "🔹 Slot 2: Lower-Middle Finisher & 2nd WK (Batting #6)",
                "🔹 Slot 3: Overseas Express Death Bowler (Bowling #9)"
            ],
            horizontal=True
        )
        
        if "Slot 1" in slot_selected:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 6px solid {RR_PINK}; background-color: #FFF5F8;">
                <h4 style="color:{RR_PINK}; margin:0;">🌟 Primary Target: Pathum Nissanka (Released by Delhi Capitals)</h4>
                <p style="margin:4px 0 0 0; color:#334155; font-size:0.92rem;">
                    <b>Why He Wins:</b> 347 pressure balls, <b>141.5 SR</b>, <b>+21.2 ROE</b>. Exceptional <b>182.4 SR at SMS Jaipur</b>. 
                    Supreme wrist-work against finger and wrist-spin. In peak international form with full SLC tournament clearance.
                    <br><b>Valuation:</b> Base ₹2.50 Cr | <b>Target Bid: ₹3.20 Cr</b> | <b>Max Walkaway: ₹3.80 Cr</b> | <b>Key Rivals:</b> DC, SRH.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            s1_df = pd.DataFrame([
                {"#": 1, "Player": "Pathum Nissanka", "Status": "Released DC", "Pressure Stats": "347b, 141.5 SR, +21.2 ROE", "SMS Jaipur Record": "182.4 SR (34b)", "Role Execution": "Master vs spin; anchor; peak form", "Rivals": "DC, SRH", "Max Ceiling": "₹3.80 Cr"},
                {"#": 2, "Player": "Kamindu Mendis", "Status": "Released SRH", "Pressure Stats": "458b, 139.3 SR, +40.3 ROE", "SMS Jaipur Record": "Proven Asian form", "Role Execution": "Left-hand rock; ambidextrous off/leg spin", "Rivals": "SRH, MI", "Max Ceiling": "₹2.80 Cr"},
                {"#": 3, "Player": "Matthew Short", "Status": "Released CSK", "Pressure Stats": "65b, 123.1 SR, 161.1 Death SR", "SMS Jaipur Record": "Tall boundary striker", "Role Execution": "Punches lengths; 2 overs off-spin", "Rivals": "CSK, PBKS", "Max Ceiling": "₹1.80 Cr"},
                {"#": 4, "Player": "Daryl Mitchell", "Status": "Uncontracted", "Pressure Stats": "142b, 135.8 SR, +12.4 ROE", "SMS Jaipur Record": "Clears big boundaries", "Role Execution": "Down-the-ground power vs spin", "Rivals": "CSK, PBKS", "Max Ceiling": "₹2.20 Cr"},
                {"#": 5, "Player": "Rachin Ravindra", "Status": "Released KKR", "Pressure Stats": "292b, 123.3 SR, -59.2 ROE", "SMS Jaipur Record": "146.6 SR (58b)", "Role Execution": "Solid vs pace; tidy left-arm spin", "Rivals": "KKR, CSK", "Max Ceiling": "₹2.50 Cr"},
                {"#": 6, "Player": "Matthew Breetzke", "Status": "Released LSG", "Pressure Stats": "72b, 94.4 SR, 115.6 Death SR", "SMS Jaipur Record": "Strong off backfoot", "Role Execution": "Tall upright puncher vs express pace", "Rivals": "LSG, DC", "Max Ceiling": "₹1.20 Cr"},
                {"#": 7, "Player": "Tim Seifert", "Status": "Uncontracted", "Pressure Stats": "188b, 148.9 SR, +14.5 ROE", "SMS Jaipur Record": "Rapid sweep hitter", "Role Execution": "360° sweeper vs spin; reserve WK", "Rivals": "KKR, PBKS", "Max Ceiling": "₹1.50 Cr"},
                {"#": 8, "Player": "Michael Bracewell", "Status": "Uncontracted", "Pressure Stats": "114b, 142.1 SR, 7.80 Econ", "SMS Jaipur Record": "Down-order power", "Role Execution": "Off-spinning all-rounder vs LHBs", "Rivals": "RCB, SRH", "Max Ceiling": "₹1.80 Cr"},
                {"#": 9, "Player": "Rovman Powell", "Status": "Uncontracted", "Pressure Stats": "240b, 146.2 SR, +18.0 ROE", "SMS Jaipur Record": "Clears 75m fence", "Role Execution": "Raw physical leverage; former RR player", "Rivals": "DC, KKR", "Max Ceiling": "₹2.00 Cr"},
                {"#": 10, "Player": "Lhuan-dre Pretorius", "Status": "Retained Core (RR)", "Pressure Stats": "26b, 138.5 SR, 178.0 Death SR", "SMS Jaipur Record": "116.7 SR (6b)", "Role Execution": "In-house 19yo prodigy; zero auction spend", "Rivals": "Internal", "Max Ceiling": "Retained (₹0.50 Cr)"}
            ])
            st.dataframe(s1_df, hide_index=True, use_container_width=True)
            
            st.warning("⚠️ **Real-World Exclusions:** Jacob Bethell opted out of IPL 2027 to manage right-knee surgery rehabilitation with ECB; Ben Duckett is banned for 2 seasons under BCCI withdrawal rules.")
            
        elif "Slot 2" in slot_selected:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 6px solid {RR_BLUE}; background-color: #F8FAFC;">
                <h4 style="color:{RR_BLUE}; margin:0;">🌟 Primary Starting #6: Donovan Ferreira (Retained Core) | Primary Domestic Buy: Karun Nair</h4>
                <p style="margin:4px 0 0 0; color:#334155; font-size:0.92rem;">
                    <b>Donovan Ferreira:</b> Retained for ₹0.75 Cr. <b>227.3 SR at SMS Jaipur</b>, 189.4 Death SR, 360° hitter, dual keeper.
                    <br><b>Karun Nair:</b> Top domestic auction pick (₹1.50 Cr max). <b>174.6 Pressure SR (+47.8 Delta)</b>, 157.1 SR at SMS.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            s2_df = pd.DataFrame([
                {"#": 1, "Player": "Donovan Ferreira", "Origin": "Overseas", "Status": "Retained Core", "Pressure Stats": "62b, 189.4 Death SR", "SMS Jaipur Record": "227.3 SR (44b)", "Role Execution": "Retained star; 360° death hitter; reserve WK", "Max Ceiling": "Retained (₹0.75 Cr)"},
                {"#": 2, "Player": "Karun Nair", "Origin": "Indian", "Status": "Released DC", "Pressure Stats": "63b, 174.6 SR, +47.8 Delta", "SMS Jaipur Record": "157.1 SR (28b)", "Role Execution": "Peak domestic form; clutch composure; Impact Sub", "Max Ceiling": "₹1.50 Cr"},
                {"#": 3, "Player": "Shahrukh Khan", "Origin": "Indian", "Status": "Released GT", "Pressure Stats": "551b, 133.6 SR, +2.0 ROE", "SMS Jaipur Record": "179.2 SR (24b)", "Role Execution": "Raw physical strength vs spin; handy off-spin", "Max Ceiling": "₹4.50 Cr"},
                {"#": 4, "Player": "Mahipal Lomror", "Origin": "Indian", "Status": "Released MI", "Pressure Stats": "19b, 163.2 SR, 156.5 Death SR", "SMS Jaipur Record": "Local ground knowledge", "Role Execution": "Rajasthan native; targets short mid-wicket fence", "Max Ceiling": "₹1.80 Cr"},
                {"#": 5, "Player": "Nehal Wadhera", "Origin": "Indian", "Status": "Released PBKS", "Pressure Stats": "127b, 117.3 SR, -30.1 ROE", "SMS Jaipur Record": "171.2 SR (80b)", "Role Execution": "Fearless back-foot punch vs 145+ km/h pace", "Max Ceiling": "₹2.80 Cr"},
                {"#": 6, "Player": "Abishek Porel", "Origin": "Indian", "Status": "Released DC", "Pressure Stats": "109b, 140.4 SR, 147.1 Death SR", "SMS Jaipur Record": "90.0 SR (10b)", "Role Execution": "Dynamic left-handed 360° keeper-finisher", "Max Ceiling": "₹2.20 Cr"},
                {"#": 7, "Player": "Zak Foulkes", "Origin": "Overseas", "Status": "Released CSK", "Pressure Stats": "12b, 183.3 SR, +8.3 ROE", "SMS Jaipur Record": "9.22 Seam Econ", "Role Execution": "140 km/h seam-bowling all-rounder; Ferreira cover", "Max Ceiling": "₹1.40 Cr"},
                {"#": 8, "Player": "George Linde", "Origin": "Overseas", "Status": "Released LSG", "Pressure Stats": "34b, 117.6 SR, 158.0 Death SR", "SMS Jaipur Record": "6.41 Spin Econ", "Role Execution": "Left-arm orthodox spinner; economical lower-order bat", "Max Ceiling": "₹1.20 Cr"},
                {"#": 9, "Player": "Aman Khan", "Origin": "Indian", "Status": "Released CSK", "Pressure Stats": "22b, 122.7 SR, 145.0 Death SR", "SMS Jaipur Record": "Seam utility", "Role Execution": "Fast-medium domestic seam bowler and pinch hitter", "Max Ceiling": "₹0.80 Cr"},
                {"#": 10, "Player": "Dasun Shanaka", "Origin": "Overseas", "Status": "Retained Core", "Pressure Stats": "105b, 94.3 SR, 154.9 Death SR", "SMS Jaipur Record": "133.3 SR (12b)", "Role Execution": "International captain; seam all-rounder; squad depth", "Max Ceiling": "Retained (₹1.00 Cr)"}
            ])
            st.dataframe(s2_df, hide_index=True, use_container_width=True)
            
        elif "Slot 3" in slot_selected:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 6px solid {RR_SUCCESS}; background-color: #F0FDF4;">
                <h4 style="color:{RR_SUCCESS}; margin:0;">🌟 Primary 100% Fit Target: Gerald Coetzee | Precision Skill Target: Matheesha Pathirana</h4>
                <p style="margin:4px 0 0 0; color:#334155; font-size:0.92rem;">
                    <b>Gerald Coetzee:</b> 100% fit, bowling 150 km/h, <b>7.84 Pressure Econ</b>, +15.1 Runs Saved. Zero surgical baggage. (Target ₹4.0–5.0 Cr).
                    <br><b>Matheesha Pathirana:</b> Unmatched yorker numbers (7.44 Ov 18 Econ, 8.89 Ov 19 Econ), but underwent surgical hamstring repair in France (June 2026). Bid strictly capped at ₹7.50 Cr.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            s3_df = pd.DataFrame([
                {"#": 1, "Player": "Gerald Coetzee", "Status": "Released SRH", "Pressure Stats": "98b, 7.84 Econ, +15.1 Saved", "Death Phase Stats": "196b, 9.43 Econ, 17 Wkts", "SMS Jaipur Record": "150 km/h bouncers", "Tactical & Medical Profile": "100% Fit & Active; 150 km/h hostility; zero surgery", "Max Ceiling": "₹5.00 Cr"},
                {"#": 2, "Player": "Matheesha Pathirana", "Status": "Released KKR", "Pressure Stats": "192b, 9.59 Econ, +21.1 Saved", "Death Phase Stats": "541b, 9.23 Econ, 50 Wkts", "SMS Jaipur Record": "Ov 18: 7.44 / Ov 19: 8.89", "Tactical & Medical Profile": "Yorker King; June 2026 France hamstring surgery; bid capped", "Max Ceiling": "₹7.50 Cr"},
                {"#": 3, "Player": "Spencer Johnson", "Status": "Released CSK", "Pressure Stats": "71b, 9.46 Econ, -5.7 Saved", "Death Phase Stats": "90b, 8.53 Econ, 9 Wkts", "SMS Jaipur Record": "9.25 Econ (24b)", "Tactical & Medical Profile": "145+ km/h left-arm angle; steep SMS bounce; back recovered", "Max Ceiling": "₹3.00 Cr"},
                {"#": 4, "Player": "Trent Boult", "Status": "Released MI", "Pressure Stats": "208b, 8.68 Econ, 11 Wkts", "Death Phase Stats": "325b, 10.14 Econ, 23 Wkts", "SMS Jaipur Record": "8.44 Econ, 8 Wkts", "Tactical & Medical Profile": "Powerplay swing royalty (5.92 Ov 1 Econ); franchise icon", "Max Ceiling": "₹4.50 Cr"},
                {"#": 5, "Player": "Lockie Ferguson", "Status": "Released PBKS", "Pressure Stats": "113b, 9.88 Econ, -5.2 Saved", "Death Phase Stats": "326b, 10.27 Econ, 16 Wkts", "SMS Jaipur Record": "152 km/h yorkers", "Tactical & Medical Profile": "Skiddy express pace; aggressive bouncers at the death", "Max Ceiling": "₹3.00 Cr"},
                {"#": 6, "Player": "Anrich Nortje", "Status": "Released LSG", "Pressure Stats": "51b, 13.41 Econ, -32.3 Saved", "Death Phase Stats": "286b, 11.48 Econ, 15 Wkts", "SMS Jaipur Record": "12.00 Econ (24b)", "Tactical & Medical Profile": "Express pace when healthy; working back to peak rhythm", "Max Ceiling": "₹2.20 Cr"},
                {"#": 7, "Player": "Luke Wood", "Status": "Released GT", "Pressure Stats": "312b, 8.56 Econ, +14.6 Saved", "Death Phase Stats": "586b, 9.93 Econ, 56 Wkts", "SMS Jaipur Record": "8.67 Econ (18b)", "Tactical & Medical Profile": "Left-arm swing up front; deceptive slower bouncers", "Max Ceiling": "₹1.80 Cr"},
                {"#": 8, "Player": "Adam Milne", "Status": "RR Core", "Pressure Stats": "60b, 9.70 Econ, +11.4 Saved", "Death Phase Stats": "149b, 10.59 Econ, 13 Wkts", "SMS Jaipur Record": "Clean seam release", "Tactical & Medical Profile": "150 km/h hit-the-deck bowler; low-cost buyback depth", "Max Ceiling": "₹1.20 Cr"},
                {"#": 9, "Player": "Riley Meredith", "Status": "Uncontracted", "Pressure Stats": "72b, 6.08 Econ, +36.5 Saved", "Death Phase Stats": "128b, 8.44 Econ, 12 Wkts", "SMS Jaipur Record": "High skiddy pace", "Tactical & Medical Profile": "Elite pressure economy in data; skids onto pads at 145+", "Max Ceiling": "₹1.50 Cr"},
                {"#": 10, "Player": "Nandre Burger", "Status": "Retained Core", "Pressure Stats": "138b, 10.17 Econ, -24.5 Saved", "Death Phase Stats": "81b, 8.89 Econ, 7 Wkts", "SMS Jaipur Record": "6.22 Econ in Ov 19!", "Tactical & Medical Profile": "In-house 145+ km/h left-arm enforcer; zero auction spend", "Max Ceiling": "Retained (₹1.50 Cr)"}
            ])
            st.dataframe(s3_df, hide_index=True, use_container_width=True)
            
            st.warning("⚠️ **Real-World Exclusion:** Mustafizur Rahman excluded due to official BCCI directives instructing KKR to release him amid civil unrest in Bangladesh (high diplomatic/NOC cancellation risk).")

    # ---------------------------------------------------------
    # TAB 3: 20-OVER BOWLING MATRIX
    # ---------------------------------------------------------
    with subtab3:
        st.markdown("#### ⏱️ The Strict 20-Over Law-Compliant Bowling Matrix")
        st.markdown("""
        **Rigorously Structured Non-Consecutive Over Sequence:** 
        Archer Over 1 (10 Over 1 wickets) | Shami Over 2 (6.11 Ov 1 Econ, 58.8% dots) | Archer Over 20 Closer (7.50 Econ, 39.3% dots) | 
        Shami completes 3 overs in Powerplay | Alternating End A / End B throughout.
        """)
        
        phase_filter = st.selectbox(
            "Filter by Match Phase:",
            ["All 20 Overs", "Powerplay (Overs 1–6)", "Middle Overs (Overs 7–15)", "Death Overs (Overs 16–20)"]
        )
        
        matrix_data = [
            {"Over": 1, "End": "End A", "Bowler": "Jofra Archer (1)", "Career Econ": 8.57, "Dots %": "52.9%", "Jaipur Econ": "10.38 RPO", "Phase": "Powerplay (Overs 1–6)", "Tactical Objective": "1st Over Tone-Setter: 10 Wickets in Over 1 (2024–26)."},
            {"Over": 2, "End": "End B", "Bowler": "Mohd. Shami (1)", "Career Econ": 6.11, "Dots %": "58.8%", "Jaipur Econ": "2.00 RPO", "Phase": "Powerplay (Overs 1–6)", "Tactical Objective": "Upright seam swing: 6.11 Ov 1 Econ, 58.8% dots; 2.00 at SMS."},
            {"Over": 3, "End": "End A", "Bowler": "Ravi Bishnoi (1)", "Career Econ": 7.60, "Dots %": "40.0%", "Jaipur Econ": "--", "Phase": "Powerplay (Overs 1–6)", "Tactical Objective": "PP Spin Ambush: Wrong-un breaks top-order batting rhythm."},
            {"Over": 4, "End": "End B", "Bowler": "Mohd. Shami (2)", "Career Econ": 7.38, "Dots %": "39.6%", "Jaipur Econ": "7.00 RPO", "Phase": "Powerplay (Overs 1–6)", "Tactical Objective": "Targets top of off-stump with seam movement."},
            {"Over": 5, "End": "End A", "Bowler": "Jofra Archer (2)", "Career Econ": 10.18, "Dots %": "43.1%", "Jaipur Econ": "15.00 RPO", "Phase": "Powerplay (Overs 1–6)", "Tactical Objective": "150 km/h enforcer burst targeting bodyline and ribs."},
            {"Over": 6, "End": "End B", "Bowler": "Mohd. Shami (3)", "Career Econ": 8.52, "Dots %": "32.5%", "Jaipur Econ": "9.80 RPO", "Phase": "Powerplay (Overs 1–6)", "Tactical Objective": "Completes 3-over Powerplay quota attacking edge."},
            {"Over": 7, "End": "End A", "Bowler": "Ravindra Jadeja (1)", "Career Econ": 7.29, "Dots %": "38.0%", "Jaipur Econ": "4.00 RPO", "Phase": "Middle Overs (Overs 7–15)", "Tactical Objective": "Flat left-arm darts from Pavilion End; chokes run rate."},
            {"Over": 8, "End": "End B", "Bowler": "Coetzee / Pathirana (1)", "Career Econ": 8.88, "Dots %": "35.0%", "Jaipur Econ": "9.00 RPO", "Phase": "Middle Overs (Overs 7–15)", "Tactical Objective": "High-pace change of rhythm; hard lengths."},
            {"Over": 9, "End": "End A", "Bowler": "Ravindra Jadeja (2)", "Career Econ": 7.73, "Dots %": "30.0%", "Jaipur Econ": "4.00 RPO", "Phase": "Middle Overs (Overs 7–15)", "Tactical Objective": "Tight line outside off; dries up boundary options."},
            {"Over": 10, "End": "End B", "Bowler": "Ravi Bishnoi (2)", "Career Econ": 8.19, "Dots %": "36.3%", "Jaipur Econ": "--", "Phase": "Middle Overs (Overs 7–15)", "Tactical Objective": "Attacking wrong-uns from High Court End."},
            {"Over": 11, "End": "End A", "Bowler": "Ravindra Jadeja (3)", "Career Econ": 8.23, "Dots %": "31.0%", "Jaipur Econ": "4.00 RPO", "Phase": "Middle Overs (Overs 7–15)", "Tactical Objective": "Masterclass control: 4.00 Economy at SMS Jaipur."},
            {"Over": 12, "End": "End B", "Bowler": "Ravi Bishnoi (3)", "Career Econ": 8.23, "Dots %": "33.0%", "Jaipur Econ": "--", "Phase": "Middle Overs (Overs 7–15)", "Tactical Objective": "Tandem spin choke (sub-7.80 RPO combined)."},
            {"Over": 13, "End": "End A", "Bowler": "Ravindra Jadeja (4)", "Career Econ": 7.14, "Dots %": "32.0%", "Jaipur Econ": "--", "Phase": "Middle Overs (Overs 7–15)", "Tactical Objective": "Completes 4 overs (7.87 career middle Econ)."},
            {"Over": 14, "End": "End B", "Bowler": "Coetzee / Pathirana (2)", "Career Econ": 6.57, "Dots %": "40.0%", "Jaipur Econ": "--", "Phase": "Middle Overs (Overs 7–15)", "Tactical Objective": "Round-arm yorkers break set partnerships."},
            {"Over": 15, "End": "End A", "Bowler": "Ravi Bishnoi (4)", "Career Econ": 8.05, "Dots %": "35.0%", "Jaipur Econ": "--", "Phase": "Middle Overs (Overs 7–15)", "Tactical Objective": "Completes 4 overs (76 middle-overs wickets)."},
            {"Over": 16, "End": "End B", "Bowler": "Jofra Archer (3)", "Career Econ": 7.91, "Dots %": "37.9%", "Jaipur Econ": "12.00 RPO", "Phase": "Death Overs (Overs 16–20)", "Tactical Objective": "150 km/h enforcer burst (7.91 death Econ)."},
            {"Over": 17, "End": "End A", "Bowler": "Coetzee / Pathirana (3)", "Career Econ": 10.44, "Dots %": "30.2%", "Jaipur Econ": "--", "Phase": "Death Overs (Overs 16–20)", "Tactical Objective": "Wide yorkers targeting boundary traps."},
            {"Over": 18, "End": "End B", "Bowler": "Mohd. Shami (4)", "Career Econ": 9.67, "Dots %": "22.2%", "Jaipur Econ": "3.00 RPO", "Phase": "Death Overs (Overs 16–20)", "Tactical Objective": "Reverse-seam yorkers (3.00 Econ at SMS)."},
            {"Over": 19, "End": "End A", "Bowler": "Coetzee / Pathirana (4)", "Career Econ": 8.89, "Dots %": "38.8%", "Jaipur Econ": "8.67 RPO", "Phase": "Death Overs (Overs 16–20)", "Tactical Objective": "Toe-crushing yorkers (8.89 Econ, 14 wkts in Ov 19)."},
            {"Over": 20, "End": "End B", "Bowler": "Jofra Archer (4)", "Career Econ": 7.50, "Dots %": "39.3%", "Jaipur Econ": "9.00 RPO", "Phase": "Death Overs (Overs 16–20)", "Tactical Objective": "The Closer: 7.50 Econ and 39.3% dots in Over 20."}
        ]
        
        matrix_df = pd.DataFrame(matrix_data)
        if phase_filter != "All 20 Overs":
            filtered_matrix = matrix_df[matrix_df["Phase"] == phase_filter]
        else:
            filtered_matrix = matrix_df
            
        st.dataframe(filtered_matrix.drop(columns=["Phase"]), hide_index=True, use_container_width=True)
        
        st.success("✅ **Law Compliance Verified:** Zero consecutive overs for any bowler. End A / End B alternating rhythm strictly preserved. Shami completely shielded from Overs 19 & 20.")

    # ---------------------------------------------------------
    # TAB 4: TACTICAL LUXURY PERMUTATIONS
    # ---------------------------------------------------------
    with subtab4:
        st.markdown("#### 💎 Tactical Luxury: 4 Strategic Lineup Permutations")
        st.markdown("Our squad depth provides the captain and coaching staff with 4 specialized combinations:")
        
        perm = st.radio(
            "Select Tactical Permutation:",
            [
                "🏰 Permutation A: SMS Jaipur Spin-Strangle (Home Defense)",
                "⚡ Permutation B: High-Velocity Enforcer (Fast Away Surfaces)",
                "🏏 Permutation C: Bat-Deep Chasing Machine (200+ Shootouts)",
                "🧤 Permutation D: Dual-Gloveman & In-Game Contingency"
            ]
        )
        
        if "Permutation A" in perm:
            st.info("""
            **Conditions:** Dry, abrasive Jaipur pitch; large 75m straight boundary.
            <br>• **10–12 Overs of Spin:** Jadeja (4 ov) + Bishnoi (4 ov) + Parag (2–3 ov) + Kamindu Mendis / Matthew Short (2 ov).
            <br>• **Fast Bowlers restricted to 8 overs:** Shami (3 in PP, 1 at death), Archer (2 in PP, 2 at death).
            <br>• **Impact Sub:** Sandeep Sharma (9.03 SMS Econ) replaces an opener to bowl dipping knuckleballs.
            """, icon="🏰")
        elif "Permutation B" in perm:
            st.info("""
            **Conditions:** True bounce, high pace, small boundaries (Wankhede / Eden Gardens).
            <br>• **Four-Pronged 145–150 km/h Pace Barrage:** Archer (150 km/h) + Coetzee (150 km/h) + Shami (142 km/h seam) + Nandre Burger (145+ km/h left-arm via Impact Sub).
            <br>• Opposition batters face unrelenting pace and bounce from both ends.
            """, icon="⚡")
        elif "Permutation C" in perm:
            st.info("""
            **Conditions:** Flat track, heavy dew in 2nd innings, target > 200.
            <br>• **Batting Depth Down to #9:** Jaiswal, Sooryavanshi, Parag, Nissanka, Jurel, Ferreira, Jadeja, Karun Nair (Impact Sub), Bishnoi, Shami, Archer.
            <br>• Every batter through #8 strikes at > 140.0, eliminating collapse risks under steep required run rates.
            """, icon="🏏")
        elif "Permutation D" in perm:
            st.info("""
            **Contingency:** In-game hand injury or split webbing for primary wicketkeeper.
            <br>• **Dual-Gloveman Architecture:** Dhruv Jurel (Primary WK) + Donovan Ferreira (Active WK) + Lhuan-dre Pretorius (Squad Reserve WK).
            <br>• If Jurel is injured, Ferreira takes the gloves without disrupting team balance or requiring an emergency substitution.
            """, icon="🧤")

    # ---------------------------------------------------------
    # TAB 5: LIVE PURSE SIMULATOR
    # ---------------------------------------------------------
    with subtab5:
        st.markdown("#### 💰 Live Auction Purse Simulator (Budget: ₹27.05 Crore)")
        st.markdown("Tweak recommended maximum bids to test franchise solvency and emergency cash reserves:")
        
        sim_c1, sim_c2 = st.columns(2)
        with sim_c1:
            bid_death = st.slider("Overseas Death Slinger (#9) Bid (₹ Cr)", min_value=3.0, max_value=8.5, value=6.5, step=0.25)
            bid_mid = st.slider("Overseas Middle Enforcer (#4) Bid (₹ Cr)", min_value=1.5, max_value=5.0, value=3.2, step=0.1)
            bid_dom = st.slider("Domestic Clutch Batter (Impact Sub) Bid (₹ Cr)", min_value=0.5, max_value=2.5, value=1.0, step=0.1)
        with sim_c2:
            bid_spin = st.slider("Mystery Spin Steal Bid (₹ Cr)", min_value=0.3, max_value=1.5, value=0.6, step=0.1)
            bid_pacer = st.slider("Backup Express Pacer Bid (₹ Cr)", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
            bid_reserve = st.slider("Domestic Depth Reserve Bid (₹ Cr)", min_value=0.3, max_value=1.2, value=0.5, step=0.1)
            
        total_spent = bid_death + bid_mid + bid_dom + bid_spin + bid_pacer + bid_reserve
        remaining_purse = 27.05 - total_spent
        
        st.markdown("---")
        res1, res2, res3 = st.columns(3)
        with res1:
            st.metric("Total Projected Spend", f"₹{total_spent:.2f} Cr")
        with res2:
            st.metric("Remaining Emergency Buffer", f"₹{remaining_purse:.2f} Cr")
        with res3:
            if remaining_purse >= 10.0:
                st.success("🟢 100% SOLVENT (Comfortable Surplus)")
            elif remaining_purse >= 5.0:
                st.warning("🟡 SOLVENT (Moderate Buffer)")
            elif remaining_purse >= 0.0:
                st.info("🟠 TIGHT (Zero Safety Net)")
            else:
                st.error("🔴 DEFICIT (Over Budget)")


elif page == "📈 What is Pressure?":

    st.markdown("### Match Pressure Explorer")
    st.markdown("""
    Explore how win probability and leverage fluctuate delivery by delivery in any match. 
    **High-pressure deliveries (top 25% leverage)** are shaded in pink, illustrating precisely which crunch moments count toward a player's pressure score.
    """)
    
    # Filter matches with at least 15 high-pressure deliveries
    valid_matches = df_enriched.groupby('match_id').agg({
        'is_high_pressure': 'sum',
        'comp_name': 'first',
        'result': 'first',
        'match_date': 'first'
    }).reset_index()
    valid_matches = valid_matches[valid_matches['is_high_pressure'] >= 15].sort_values('is_high_pressure', ascending=False)
    
    match_options = {
        m['match_id']: f"{m['comp_name']} | {m['result']} ({int(m['is_high_pressure'])} pressure balls)"
        for _, m in valid_matches.iterrows()
    }
    
    selected_match_id = st.selectbox(
        "Select a Match to Inspect:",
        options=list(match_options.keys()),
        format_func=lambda x: match_options[x]
    )
    
    m_data = df_enriched[df_enriched['match_id'] == selected_match_id].copy().sort_values(['innings', 'overid', 'innings_ball_num'])
    m_data['ball_seq'] = np.arange(len(m_data)) + 1
    
    # Match Summary KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Competition", str(m_data['comp_name'].iloc[0]))
    with c2:
        st.metric("Total Balls", len(m_data))
    with c3:
        st.metric("High-Pressure Balls", int(m_data['is_high_pressure'].sum()))
    with c4:
        st.metric("Result", str(m_data['result'].iloc[0]))
        
    # Plotly Match Worm with Pressure Shading
    fig_worm = go.Figure()
    
    # Base WP Line
    fig_worm.add_trace(go.Scatter(
        x=m_data['ball_seq'],
        y=m_data['wp_batting_team'],
        mode='lines',
        name='Batting Team Win Probability',
        line=dict(color=RR_BLUE, width=2.5),
        hoverinfo='skip'
    ))
    
    # Normal Balls
    norm_m = m_data[~m_data['is_high_pressure']]
    fig_worm.add_trace(go.Scatter(
        x=norm_m['ball_seq'],
        y=norm_m['wp_batting_team'],
        mode='markers',
        name='Routine Delivery',
        marker=dict(color='#A0AEC0', size=5, opacity=0.6),
        customdata=np.stack([
            norm_m['innings'], norm_m['overid'], norm_m['over_ball_num'],
            norm_m['striker_name'], norm_m['bowler_name'], norm_m['delivery_runs'],
            norm_m['is_wicket'], norm_m['leverage_index']
        ], axis=-1),
        hovertemplate="<b>Inn %{customdata[0]} Ov %{customdata[1]}.%{customdata[2]}</b><br>" +
                      "Batter: %{customdata[3]}<br>" +
                      "Bowler: %{customdata[4]}<br>" +
                      "Runs: %{customdata[5]} | Wicket: %{customdata[6]}<br>" +
                      "Leverage: %{customdata[7]:.3f}<br>" +
                      "Win Prob: %{y:.1%}<extra></extra>"
    ))
    
    # High Pressure Balls
    press_m = m_data[m_data['is_high_pressure']]
    fig_worm.add_trace(go.Scatter(
        x=press_m['ball_seq'],
        y=press_m['wp_batting_team'],
        mode='markers',
        name='High Pressure Delivery (Top 25% WPLI)',
        marker=dict(color=RR_PINK, size=10, symbol='diamond'),
        customdata=np.stack([
            press_m['innings'], press_m['overid'], press_m['over_ball_num'],
            press_m['striker_name'], press_m['bowler_name'], press_m['delivery_runs'],
            press_m['is_wicket'], press_m['leverage_index']
        ], axis=-1),
        hovertemplate="<b>🔥 HIGH PRESSURE DELIVEY</b><br>" +
                      "Inn %{customdata[0]} Ov %{customdata[1]}.%{customdata[2]}<br>" +
                      "Batter: %{customdata[3]}<br>" +
                      "Bowler: %{customdata[4]}<br>" +
                      "Runs: %{customdata[5]} | Wicket: %{customdata[6]}<br>" +
                      "Leverage: %{customdata[7]:.3f}<br>" +
                      "Win Prob: %{y:.1%}<extra></extra>"
    ))
    
    fig_worm.add_hline(y=0.5, line_dash="dash", line_color="#CBD5E1")
    fig_worm.update_layout(
        title="Ball-by-Ball Win Probability & Leverage Spikes",
        xaxis_title="Match Delivery Number",
        yaxis_title="Batting Team Win Probability",
        yaxis=dict(range=[-0.05, 1.05], tickformat=".0%"),
        template="plotly_white",
        height=480,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_worm, use_container_width=True)

# -------------------------------------------------------------
# PAGE 3: PLAYER PROFILE
# -------------------------------------------------------------
elif page == "👤 Player Profile":
    st.markdown("### Player Pressure Profile")
    
    role_choice = st.radio("Choose Role:", ["Batter", "Bowler"], horizontal=True)
    
    if role_choice == "Batter":
        player_list = all_batters['player_name'].dropna().unique().tolist()
        default_idx = player_list.index("Tim David") if "Tim David" in player_list else 0
        selected_player = st.selectbox("Select Batter:", player_list, index=default_idx)
        p_row = all_batters[all_batters['player_name'] == selected_player].iloc[0]
        
        # Header info
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Overall Pressure Rank", f"#{int(p_row['rank'])}")
        with c2:
            st.metric("Pressure Reliability Rating", f"{p_row['pressure_rating']:.2f}")
        with c3:
            st.metric("Pressure Deliveries", f"{int(p_row['press_balls'])} / {int(p_row['total_balls'])}")
        with c4:
            st.metric("Match Consistency", f"{p_row['consistency_pct']:.1f}%")
            
        st.markdown("---")
        
        # Side-by-side Normal vs Pressure Stats
        col_norm, col_press = st.columns(2)
        with col_norm:
            st.markdown("#### ⚪ Normal Match Situations")
            st.metric("Strike Rate", f"{p_row['norm_sr']:.1f}")
            st.metric("Dismissal Rate", f"{p_row['norm_dismissal_rate']:.1%}")
            st.metric("Total Runs", f"{int(p_row['norm_runs'])}")
            
        with col_press:
            st.markdown("#### 🔥 High-Pressure Situations")
            st.metric("Strike Rate", f"{p_row['press_sr']:.1f}", delta=f"{p_row['sr_delta']:+.1f} SR Delta")
            st.metric("Runs Over Expected", f"{p_row['press_roe']:+.1f} Runs")
            st.metric("Win Probability Added", f"{p_row['press_wpa']:+.2f} WPA")
            
        # Match-by-match impact bar chart
        st.markdown("#### Match-by-Match Pressure Performance (Green = Rose, Red = Dipped)")
        p_balls = df_enriched[(df_enriched['striker_name'] == selected_player) & (df_enriched['is_high_pressure']) & (df_enriched['is_legal_ball'])]
        match_impact = p_balls.groupby('match_id').agg({
            'runs_over_expected_batter': 'sum',
            'comp_name': 'first',
            'batter_runs': 'sum',
            'match_id': 'count'
        }).rename(columns={'match_id': 'balls'}).reset_index()
        
        if len(match_impact) > 0:
            match_impact['outcome'] = np.where(match_impact['runs_over_expected_batter'] >= 0, 'Positive Impact (Rose)', 'Negative Impact (Dipped)')
            match_impact['match_label'] = [f"Match {i+1}" for i in range(len(match_impact))]
            
            fig_bar = px.bar(
                match_impact, x='match_label', y='runs_over_expected_batter',
                color='outcome',
                color_discrete_map={'Positive Impact (Rose)': RR_SUCCESS, 'Negative Impact (Dipped)': RR_DANGER},
                custom_data=['comp_name', 'batter_runs', 'balls'],
                labels={'runs_over_expected_batter': 'Runs Over Context Expected', 'match_label': 'Match Sequence'}
            )
            fig_bar.update_traces(
                hovertemplate="<b>%{x}</b> (%{customdata[0]})<br>" +
                              "Runs: %{customdata[1]} off %{customdata[2]} balls<br>" +
                              "Runs Over Expected: %{y:+.1f}<extra></extra>"
            )
            fig_bar.update_layout(template="plotly_white", height=320, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)
            
    else:
        player_list = all_bowlers['player_name'].dropna().unique().tolist()
        default_idx = player_list.index("Sunil Narine") if "Sunil Narine" in player_list else 0
        selected_player = st.selectbox("Select Bowler:", player_list, index=default_idx)
        p_row = all_bowlers[all_bowlers['player_name'] == selected_player].iloc[0]
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Overall Pressure Rank", f"#{int(p_row['rank'])}")
        with c2:
            st.metric("Pressure Reliability Rating", f"{p_row['pressure_rating']:.2f}")
        with c3:
            st.metric("Pressure Deliveries", f"{int(p_row['press_balls'])} / {int(p_row['total_balls'])}")
        with c4:
            st.metric("Match Consistency", f"{p_row['consistency_pct']:.1f}%")
            
        st.markdown("---")
        
        col_norm, col_press = st.columns(2)
        with col_norm:
            st.markdown("#### ⚪ Normal Match Situations")
            st.metric("Economy Rate (RPO)", f"{p_row['norm_economy']:.2f}")
            st.metric("Dot Ball %", f"{p_row['norm_dot_pct']:.1f}%")
            st.metric("Wickets", f"{int(p_row['norm_wickets'])}")
            
        with col_press:
            st.markdown("#### 🔥 High-Pressure Situations")
            st.metric("Economy Rate (RPO)", f"{p_row['press_economy']:.2f}", delta=f"{p_row['economy_delta']:+.2f} RPO Improved")
            st.metric("Runs Saved vs Expected", f"{p_row['press_runs_saved']:+.1f} Runs")
            st.metric("Pressure Wickets", f"{int(p_row['press_wickets'])} Wickets")
            
        st.markdown("#### Match-by-Match Pressure Performance (Green = Rose, Red = Dipped)")
        p_balls = df_enriched[(df_enriched['bowler_name'] == selected_player) & (df_enriched['is_high_pressure']) & (df_enriched['is_legal_ball'])]
        match_impact = p_balls.groupby('match_id').agg({
            'runs_saved_bowler': 'sum',
            'comp_name': 'first',
            'bowler_runs_conceded': 'sum',
            'is_bowler_wicket': 'sum',
            'match_id': 'count'
        }).rename(columns={'match_id': 'balls'}).reset_index()
        
        if len(match_impact) > 0:
            match_impact['outcome'] = np.where(match_impact['runs_saved_bowler'] >= 0, 'Positive Impact (Rose)', 'Negative Impact (Dipped)')
            match_impact['match_label'] = [f"Match {i+1}" for i in range(len(match_impact))]
            
            fig_bar = px.bar(
                match_impact, x='match_label', y='runs_saved_bowler',
                color='outcome',
                color_discrete_map={'Positive Impact (Rose)': RR_SUCCESS, 'Negative Impact (Dipped)': RR_DANGER},
                custom_data=['comp_name', 'bowler_runs_conceded', 'is_bowler_wicket', 'balls'],
                labels={'runs_saved_bowler': 'Runs Saved vs Context Expected', 'match_label': 'Match Sequence'}
            )
            fig_bar.update_traces(
                hovertemplate="<b>%{x}</b> (%{customdata[0]})<br>" +
                              "Figures: %{customdata[2]}/%{customdata[1]} in %{customdata[3]} balls<br>" +
                              "Runs Saved: %{y:+.1f}<extra></extra>"
            )
            fig_bar.update_layout(template="plotly_white", height=320, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------------------------------------
# PAGE 4: COMPARE PLAYERS
# -------------------------------------------------------------
elif page == "⚔️ Compare Players":
    st.markdown("### Head-to-Head Player Comparison")
    
    role = st.radio("Select Role:", ["Batters", "Bowlers"], horizontal=True)
    
    if role == "Batters":
        col1, col2 = st.columns(2)
        with col1:
            p1 = st.selectbox("Player 1:", all_batters['player_name'].dropna().unique(), index=0)
        with col2:
            p2 = st.selectbox("Player 2:", all_batters['player_name'].dropna().unique(), index=1)
            
        r1 = all_batters[all_batters['player_name'] == p1].iloc[0]
        r2 = all_batters[all_batters['player_name'] == p2].iloc[0]
        
        comp_df = pd.DataFrame({
            "Metric": [
                "Pressure Rating", "Pressure Balls Faced", "Normal Strike Rate", "Pressure Strike Rate",
                "Strike Rate Delta (Δ)", "Runs Over Expected (ROE)", "Win Probability Added (WPA)", "Consistency %"
            ],
            f"{p1}": [
                f"{r1['pressure_rating']:.2f}", f"{int(r1['press_balls'])}", f"{r1['norm_sr']:.1f}", f"{r1['press_sr']:.1f}",
                f"{r1['sr_delta']:+.1f}", f"{r1['press_roe']:+.1f}", f"{r1['press_wpa']:+.2f}", f"{r1['consistency_pct']:.1f}%"
            ],
            f"{p2}": [
                f"{r2['pressure_rating']:.2f}", f"{int(r2['press_balls'])}", f"{r2['norm_sr']:.1f}", f"{r2['press_sr']:.1f}",
                f"{r2['sr_delta']:+.1f}", f"{r2['press_roe']:+.1f}", f"{r2['press_wpa']:+.2f}", f"{r2['consistency_pct']:.1f}%"
            ]
        })
        st.table(comp_df)
        
    else:
        col1, col2 = st.columns(2)
        with col1:
            p1 = st.selectbox("Player 1:", all_bowlers['player_name'].dropna().unique(), index=0)
        with col2:
            p2 = st.selectbox("Player 2:", all_bowlers['player_name'].dropna().unique(), index=1)
            
        r1 = all_bowlers[all_bowlers['player_name'] == p1].iloc[0]
        r2 = all_bowlers[all_bowlers['player_name'] == p2].iloc[0]
        
        comp_df = pd.DataFrame({
            "Metric": [
                "Pressure Rating", "Pressure Balls Bowled", "Normal Economy", "Pressure Economy",
                "Economy Delta (Δ)", "Pressure Wickets", "Runs Saved vs Context", "Win Probability Added (WPA)", "Consistency %"
            ],
            f"{p1}": [
                f"{r1['pressure_rating']:.2f}", f"{int(r1['press_balls'])}", f"{r1['norm_economy']:.2f}", f"{r1['press_economy']:.2f}",
                f"{r1['economy_delta']:+.2f}", f"{int(r1['press_wickets'])}", f"{r1['press_runs_saved']:+.1f}", f"{r1['press_wpa']:+.2f}", f"{r1['consistency_pct']:.1f}%"
            ],
            f"{p2}": [
                f"{r2['pressure_rating']:.2f}", f"{int(r2['press_balls'])}", f"{r2['norm_economy']:.2f}", f"{r2['press_economy']:.2f}",
                f"{r2['economy_delta']:+.2f}", f"{int(r2['press_wickets'])}", f"{r2['press_runs_saved']:+.1f}", f"{r2['press_wpa']:+.2f}", f"{r2['consistency_pct']:.1f}%"
            ]
        })
        st.table(comp_df)

# -------------------------------------------------------------
# PAGE 5: TRUST & SENSITIVITY
# -------------------------------------------------------------
elif page == "🛡️ Trust & Sensitivity":
    st.markdown("### Model Trust, Reliability & Sensitivity")
    st.markdown("""
    Trust is established through rigorous validation, not reputation. 
    Below, explore how rankings behave under different mathematical definitions of pressure and sample volume cutoffs.
    """)
    
    st.markdown("#### Interactive Sensitivity Explorer")
    col_def, col_vol = st.columns(2)
    with col_def:
        press_def = st.selectbox(
            "Pressure Definition:",
            [
                "Win Probability Leverage Index (WPLI - Primary)",
                "Contextual Tension Index (CTI - Alt 1)",
                "Late Close Filter (LCF - Alt 2)"
            ]
        )
    with col_vol:
        min_balls = st.slider("Minimum Pressure Deliveries Threshold:", min_value=40, max_value=90, value=60, step=10)
        
    def_col_map = {
        "Win Probability Leverage Index (WPLI - Primary)": "is_high_pressure_wpli",
        "Contextual Tension Index (CTI - Alt 1)": "is_high_pressure_cti",
        "Late Close Filter (LCF - Alt 2)": "is_high_pressure_lcf"
    }
    
    chosen_col = def_col_map[press_def]
    
    # Dynamically re-compute on the fly
    dynamic_batters = compute_batter_ratings(df_enriched, pressure_col=chosen_col, min_pressure_balls=min_balls)
    dynamic_bowlers = compute_bowler_ratings(df_enriched, pressure_col=chosen_col, min_pressure_balls=min_balls)
    
    st.markdown(f"**Top 5 Under `{press_def}` (Min {min_balls} Balls):**")
    c_b, c_bw = st.columns(2)
    with c_b:
        st.markdown("**Top 5 Batters**")
        st.dataframe(dynamic_batters[['rank', 'player_name', 'pressure_rating', 'press_balls', 'press_sr', 'sr_delta']].head(5), hide_index=True)
    with c_bw:
        st.markdown("**Top 5 Bowlers**")
        st.dataframe(dynamic_bowlers[['rank', 'player_name', 'pressure_rating', 'press_balls', 'press_economy', 'economy_delta']].head(5), hide_index=True)
        
    st.markdown("---")
    st.markdown("#### Quantitative Reliability Benchmarks")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Bootstrap Resamples", "500 Iterations", help="Empirical resampling of delivery outcomes")
    with m2:
        st.metric("Split-Half Reliability", "Odd vs Even Matches", help="Cross-validated match partition correlation")
    with m3:
        st.metric("Empirical Bayes Prior Weight", "K = 30 Balls", help="Shrinkage parameter towards league mean")
