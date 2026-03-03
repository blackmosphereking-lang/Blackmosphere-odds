import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import requests
from datetime import datetime, timedelta

# --- PWA & THEME CONFIGURATION ---
st.set_page_config(page_title="Blackmosphere Gold", page_icon="🏆", layout="wide")

st.markdown(
    """
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#D4AF37">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <style>
        .stApp { background-color: #000000; background-image: radial-gradient(circle at 50% -20%, #1a1a1a, #000000); }
        h1, h2, h3 { color: #D4AF37 !important; text-shadow: 0px 0px 15px rgba(212, 175, 55, 0.3); }
        .stButton>button { background: linear-gradient(135deg, #D4AF37 0%, #AA8418 100%) !important; color: #000 !important; font-weight: bold !important; width: 100%; border: none !important; }
        [data-testid="stMetric"] { background: rgba(212, 175, 55, 0.05) !important; border: 1px solid #D4AF37 !important; border-radius: 10px !important; }
        .stMarkdown, p, span { color: #e0e0e0 !important; }
        .stTabs [aria-selected="true"] { color: #D4AF37 !important; border-bottom-color: #D4AF37 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SECURE API CONFIGURATION ---
# This version pulls the key from your Streamlit Dashboard Secrets for safety
try:
    API_KEY = st.secrets["FOOTBALL_API_KEY"]
except KeyError:
    st.error("⚠️ API Key not found in Secrets. Please add 'FOOTBALL_API_KEY' to your Streamlit Cloud settings.")
    st.stop()

BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY, 'Accept-Encoding': ''}

LEAGUE_CODES = {
    'Premier League': 'PL', 'Bundesliga': 'BL1', 'Serie A': 'SA',
    'La Liga': 'PD', 'Primera Division': 'PD', 'Ligue 1': 'FL1', 'Eredivisie': 'DED'
}

fallback_league_params = {
    'PL': {'home_adv_goals': 0.32, 'xg_per_match': 2.85},
    'BL1': {'home_adv_goals': 0.45, 'xg_per_match': 3.25},
    'SA': {'home_adv_goals': 0.35, 'xg_per_match': 2.45},
    'PD': {'home_adv_goals': 0.38, 'xg_per_match': 2.60},
    'FL1': {'home_adv_goals': 0.33, 'xg_per_match': 2.75},
    'DED': {'home_adv_goals': 0.42, 'xg_per_match': 3.40}
}

@st.cache_data(ttl=600)
def fetch_live_matches():
    try:
        url = f"{BASE_URL}/matches"
        params = {'dateFrom': datetime.now().strftime('%Y-%m-%d'), 
                  'dateTo': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                  'status': 'SCHEDULED
