import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import requests
from datetime import datetime, timedelta

# --- PWA & THEME CONFIGURATION (STEP 2 INCORPORATED) ---
st.set_page_config(page_title="Blackmosphere Gold", page_icon="🏆", layout="wide")

# This block links the manifest.json and sets mobile browser behavior
st.markdown(
    """
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#D4AF37">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <style>
        /* Main Background */
        .stApp {
            background-color: #000000;
            background-image: radial-gradient(circle at 50% -20%, #1a1a1a, #000000);
        }
        /* Gold Headers */
        h1, h2, h3 {
            color: #D4AF37 !important;
            text-shadow: 0px 0px 15px rgba(212, 175, 55, 0.3);
        }
        /* Gold Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #D4AF37 0%, #AA8418 100%) !important;
            color: #000 !important;
            border: none !important;
            font-weight: bold !important;
            width: 100%;
        }
        /* Metric Cards */
        [data-testid="stMetric"] {
            background: rgba(212, 175, 55, 0.05) !important;
            border: 1px solid #D4AF37 !important;
            padding: 15px !important;
            border-radius: 10px !important;
        }
        .stMarkdown, p, span { color: #e0e0e0 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- API CONFIGURATION ---
API_KEY = st.secrets["FOOTBALL_API_KEY"] if "FOOTBALL_API_KEY" in st.secrets else "7ab0a5f50ad043559bb77700e966fe78"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY, 'Accept-Encoding': ''}

# [span_0](start_span)[span_1](start_span)League mapping (Includes fix for 'Primera Division' crash)[span_0](end_span)[span_1](end_span)
LEAGUE_CODES = {
    'Premier League': 'PL', 'Bundesliga': 'BL1', 'Serie A': 'SA',
    'La Liga': 'PD', 'Primera Division': 'PD', 'Ligue 1': 'FL1',
    'Eredivisie': 'DED'
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
                  'status': 'SCHEDULED'}
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get('matches', [])
    except:
        return []

def predict_match_outcome(league_name, home_strength=1.0, away_strength=1.0):
    # [span_2](start_span)Safety lookup to prevent the crash seen in your logs[span_2](end_span)
    api_code = LEAGUE_CODES.get(league_name, 'PL')
    params = fallback_league_params.get(api_code, fallback_league_params['PL'])
    
    avg_goals = params['xg_per_match'] / 2
    h_lambda = avg_goals * home_strength * np.exp(params['home_adv_goals']/2) / away_strength
    a_lambda = avg_goals * away_strength / (home_strength * np.exp(params['home_adv_goals']/2))

    max_goals = 8
    h_goals = np.arange(max_goals)
    a_goals = np.arange(max_goals)
    p_h_dist = poisson.pmf(h_goals, h_lambda)
    p_a_dist = poisson.pmf(a_goals, a_lambda)
    prob_matrix = np.outer(p_h_dist, p_a_dist)

    p_home = np.sum(np.tril(prob_matrix, -1))
    p_draw = np.sum(np.diag(prob_matrix))
    p_away = np.sum(np.triu(prob_matrix, 1))
    
    return {
        'home': p_home, 'draw': p_draw, 'away': p_away,
        'h_odds': 1/p_home if p_home > 0 else 100,
        'btts': np.sum(prob_matrix[1:, 1:])
    }

# --- UI START ---
st.markdown("<h1 style='text-align: center;'>🏆 BLACKMOSPHERE GOLD</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #D4AF37;'>PREMIUM SPORTS PREDICTION ENGINE</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔮 Predictor", "⚽ Live Matches", "🎯 Parlay"])

if 'parlay' not in st.session_state:
    st.session_state.parlay = []

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        l_choice = st.selectbox("League Selection", list(LEAGUE_CODES.keys()))
        h_s = st.slider("Home Advantage", 0.5, 2.5, 1.0)
    with col2:
        a_s = st.slider("Away Threat", 0.5, 2.5, 1.0)
    
    if st.button("CALCULATE PROBABILITY"):
        res = predict_match_outcome(l_choice, h_s, a_s)
        c1, c2, c3 = st.columns(3)
        c1.metric("HOME WIN", f"{res['home']:.1%}")
        c2.metric("DRAW", f"{res['draw']:.1%}")
        c3.metric("AWAY WIN", f"{res['away']:.1%}")
        
        if st.button("ADD TO GOLD TICKET"):
            st.session_state.parlay.append({'name': f"{l_choice} Bet", 'odds': res['h_odds']})
            st.success("Leg added to parlay.")

with tab2:
    matches = fetch_live_matches()
    if not matches:
        st.info("Searching for upcoming fixtures...")
    for m in matches[:8]:
        with st.container():
            st.markdown(f"**{m['homeTeam']['name']} vs {m['awayTeam']['name']}**")
            if st.button("Analyze Match", key=f"btn_{m['id']}"):
                res = predict_match_outcome(m['competition']['name'])
                st.write(f"Probabilities: H:{res['home']:.1%} | D:{res['draw']:.1%} | A:{res['away']:.1%}")

with tab3:
    st.markdown("### 🎯 YOUR GOLD TICKET")
    total_odds = 1.0
    for i, item in enumerate(st.session_state.parlay):
        st.write(f"🔸 {item['name']} - {item['odds']:.2f}")
        total_odds *= item['odds']
    
    if st.session_state.parlay:
        st.divider()
        st.markdown(f"## TOTAL ODDS: {total_odds:,.2f}")
        if st.button("CLEAR TICKET"):
            st.session_state.parlay = []
            st.rerun()
