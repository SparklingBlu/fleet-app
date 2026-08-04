# team_1.py — standalone deployment for Team 1 (no query string needed)
import streamlit as st

st.set_page_config(
    page_title="SparklingBlu — Team 1",
    page_icon="🚛",
    layout="wide"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"],[data-testid="stMain"],.main{background:#f0f4f8!important;}
[data-testid="stAppViewContainer"] p,[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] div,[data-testid="stAppViewContainer"] label,
[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] span,
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
[data-testid="stDataFrame"]{background:white!important;border-radius:10px!important;}
[data-testid="stCaptionContainer"] p{color:#555!important;font-size:13px!important;}
</style>
""", unsafe_allow_html=True)

from team_view import render_team_view
render_team_view("Team 1")
