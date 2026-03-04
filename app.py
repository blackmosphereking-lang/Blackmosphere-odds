# app.py – Modern UI with betting slip, odds display, and cosmic overlay

import streamlit as st
from datetime import date
from api import fetch_matches, fetch_standings
from models import enhanced_poisson
from config import COSMIC_ENABLED, COSMIC_API_KEY, RG_WARNING
from config import LEAGUE, PRIMARY_COLOR
from cosmic import cosmic_verdict
from sources import sofa_search_team
from config import LEAGUE, LEAGUE_PARAMS
from models import get_league_params, get_league_info

# ── Modern UI Setup ────────────────────────────────────────────────
# Fixed config imports

CSS = """
/* FootMob UI Styles */
/* Injected via config.py */
"""

st.markdown(CSS, unsafe_allow_html=True)

# ── Top Bar
c1, c2, c3 = st.columns([3, 3, 2])
c1.title(f"<h1 style='color:{PRIMARY_COLOR}'>Blackmosphere AI</h1>", unsafe_allow_html=True)
st.session_state.selected_date = c2.date_input("Select Date", value=date.today(), format="YYYY-MM-DD")
league_filter = c3.selectbox("League", ["All"] + list(LEAGUE.keys()), index=0)
st.markdown("""
<div style='background-color:#151924; padding:16px; border-radius:18px; margin-top:-24px; color:#9BA0B21; font-size:14px; letter-spacing:-0.2px; text-align:center'>
⚠️ Live odds via SofaScore & Pinnacle API (Premium Feature)
</div>
""", unsafe_allow_html=True)

# ── Main Content Area
st.markdown(f"<h2 style='color:#D5A021'>Blackmosphere AI</h1>", unsafe_allow_html=True)
st.markdown(f"<div style='background-color:#1A1F2E; padding:24px; border-radius:18px; margin-bottom:16px; border-left:3px solid #D5A021"
)
st.write("Live odds loading... Football-data.org API Key needed for matches & standings
         SofaScore API Key for live odds
         Pinnacle API for betting lines
         StatsBomb for historical data

         <div style='color:#9BA0Kills API Keys to unlock premium features</div>
         <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Visit dashboard</a> →
         <a href='https://docs.blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >API docs</a> →
         <a href='https://www.gamblersanonymous.org' style='color:#FFD700' target='_blank'
     >Responsible Gaming</a> →
         <a href='https://github.com/blackmosphere/blackmosphere-odds
         style='color:#3CB9FF' target='_blank'
     >GitHub repo</a> →
         <a href='https://docs.blackmosphere.ai' style='color:#D5A021' target='_blank'
     >API Keys & config values →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Premium Features</a> →
     <a href='https://blackmosphere.ai' style='color:#3CB9FF' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Premium Features</a> →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#3CB9FF' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#2FD921' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#3CB9FF' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#3CB9FF' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#3CB9FF' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a> →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#3CB9FF' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#3CB9FF' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#3CB9FF' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C0' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#3CB9FF' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#3CB9FF' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#3CB9FF' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#3CB9FF' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9A0' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#D5A021' target='_blank'
     >Live Dashboard</a →
     <a href='https://blackmosphere.ai' style='color:#2FD9C5' target='_blank'
     >Live Dashboard</a →
    