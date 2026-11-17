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
    st.markdown("### 👑 Rajasthan Royals War Room: IPL 2027 Auction Blueprint")
    st.markdown("""
    **Translating Data Science into Silverware:** This module connects our ball-by-ball pressure ratings directly to 
    **Rajasthan Royals' tactical requirements for the IPL 2027 Auction**. By analyzing 76 historical RR matches in the dataset, 
    we identify key squad vulnerabilities and target the exact statistical profiles needed to build a champion team.
    """)
    
    # Download Deliverables Section
    st.markdown("#### 📥 Download Submission Artifacts")
    cd1, cd2, cd3 = st.columns(3)
    with cd1:
        with open("outputs/report.pdf", "rb") as f:
            st.download_button(
                label="📄 Download Methodology Report (PDF)",
                data=f,
                file_name="RR_SupeRR_Selector_Methodology_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    with cd2:
        with open("outputs/report.docx", "rb") as f:
            st.download_button(
                label="📝 Download Methodology Report (DOCX)",
                data=f,
                file_name="RR_SupeRR_Selector_Methodology_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
    with cd3:
        with open("outputs/rr_auction_presentation.pptx", "rb") as f:
            st.download_button(
                label="📊 Download War Room Presentation (PPTX)",
                data=f,
                file_name="RR_IPL2027_Auction_Strategy_Presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
            )
            
    st.markdown("---")
    
    # 3 Strategic Pillars
    st.markdown("#### 🎯 Rajasthan Royals Tactical Audit & Key Gaps")
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid {RR_PINK};">
            <div class="metric-title">Critical Need 1</div>
            <div class="metric-val" style="font-size: 1.3rem;">Death-Overs Power Finisher</div>
            <p style="font-size: 0.85rem; color: #475569; margin-top: 8px;">
                Shimron Hetmyer generated <b>-31.5 Runs Over Expected</b> under pressure for RR. With Jos Buttler gone, 
                RR needs an elite overseas assassin to finish tight chases.
            </p>
            <span class="badge-pink">Target: Tim David / Josh Inglis</span>
        </div>
        """, unsafe_allow_html=True)
    with g2:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid {RR_BLUE};">
            <div class="metric-title">Critical Need 2</div>
            <div class="metric-val" style="font-size: 1.3rem;">Spin Choke Succession</div>
            <p style="font-size: 0.85rem; color: #475569; margin-top: 8px;">
                Yuzvendra Chahal (25 pressure wkts) and R Ashwin (17 wkts) anchored RR's middle overs. RR must secure 
                a world-class spin choke to control overs 10-16.
            </p>
            <span class="badge-blue">Target: Sunil Narine / Sufiyan Muqeem</span>
        </div>
        """, unsafe_allow_html=True)
    with g3:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid {RR_GOLD};">
            <div class="metric-title">Critical Need 3</div>
            <div class="metric-val" style="font-size: 1.3rem;">145+ km/h Express Death Pace</div>
            <p style="font-size: 0.85rem; color: #475569; margin-top: 8px;">
                While Sandeep Sharma provides elite medium-pace variations, RR lacks raw express intimidation 
                to blow away lower orders at the death.
            </p>
            <span style="background-color: {RR_GOLD}; color: black; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">Target: Riley Meredith / Mayank Yadav</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # In-House Crown Jewel: Vaibhav Sooryavanshi
    st.markdown("#### 💎 Crown Jewel Case Study: Maximizing Vaibhav Sooryavanshi")
    col_v1, col_v2 = st.columns([1.5, 2.5])
    with col_v1:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, {RR_BLUE} 0%, #1B3B6F 100%); color: white;">
            <div style="color: {RR_GOLD}; font-size: 0.9rem; font-weight: bold;">RR IN-HOUSE ASSET</div>
            <div style="color: white; font-size: 1.8rem; font-weight: 800; margin: 4px 0;">Vaibhav Sooryavanshi</div>
            <div style="color: {RR_PINK}; font-size: 1.1rem; font-weight: bold;">Rank #3 Overall Batter (Rating: 73.40)</div>
            <hr style="border-color: rgba(255,255,255,0.2); margin: 12px 0;">
            <p style="font-size: 0.9rem; margin-bottom: 4px;">• <b>174 Pressure Balls</b> Faced (35 matches)</p>
            <p style="font-size: 0.9rem; margin-bottom: 4px;">• <b>213.8 Pressure Strike Rate</b></p>
            <p style="font-size: 0.9rem; margin-bottom: 4px;">• <b>+111.7 Runs Over Expected</b></p>
            <p style="font-size: 0.9rem;">• <b>+93.3 ROE specifically for RR</b></p>
        </div>
        """, unsafe_allow_html=True)
    with col_v2:
        st.markdown("""
        **Strategic Directive for Franchise Leadership:**
        1. **Locked-In Opening Dynamo:** Pair Sooryavanshi with **Yashasvi Jaiswal** to forge the most destructive Left-Hand opening pair in IPL history.
        2. **Pressure Absorption for Samson:** His 213.8 strike rate dismantles opposition bowling in the Powerplay, completely releasing run-rate pressure from Sanju Samson at #3.
        3. **Purse Efficiency Multiplier:** Retaining Sooryavanshi at youth scale frees up massive purse resources (₹15–20 Cr) to dominate bidding for Tier 1 bowling cornerstones like Sunil Narine or Tim David.
        """)

    st.markdown("---")
    
    # Tiered Target Matrix
    st.markdown("#### 📋 IPL 2027 Tiered Auction Strategy Matrix")
    tab_t1, tab_t2, tab_t3 = st.tabs(["⭐ Tier 1: Marquee Cornerstones", "⚡ Tier 2: High-Value Specialists", "💡 Tier 3: Budget Steals"])
    
    with tab_t1:
        st.markdown("""
        | Target Player | Role | Pressure Score | Key Impact Metric | Recommended Max Bid | Tactical Rationale |
        |---|---|---|---|---|---|
        | **Tim David** | Finisher (#6/#7) | **76.74** | 188.6 SR (+134.5 ROE, +2.53 WPA) | ₹12–15 Cr | Absolute priority finisher to solve RR's death chase deficit. |
        | **Sunil Narine** | Mystery Spinner | **77.46** | 5.65 RPO (+157.3 Runs Saved, 100% Cons) | ₹12–16 Cr | The gold standard spin choke; provides 4 unassailable overs. |
        | **Kuldeep Yadav** | Wrist Spinner | **67.95** | 35 Wickets (+4.85 WPA, 89.8% Cons) | ₹10–13 Cr | Elite breakthrough spinner to replace Chahal's wicket threat. |
        """)
        
    with tab_t2:
        st.markdown("""
        | Target Player | Role | Pressure Score | Key Impact Metric | Recommended Max Bid | Tactical Rationale |
        |---|---|---|---|---|---|
        | **Josh Inglis** | WK / Middle Finisher | **72.98** | 183.5 SR (+98.8 ROE, 81.5% Cons) | ₹6–9 Cr | Supreme spin player; covers wicketkeeping and middle-order acceleration. |
        | **Riley Meredith** | Express Pacer | **73.79** | 6.08 RPO (+3.19 Econ Delta, 100% Cons) | ₹5–8 Cr | 145+ km/h express pace at death; partners Sandeep Sharma seamlessly. |
        | **Mayank Yadav** | Indian Tearaway | **65.63** | 7.47 RPO (10 Wickets in 110 Balls) | ₹6–9 Cr | Indian express speed; delivers unplayable thunderbolts to intimidate lower orders. |
        """)
        
    with tab_t3:
        st.markdown("""
        | Target Player | Role | Pressure Score | Key Impact Metric | Recommended Max Bid | Tactical Rationale |
        |---|---|---|---|---|---|
        | **Naman Dhir** | Indian Top/Middle | **73.01** | 183.9 SR (+63.6 ROE) | ₹3–5 Cr | High-ceiling young Indian batter capable of multiple batting orders. |
        | **Sameer Rizvi** | Spin Destroyer | **68.96** | 170.7 SR (+36.1 SR Delta) | ₹2–4 Cr | Destructive middle-overs spin hitter for Sawai Mansingh Stadium pitch conditions. |
        | **Sufiyan Muqeem** | Wrist Spinner | **74.28** | 3.74 RPO (+62.3 Runs Saved, 100% Cons) | ₹2–4 Cr | Breakout international wrist-spin sensation; huge upside at budget cost. |
        | **Ashutosh Sharma** | Clutch Finisher | **67.29** | 183.7 SR (+31.8 ROE) | ₹2–4 Cr | Proven domestic ice-in-veins finisher; excellent purse saver. |
        | **Ehsan Khan** | Spin Anchor | **65.74** | 5.45 RPO (100% Consistency) | ₹1–2 Cr | Extreme economy reliability at low auction commitment. |
        """)

# -------------------------------------------------------------
# PAGE 2: WHAT IS PRESSURE? (MATCH EXPLORER)
# -------------------------------------------------------------
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
