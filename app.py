# app.py — Blackmosphere FootMob Edition (FIXED)

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Dict, List

# Direct imports - no more missing constants
from config import CSS, LEAGUE_CODES, RG_WARNING
from models import predict_match, kelly_stake
from cosmic import cosmic_verdict
from api import fetch_matches, fetch_standings

# Try importing sources (optional)
try:
    from sources import sofa_today_events, sofa_team_last5
    SOFA_OK = True
except Exception:
    SOFA_OK = False

# ════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Blackmosphere | AI + Cosmic Predictions",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CSS, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════════════════

_defaults = {
    'parlay': [],
    'bankroll': 1000.0,
    'bet_history': [],
    'selected_date': date.today(),
    'cosmic_toggle': True,
    'value_threshold': 0.05,
    'filters': {'show_value_only': False, 'min_probability': 0.0}
}

for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")

# ════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def load_today_matches() -> Dict[str, List[Dict]]:
    """Load today's matches grouped by league."""
    if not API_KEY:
        # Fallback to SofaScore if no API key
        if SOFA_OK:
            events = sofa_today_events()
            if not events:
                return {}
            grouped = {}
            for e in events:
                league = e.get('tournament', {}).get('category', {}).get('name', 'Other')
                if league not in grouped:
                    grouped[league] = []
                grouped[league].append({
                    'id': e.get('id'),
                    'home': e.get('homeTeam', {}).get('name', 'TBD'),
                    'away': e.get('awayTeam', {}).get('name', 'TBD'),
                    'home_id': e.get('homeTeam', {}).get('id', 0),
                    'away_id': e.get('awayTeam', {}).get('id', 0),
                    'time': e.get('time', '00:00'),
                    'league': league,
                    'venue': e.get('venue', {}).get('name', 'TBD'),
                    'status': 'Scheduled'
                })
            return grouped
        return {}

    # Use Football Data API
    matches = fetch_matches(API_KEY, days=7)

    grouped = {}
    for m in matches:
        league = m.get('competition', 'Other')
        if league not in grouped:
            grouped[league] = []
        utc = m.get('utcDate', '')
        try:
            dt = datetime.fromisoformat(utc.replace('Z', '+00:00'))
            time_str = dt.strftime('%H:%M')
        except (ValueError, AttributeError):
            time_str = '00:00'

        # FIX 1: 'status' may be a string, not a dict — handle both cases
        raw_status = m.get('status', 'Scheduled')
        if isinstance(raw_status, dict):
            status_str = raw_status.get('description', 'Scheduled')
        else:
            status_str = str(raw_status)

        grouped[league].append({
            'id': m.get('id'),
            'home': m.get('homeTeam', {}).get('name', 'TBD'),
            'away': m.get('awayTeam', {}).get('name', 'TBD'),
            'home_id': m.get('homeTeam', {}).get('id', 0),
            'away_id': m.get('awayTeam', {}).get('id', 0),
            'time': time_str,
            'league': league,
            'venue': 'Stadium',
            'status': status_str
        })
    return grouped


def get_team_strength(team_name: str, league_code: str = 'PL') -> float:
    """Get team strength from standings."""
    if not API_KEY:
        return 1.0
    standings = fetch_standings(API_KEY, league_code)
    return standings.get(team_name, 1.0)


def calculate_value(prob: float, odds: float) -> tuple:
    """Calculate edge and value status."""
    if odds <= 0:
        return 0.0, False
    implied = 1 / odds
    edge = prob - implied
    is_value = edge > st.session_state.value_threshold
    return edge, is_value


def add_to_slip(name: str, odds: float, prob: float):
    """Add selection to bet slip."""
    # FIX 2: Prevent duplicate entries in the slip
    for existing in st.session_state.parlay:
        if existing["name"] == name:
            return
    st.session_state.parlay.append({
        "name": name,
        "odds": round(odds, 2),
        "prob": round(prob, 2)
    })


# ════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════════════════════════════════════════

st.sidebar.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon">⚽</div>
        <div class="logo-text">
            <h2>Blackmosphere</h2>
            <span>AI + Cosmic Predictions</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# FIX 3: Display the actual dynamic bankroll value, not a hardcoded string
st.sidebar.markdown(f"""
    <div class="bankroll-card">
        <div class="label">Bankroll</div>
        <div class="amount">${st.session_state.bankroll:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("""
    <div class="responsible-banner">
        ⚠️ <strong>Gamble Responsibly:</strong> This is for entertainment only.
        Not affiliated with any bookmaker. Never bet more than you can afford to lose.
        <a href="#" style="color:#FFDADA;">Get Help</a>
    </div>
    """, unsafe_allow_html=True)

# Main content
st.markdown("""
    <div class="main-header">
        <div class="header-content">
            <h1>FootMob AI</h1>
            <p>AI + Cosmic Predictions for Football Betting</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Load matches
matches = load_today_matches()

if not matches:
    st.write("No matches found for today. Please check back later.")
else:
    for league, games in matches.items():
        st.markdown(f"### {league}")
        for game in games:
            st.write(f"**{game['home']} vs {game['away']}**")
            st.write(f"Time: {game['time']}")
            st.write(f"Venue: {game['venue']}")
            st.write(f"Status: {game['status']}")

            # FIX 4: KeyError — league may not exist in LEAGUE_CODES.
            # Use .get() with a sensible default instead of direct indexing.
            league_code = LEAGUE_CODES.get(league, 'PL')

            home_strength = get_team_strength(game['home'], league_code)
            away_strength = get_team_strength(game['away'], league_code)
            prediction = predict_match(league, home_strength, away_strength)

            # Display prediction
            st.write("#### Prediction")
            st.write(f"**Home Win Probability:** {prediction['home'] * 100:.2f}%")
            st.write(f"**Draw Probability:** {prediction['draw'] * 100:.2f}%")
            st.write(f"**Away Win Probability:** {prediction['away'] * 100:.2f}%")

            # FIX 5: Use a unique key for each button to prevent Streamlit's
            # DuplicateWidgetID error when multiple games are rendered.
            btn_key = f"slip_{game.get('id', '')}_{game['home']}_{game['away']}"
            if st.button(f"Add {game['home']} vs {game['away']} to slip", key=btn_key):
                # FIX 6: Guard against missing 'h_odds' key — fall back to 0.0
                h_odds = prediction.get('h_odds', 0.0)
                add_to_slip(
                    f"{game['home']} vs {game['away']}",
                    h_odds,
                    prediction['home']
                )

# Display bet slip
if st.session_state.parlay:
    st.markdown("### Bet Slip")
    for i, bet in enumerate(st.session_state.parlay):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(
                f"**{bet['name']}** — Odds: {bet['odds']} — "
                f"Probability: {bet['prob'] * 100:.2f}%"
            )
        # FIX 7: Provide a way to remove items from the slip
        with col2:
            if st.button("❌", key=f"remove_{i}"):
                st.session_state.parlay.pop(i)
                st.rerun()