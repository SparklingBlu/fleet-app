# app_drivers.py — SparklingBlu Fleet Management System
# PUBLIC VIEWS: drivers | team
# Reads published data from GitHub Gist — no admin access, no API calls
# note: the password-protected Management/Fleet view lives in app_management.py,
# deployed as a SEPARATE Streamlit Cloud app. Do not add a "fleet" view here.

import streamlit as st
import pandas as pd
from datetime import datetime
from storage import load_fleet_data

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SparklingBlu — Driver Performance",
    page_icon="🚛",
    layout="wide"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"],[data-testid="stMain"],.main{background:#f0f4f8!important;}
[data-testid="stAppViewContainer"] p,[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] div,[data-testid="stAppViewContainer"] label,
[data-testid="stMarkdownContainer"] p,[data-testdata="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li{color:#0f2027!important;}
h1,h2,h3{color:#0f2027!important;}
[data-testid="stMetric"]{background:white!important;border-radius:14px!important;
  padding:18px 22px!important;text-align:center!important;
  box-shadow:0 2px 10px rgba(0,0,0,.10)!important;}
[data-testid="stMetricLabel"]>div{font-size:12px!important;font-weight:800!important;
  color:#203a43!important;text-transform:uppercase!important;letter-spacing:.6px!important;}
[data-testid="stMetricValue"]>div{font-size:32px!important;font-weight:900!important;
  color:#0f2027!important;}
[data-testid="stAlert"] p,[data-testid="stAlert"] span{color:#0f2027!important;}
[data-testid="stTextInput"] input{background:white!important;color:#0f2027!important;
  border:1.5px solid #2c5364!important;border-radius:8px!important;}
[data-testid="stTextInput"] label,[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label,[data-testid="stFileUploader"] label{
  color:#0f2027!important;font-weight:600!important;}
[data-testid="stCaptionContainer"] p{color:#555!important;font-size:13px!important;}
[data-testid="stDataFrame"]{background:white!important;border-radius:10px!important;}
[data-testid="stExpander"] summary p{color:#0f2027!important;font-weight:600!important;}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
BASE_URL = "https://sparklingblu-public.streamlit.app"

# ── HELPERS ───────────────────────────────────────────────────────────────────
def date_only():
    return datetime.now().strftime("%d %b %Y")

def insight_html(text):
    return (
        f'<div style="background:white;border-radius:12px;padding:14px 18px;'
        f'box-shadow:0 2px 8px rgba(0,0,0,.07);margin-bottom:10px;'
        f'font-size:15px;color:#0f2027;">{text}</div>'
    )

# ── ROUTE ─────────────────────────────────────────────────────────────────────
params     = st.query_params
view       = params.get("view", "drivers")
team_param = params.get("team", None)


# ════════════════════════════════════════════════════════
# DRIVERS VIEW
# ════════════════════════════════════════════════════════
if view == "drivers":
    data = load_fleet_data()
    st.markdown("# 🚛 SparklingBlu — Your Weekly Stats")

    if not data:
        st.warning("Stats not available yet. Ask your fleet manager to publish this week's data.")
        st.stop()

    df      = pd.DataFrame(data["fleet"])
    updated = data.get("updated_at", "")

    st.markdown(f"*Updated: {updated}*")
    st.divider()

    search = st.text_input("Type your name:", placeholder="e.g. John Msosa")
    if not search:
        st.info("Start typing your name above to see your stats.")
        st.stop()

    matches = df[df["Driver"].str.lower().str.contains(search.strip().lower(), na=False)]
    if matches.empty:
        st.warning("No driver found. Try a different spelling.")
        st.stop()
    if len(matches) > 1:
        choice  = st.selectbox("Multiple matches — select your name:", matches["Driver"].tolist())
        matches = matches[matches["Driver"] == choice]

    row = matches.iloc[0]

    st.markdown(f"""
    <div style="background:white;border-radius:16px;padding:28px 32px;
                box-shadow:0 4px 20px rgba(0,0,0,.10);margin-bottom:18px;">
        <h2 style="margin:0 0 4px 0;color:#0f2027;">👤 {row['Driver']}</h2>
        <p style="color:#555;margin:0 0 20px 0;font-size:15px;">
            Hotspot: {row.get('Hotspot', '—')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Your Stats This Period")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("⏱️ Hours Online",   f"{row.get('Hours Online',  '—')}h")
    k2.metric("🚗 Hours on Trip",  f"{row.get('Hours on Trip', '—')}h")
    k3.metric("📦 Total Trips",     str(row.get("Total Trips",  "—")))
    k4.metric("⭐ Score",           f"{row.get('Score', '—')}%")

    st.divider()
    
    st.markdown(f"**Status:** {row.get('Status', '—')}")
    st.info(row.get('Coaching', 'No coaching available yet.'))
    
    st.divider()
    st.caption(f"SparklingBlu Fleet Team 🚛  |  Updated: {updated}")

# ════════════════════════════════════════════════════════
# TEAM VIEW
# ════════════════════════════════════════════════════════
elif view == "team":
    data = load_fleet_data()

    if not data:
        st.warning("No data available. Ask the fleet manager to publish this week's stats.")
        st.stop()

    df      = pd.DataFrame(data["fleet"])
    updated = data.get("updated_at", "")

    # Get team names from data
    available_teams = df["Team"].unique().tolist() if "Team" in df.columns else []

    selected_team = (
        team_param if team_param and team_param in available_teams
        else st.selectbox("Select your team:", available_teams) if available_teams
        else None
    )

    if not selected_team:
        st.warning("No teams found in the current data.")
        st.stop()

    team_df = df[df["Team"] == selected_team].copy()

    st.markdown(f"# 👥 {selected_team} — Weekly Performance")
    st.markdown(f"*Updated: {updated}*")
    st.divider()

    if team_df.empty:
        st.warning("No drivers found for this team in the current data.")
        st.stop()

    t_total   = len(team_df)
    t_avg_hrs = round(team_df["Hours Online"].astype(float).mean(), 1) if "Hours Online" in team_df.columns else "—"
    t_avg_trp = round(team_df["Total Trips"].astype(float).mean(),  1) if "Total Trips"  in team_df.columns else "—"
    t_avg_score = round(team_df["Score"].mean(), 1) if "Score" in team_df.columns else "—"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Team Size",        t_total)
    m2.metric("Avg Hours Online", f"{t_avg_hrs}h")
    m3.metric("Avg Trips",        t_avg_trp)
    m4.metric("Avg Score",        f"{t_avg_score}%")

    st.divider()

    show_cols = ["Driver", "Hours Online", "Hours on Trip", "Total Trips", "Score", "Status", "Coaching"]
    show_cols = [c for c in show_cols if c in team_df.columns]
    st.dataframe(
        team_df[show_cols].sort_values("Score", ascending=False).reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"SparklingBlu Fleet  |  Updated: {updated}")

else:
    st.warning("Please use the link provided by your fleet manager.")