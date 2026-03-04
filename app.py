# app.py – Blackmosphere AI (FootMob Style)

import streamlit as st
from datetime import date, datetime
from typing import Dict, List, Optional
import pandas as pd
import math

# ──────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────────────────────────────────────

# Try to import optional modules, provide fallbacks if not available
try:
    from config import (
        FOOTBALL_DATA_API_KEY,
        LEAGUE_PARAMS,
        RG_WARNING,
        PRIMARY_COLOR,
        COSMIC_ENABLED
    )
except ImportError:
    # Fallback values if config is incomplete
    FOOTBALL_DATA_API_KEY = ""
    LEAGUE_PARAMS = {
        "PL": {"home_advantage": 1.4, "avg_goals": 2.7, "hha": 0.35},
        "PD": {"home_advantage": 1.3, "avg_goals": 2.5, "hha": 0.32},
        "BL1": {"home_advantage": 1.2, "avg_goals": 2.0, "hha": 0.28},
    }
    RG_WARNING = "⚠️ Gamble responsibly. Play within your means."
    PRIMARY_COLOR = "#D5A021"
    COSMIC_ENABLED = True

try:
    from api import fetch_matches, fetch_standings
except ImportError:
    # Fallback functions
    def fetch_matches(league_code: str, date_from: str, date_to: str) -> pd.DataFrame:
        return pd.DataFrame()
    def fetch_standings(league_code: str) -> pd.DataFrame:
        return pd.DataFrame()

try:
    from models import predict_match, kelly_stake
except ImportError:
    # Fallback function
    def predict_match(home: str, away: str, home_str: float = 1.0, away_str: float = 1.0) -> Dict:
        return {"home": 0.33, "draw": 0.33, "away": 0.34, "over25": 0.5, "btts": 0.5}
    def kelly_stake(prob: float, odds: float, bankroll: float, fraction: float = 0.25) -> float:
        return 0.0

try:
    from cosmic import cosmic_verdict
except ImportError:
    def cosmic_verdict(home: str, away: str, hs: float = 1.0, as_: float = 1.0, d=None) -> Dict:
        return {"pick": "⚖️ DRAW", "bias": 0.0, "confidence": 0.5}

# ──────────────────────────────────────────────────────────────────────────────
# UI CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Blackmosphere AI - FootMob Edition",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────────────────────────────────────
# CSS STYLES
# ──────────────────────────────────────────────────────────────────────────────

CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@600;700&display=swap" rel="stylesheet">
<style>
    body { background: radial-gradient(circle at 10% 20%, #0C0F17 40%, #080A10 90%); color: #E5E5E5; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Montserrat', sans-serif; letter-spacing: -0.5px; }
    .tag-pill { display: inline-block; padding: 4px 10px; border-radius: 999px; background: rgba(213, 160, 33, 0.12); color: #F5D59D; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; }
    .hero-card { background: linear-gradient(135deg, #151924 0%, #1C2132 100%); border-radius: 20px; padding: 28px; margin: 24px 0; border: 1px solid rgba(213, 160, 33, 0.35); box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45); position: relative; overflow: hidden; }
    .hero-card::after { content: ''; position: absolute; inset: -60px auto auto 60%; width: 340px; height: 340px; background: radial-gradient(circle, rgba(47, 217, 197, 0.28), transparent 62%); filter: blur(70px); }
    .hero-left h1 { font-size: 32px; font-weight: 700; margin: 0; background: linear-gradient(90deg, #FFF, #D5A021); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-meta { color: #9BA0B5; font-size: 14px; margin: 8px 0 16px 0; }
    .primary-btn { background: #D5A021; color: #0C0F17; font-weight: 700; border: none; border-radius: 999px; padding: 12px 26px; box-shadow: 0 12px 28px rgba(213, 160, 33, 0.40); cursor: pointer; transition: all 0.25s ease; }
    .primary-btn:hover { transform: translateY(-2px); }
    .ghost-btn { background: transparent; border: 1px solid rgba(255, 255, 255, 0.18); color: #E5E5E5; font-weight: 600; border-radius: 999px; padding: 12px 26px; cursor: pointer; }
    .league-section { background: rgba(213, 160, 33, 0.08); padding: 12px 18px; border-radius: 12px; margin: 32px 0 12px 0; font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 18px; text-transform: uppercase; }
    .match-card { background: linear-gradient(135deg, #151924 0%, #1A1F2E 100%); border-radius: 18px; padding: 24px; margin: 16px 0; border: 1px solid rgba(255, 255, 255, 0.06); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35); transition: transform 0.25s ease; }
    .match-card:hover { transform: translateY(-4px); border-color: rgba(213, 160, 33, 0.25); }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
    .clubs { display: flex; align-items: center; gap: 18px; font-weight: 700; font-size: 17px; }
    .crest { width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #1F2533, #2A3042); display: flex; align-items: center; justify-content: center; font-size: 24px; }
    .vs-pill { padding: 6px 14px; border-radius: 999px; background: #1C2132; font-size: 11px; font-weight: 700; text-transform: uppercase; color: #9BA0B5; }
    .prob-bar { flex: 1; height: 8px; background: #1F2435; border-radius: 999px; overflow: hidden; }
    .prob-bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #2FD9C5, #3CB9FF); transition: width 0.4s ease; }
    .market-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-top: 18px; }
    .market-card { background: #1A1F2E; border-radius: 14px; padding: 16px; border: 1px solid rgba(255, 255, 255, 0.05); }
    .market-card.cosmic { background: #231C2D; border: 1px solid rgba(255, 0, 255, 0.35); }
    .market-card h4 { font-size: 13px; font-weight: 700; text-transform: uppercase; color: #D5A021; margin: 0 0 10px 0; }
    .metric-row { display: flex; justify-content: space-between; margin: 6px 0; font-size: 13px; }
    .metric-row strong { color: white !important; font-weight: 700; }
    .card-actions { display: flex; gap: 12px; margin-top: 18px; }
    .responsible-banner { background: rgba(139, 0, 0, 0.85); color: #FFDADA; padding: 12px 18px; border-radius: 12px; margin-top: 32px; text-align: center; font-size: 13px; font-weight: 500; }
    .stButton > button { border-radius: 999px; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    .match-card { animation: fadeIn 0.35s ease backwards; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────

if "parlay" not in st.session_state:
    st.session_state.parlay = []
if "bankroll" not in st.session_state:
    st.session_state.bankroll = 1000.0
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()
if "show_cosmic" not in st.session_state:
    st.session_state.show_cosmic = True
if "league_filter" not in st.session_state:
    st.session_state.league_filter = "All"

# ──────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def add_to_parlay(market_name: str, odds: float, prob: float):
    st.session_state.parlay.append({
        "name": market_name,
        "odds": odds,
        "prob": prob,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    st.toast(f"Added: {market_name} @ {odds:.2f}", icon="🎯")

def get_team_strength(team_name: str, league: str) -> float:
    """Get team strength from standings or use default"""
    # Default strength based on team name length (pseudo-random but consistent)
    base = 1.0 + (len(team_name) % 10) / 20
    return round(base, 2)

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR - BET SLIP
# ──────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🎯 Gold Ticket")
    if st.session_state.parlay:
        total_odds = 1.0
        for leg in st.session_state.parlay:
            total_odds *= leg["odds"]
            st.markdown(f"🔸 {leg['name']}<br>**@{leg['odds']:.2f}**", unsafe_allow_html=True)
        st.divider()
        st.metric("Combined Odds", f"{total_odds:.2f}")
        stake = st.number_input("Stake ($)", 5.0, 10000.0, 25.0)
        if st.button("LOG BET", use_container_width=True, type="primary"):
            profit = stake * (total_odds - 1)
            st.success(f"Bet logged! Potential profit: ${profit:.2f}")
    else:
        st.info("No selections. Add markets from match cards.")
    
    st.divider()
    st.metric("Bankroll", f"${st.session_state.bankroll:,.2f}")
    
    st.divider()
    st.markdown("### ⚙️ Settings")
    st.session_state.show_cosmic = st.toggle("Cosmic Overlay", value=True)
    st.session_state.league_filter = st.selectbox(
        "League Filter",
        ["All", "Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1", "Champions League"]
    )

# ──────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT
# ──────────────────────────────────────────────────────────────────────────────

# Header
col1, col2, col3 = st.columns([3, 2, 1])
col1.markdown("<h1 style='margin:0'>⚽ Blackmosphere AI</h1>", unsafe_allow_html=True)
col2.date_input("Select Date", st.session_state.selected_date, key="date_picker")

# API Status
if not FOOTBALL_DATA_API_KEY:
    st.warning("⚠️ API Key not configured. Using demo data.")

# Hero Section - Featured Match
st.markdown("""
<div class="hero-card">
  <div class="hero-left">
    <span class="tag-pill">Featured Match</span>
    <h1>Manchester City vs Real Madrid</h1>
    <div class="hero-meta">
      <span>🏟️ Etihad Stadium</span> · <span>🕐 21:00 GMT</span> · <span>🌦️ 14°C</span>
    </div>
    <div>
      <button class="primary-btn">🏠 1.92</button>
      <button class="ghost-btn">🍔 3.80</button>
      <button class="ghost-btn">✈️ 3.60</button>
    </div>
  </div>
  <div style="text-align:right">
    <div style="font-size:22px;font-weight:700;color:#2FD9C5">Kickoff in 02h 17m</div>
    <div style="font-size:13px;color:#9BA0B5;margin-top:6px">Cosmic Signal: <strong>63%</strong></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# MATCH DATA (Demo fixtures)
# ──────────────────────────────────────────────────────────────────────────────

FIXTURES = [
    {"home": "Manchester City", "away": "Real Madrid", "league": "Champions League", "time": "21:00", "home_str": 1.65, "away_str": 1.45},
    {"home": "Arsenal", "away": "Bayern Munich", "league": "Champions League", "time": "19:45", "home_str": 1.42, "away_str": 1.38},
    {"home": "Liverpool", "away": "Atalanta", "league": "Europa League", "time": "20:00", "home_str": 1.55, "away_str": 1.25},
    {"home": "Manchester United", "away": "Chelsea", "league": "Premier League", "time": "16:00", "home_str": 1.20, "away_str": 1.28},
    {"home": "Barcelona", "away": "Atlético Madrid", "league": "La Liga", "time": "20:00", "home_str": 1.50, "away_str": 1.35},
    {"home": "Bayern Munich", "away": "Dortmund", "league": "Bundesliga", "time": "17:30", "home_str": 1.70, "away_str": 1.30},
    {"home": "PSG", "away": "Monaco", "league": "Ligue 1", "time": "20:00", "home_str": 1.48, "away_str": 1.32},
    {"home": "Inter Milan", "away": "Juventus", "league": "Serie A", "time": "19:00", "home_str": 1.40, "away_str": 1.35},
]

# Filter by league
if st.session_state.league_filter != "All":
    FIXTURES = [f for f in FIXTURES if f["league"] == st.session_state.league_filter]

# ──────────────────────────────────────────────────────────────────────────────
# RENDER MATCHES
# ──────────────────────────────────────────────────────────────────────────────

current_league = None

for i, match in enumerate(FIXTURES):
    league = match["league"]
    
    if league != current_league:
        st.markdown(f"<div class='league-section'>{league}</div>", unsafe_allow_html=True)
        current_league = league
    
    # Get predictions
    pred = predict_match(match["home"], match["away"], match["home_str"], match["away_str"])
    cosmic = cosmic_verdict(match["home"], match["away"], match["home_str"], match["away_str"])
    
    # Match Card
    st.markdown(f"""
    <div class="match-card">
      <div class="card-header">
        <div class="clubs">
          <div class="club">
            <div class="crest">🏠</div>
            <span>{match['home']}</span>
          </div>
          <div class="vs-pill">vs</div>
          <div class="club">
            <div class="crest">✈️</div>
            <span>{match['away']}</span>
          </div>
        </div>
        <div style="font-size:13px;color:#9BA0B5;font-weight:600">{match['time']}</div>
      </div>
      <div style="display:flex;align-items:center;gap:14px;margin-bottom:10px;font-size:13px;color:#9BA0B5">
        <span style="min-width:40px">Home</span>
        <div class="prob-bar"><div class="prob-bar-fill" style="width:{pred['home']*100}%"></div></div>
        <span>{pred['home']:.1%}</span>
      </div>
      <div style="display:flex;align-items:center;gap:14px;margin-bottom:10px;font-size:13px;color:#9BA0B5">
        <span style="min-width:40px">Draw</span>
        <div class="prob-bar"><div class="prob-bar-fill" style="width:{pred['draw']*100}%"></div></div>
        <span>{pred['draw']:.1%}</span>
      </div>
      <div style="display:flex;align-items:center;gap:14px;font-size:13px;color:#9BA0B5">
        <span style="min-width:40px">Away</span>
        <div class="prob-bar"><div class="prob-bar-fill" style="width:{pred['away']*100}%"></div></div>
        <span>{pred['away']:.1%}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Market Grid
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown(f"""
        <div class="market-card">
          <h4>⚽ Over / Under</h4>
          <div class="metric-row">Over 2.5 <strong>{pred['over25']:.1%}</strong></div>
          <div class="metric-row">Under 2.5 <strong>{1-pred['over25']:.1%}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        o25_odds = round(1 / max(pred["over25"], 0.01), 2)
        if st.button(f"Add Over 2.5 @ {o25_odds}", key=f"ou_{i}"):
            add_to_parlay(f"{match['home']} vs {match['away']} - Over 2.5", o25_odds, pred["over25"])
    
    with cols[1]:
        st.markdown(f"""
        <div class="market-card">
          <h4>🎯 Double Chance</h4>
          <div class="metric-row">1X <strong>{pred['home']+pred['draw']:.1%}</strong></div>
          <div class="metric-row">X2 <strong>{pred['draw']+pred['away']:.1%}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        dc_odds = round(1 / max(pred["home"] + pred["draw"], 0.01), 2)
        if st.button(f"Add 1X @ {dc_odds}", key=f"dc_{i}"):
            add_to_parlay(f"{match['home']} vs {match['away']} - 1X", dc_odds, pred["home"] + pred["draw"])
    
    with cols[2]:
        if st.session_state.show_cosmic:
            st.markdown(f"""
            <div class="market-card cosmic">
              <h4>{cosmic['pick']}</h4>
              <div class="metric-row">Confidence <strong>{cosmic.get('confidence', 0.5):.0%}</strong></div>
              <div class="metric-row">Bias <strong>{cosmic.get('bias', 0):.2f}</strong></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="market-card">
              <h4>BTTS</h4>
              <div class="metric-row">Yes <strong>{pred['btts']:.1%}</strong></div>
              <div class="metric-row">No <strong>{1-pred['btts']:.1%}</strong></div>
            </div>
            """, unsafe_allow_html=True)
            btts_odds = round(1 / max(pred["btts"], 0.01), 2)
            if st.button(f"Add BTTS @ {btts_odds}", key=f"btts_{i}"):
                add_to_parlay(f"{match['home']} vs {match['away']} - BTTS", btts_odds, pred["btts"])

# ──────────────────────────────────────────────────────────────────────────────
# RESPONSIBLE GAMBLING
# ──────────────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="responsible-banner">
  🎲 {RG_WARNING} 
  <a href='https://www.gamblersanonymous.org' style='color:#FFD700;margin-left:10px'>Get Help</a>
</div>
""", unsafe_allow_html=True)