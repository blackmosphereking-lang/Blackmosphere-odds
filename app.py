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
        except:
            time_str = '00:00'

        grouped[league].append({
            'id': m.get('id'),
            'home': m.get('homeTeam', {}).get('name', 'TBD'),
            'away': m.get('awayTeam', {}).get('name', 'TBD'),
            'home_id': m.get('homeTeam', {}).get('id', 0),
            'away_id': m.get('awayTeam', {}).get('id', 0),
            'time': time_str,
            'league': league,
            'venue': 'Stadium',
            'status': m.get('status', {}).get('description', 'Scheduled')
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
    st.session_state.parlay.append({
        "name": name,
        "odds": round
\<Streaming stoppped because the conversation grew too long for this model\>