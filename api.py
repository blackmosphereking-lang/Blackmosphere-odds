# app.py — Blackmosphere FootMob Edition
# Modern, sophisticated football prediction interface

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────

from config import (
    CSS, LEAGUE_CODES, PINNACLE_LEAGUE_IDS, 
    STATSBOMB_COMPS, RG_WARNING, MARKET_ICONS
)
from models import predict_match, kelly_stake, poisson_prob
from cosmic import cosmic_verdict
from sources import (
    sofa_today_events, sofa_event_prediction, sofa_team_last5,
    sb_team_xg, pinnacle_odds
)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Blackmosphere | AI + Cosmic Predictions",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject modern CSS
st.markdown(CSS, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════

_defaults = {
    'parlay': [],
    'bankroll': 1000.0,
    'bet_history': [],
    'selected_date': date.today(),
    'cosmic_toggle': True,
    'value_threshold': 0.05,
    'filters': {
        'show_value_only': False,
        'min_probability': 0.0,
        'leagues': []
    }
}

for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def load_today_matches() -> Dict[str, List[Dict]]:
    """Load today's matches grouped by league."""
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
            'home_id': e.get('homeTeam', {}).get('id'),
            'away_id': e.get('awayTeam', {}).get('id'),
            'start': e.get('startTimestamp', 0),
            'time': datetime.fromtimestamp(e.get('startTimestamp', 0)).strftime('%H:%M'),
            'league': league,
            'venue': e.get('venue', {}).get('name', 'TBD'),
            'status': e.get('status', {}).get('description', 'Scheduled')
        })
    return grouped


def get_team_strength(team_id: int) -> float:
    """Get team strength from recent performance."""
    data = sofa_team_last5(team_id)
    if not data:
        return 1.0
    goals = data.get('goals_scored_avg', 1.5)
    conceded = data.get('goals_conceded_avg', 1.5)
    return max(0.5, min(2.5, (goals + (2.5 - conceded)) / 2))


def calculate_value(prob: float, odds: float) -> tuple:
    """Calculate edge and value status."""
    implied = 1 / odds
    edge = prob - implied
    is_value = edge > st.session_state.value_threshold
    return edge, is_value


def format_prob_bar(prob: float, color: str = "#2FD9C5") -> str:
    """Create a styled probability bar."""
    pct = prob * 100
    return f"""
    <div class="prob-bar-container">
        <div class="prob-bar" style="width:{pct}%; background:{color};"></div>
        <span class="prob-text">{pct:.1f}%</span>
    </div>
    """


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <span class="logo-icon">🔮</span>
        <div class="logo-text">
            <h2>BLACKMOSPHERE</h2>
            <span>AI + COSMIC PREDICTIONS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Date Picker
    st.markdown("### 📅 Date")
    selected_date = st.date_input(
        "Match Date",
        value=st.session_state.selected_date,
        key="date_picker"
    )
    st.session_state.selected_date = selected_date
    
    # Cosmic Toggle
    st.markdown("### 🔮 Cosmic Layer")
    st.session_state.cosmic_toggle = st.toggle(
        "Enable Esoteric Predictions",
        value=st.session_state.cosmic_toggle
    )
    
    # Filters
    st.markdown("### ⚙️ Filters")
    st.session_state.filters['show_value_only'] = st.toggle(
        "Show Value Bets Only",
        value=False
    )
    st.session_state.filters['min_probability'] = st.slider(
        "Min Probability",
        0.0, 1.0, 0.0, 0.05
    )
    
    # League Filter
    all_leagues = ["All Leagues", "Premier League", "La Liga", "Bundesliga", 
                   "Serie A", "Ligue 1", "Champions League"]
    selected_league = st.selectbox("Filter League", all_leagues)
    
    st.markdown("---")
    
    # Bankroll Display
    st.markdown(f"""
    <div class="bankroll-card">
        <span class="label">💰 Bankroll</span>
        <span class="amount">${st.session_state.bankroll:,.2f}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Bet Slip Summary
    if st.session_state.parlay:
        st.markdown("### 🎯 Bet Slip")
        total_odds = 1.0
        for i, leg in enumerate(st.session_state.parlay):
            total_odds *= leg['odds']
            st.markdown(f"""
            <div class="slip-leg">
                <span>{leg['name']}</span>
                <strong>@ {leg['odds']:.2f}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="slip-total">
            <span>Combined Odds</span>
            <strong>{total_odds:.2f}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        stake = st.number_input("Stake ($)", min_value=1.0, value=10.0)
        potential = stake * total_odds
        
        st.markdown(f"""
        <div class="potential-return">
            Potential Return: <strong>${potential:,.2f}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ LOG BET", use_container_width=True):
            st.session_state.bet_history.append({
                'Date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'Legs': len(st.session_state.parlay),
                'Odds': round(total_odds, 2),
                'Stake': stake,
                'Potential': round(potential, 2),
                'Result': 'Pending'
            })
            st.session_state.bankroll -= stake
            st.session_state.parlay = []
            st.rerun()
        
        if st.button("🗑️ Clear Slip", use_container_width=True):
            st.session_state.parlay = []
            st.rerun()
    else:
        st.info("No bets in slip. Add selections from match cards.")
    
    # Responsible Gaming
    st.markdown("---")
    st.markdown(RG_WARNING, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="main-header">
    <div class="header-content">
        <h1>⚽ Today's Matches</h1>
        <p>AI-Powered Predictions with Cosmic Overlay</p>
    </div>
    <div class="header-stats">
        <div class="stat-box">
            <span class="stat-value" id="match_count">--</span>
            <span class="stat-label">Matches</span>
        </div>
        <div class="stat-box">
            <span class="stat-value" id="value_count">--</span>
            <span class="stat-label">Value Bets</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Load Matches
with st.spinner("Loading today's fixtures..."):
    matches_by_league = load_today_matches()

if not matches_by_league:
    st.markdown("""
    <div class="empty-state">
        <span class="empty-icon">📅</span>
        <h3>No Matches Today</h3>
        <p>Select a different date or check back later.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Filter leagues
    if selected_league != "All Leagues":
        matches_by_league = {selected_league: matches_by_league.get(selected_league, [])}
    
    total_matches = sum(len(v) for v in matches_by_league.values())
    value_bets = 0
    
    # Update header stats
    st.markdown(f"""
    <script>
        document.getElementById('match_count').textContent = '{total_matches}';
    </script>
    """, unsafe_allow_html=True)
    
    # Render League Sections
    for league_name, matches in matches_by_league.items():
        if not matches:
            continue
            
        # League Header
        league_code = LEAGUE_CODES.get(league_name, 'OT')
        st.markdown(f"""
        <div class="league-header">
            <span class="league-badge">{league_code}</span>
            <h2>{league_name}</h2>
            <span class="match-count">{len(matches)} matches</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Match Cards
        for match in matches:
            with st.container():
                # Get team strengths
                home_str = get_team_strength(match.get('home_id', 0))
                away_str = get_team_strength(match.get('away_id', 0))
                
                # Generate predictions
                league_key = LEAGUE_CODES.get(league_name, 'PL')
                pred = predict_match(league_key, home_str, away_str)
                
                # Cosmic verdict
                cosmic = None
                if st.session_state.cosmic_toggle:
                    cosmic = cosmic_verdict(
                        match['home'], match['away'],
                        home_str, away_str, 
                        st.session_state.selected_date
                    )
                
                # Check for value bets
                value_count = 0
                markets_to_check = [
                    ('Home Win', pred['home'], pred['h_odds']),
                    ('Draw', pred['draw'], pred['d_odds']),
                    ('Away Win', pred['away'], pred['a_odds']),
                    ('Over 2.5', pred['over25'], pred['over25_odds']),
                    ('BTTS', pred['btts'], pred['btts_odds'])
                ]
                for _, prob, odds in markets_to_check:
                    edge, is_val = calculate_value(prob, odds)
                    if is_val:
                        value_count += 1
                
                value_bets += value_count
                
                # Filter by value toggle
                if st.session_state.filters['show_value_only'] and value_count == 0:
                    continue
                
                # ─── MATCH CARD ─────────────────────────────────────────────
                st.markdown(f"""
                <div class="match-card" id="match_{match['id']}">
                    <div class="card-top">
                        <div class="match-info">
                            <span class="match-time">{match['time']}</span>
                            <span class="match-status">{match['status']}</span>
                        </div>
                        <div class="match-venue">📍 {match['venue']}</div>
                    </div>
                    
                    <div class="teams-row">
                        <div class="team home-team">
                            <div class="team-crest">🏠</div>
                            <span class="team-name">{match['home']}</span>
                            <div class="strength-bar">
                                <div class="strength-fill" style="width:{home_str*40}%"></div>
                            </div>
                        </div>
                        
                        <div class="match-center">
                            <span class="vs">VS</span>
                            <div class="prob-summary">
                                <span class="prob-home">{pred['home']:.0%}</span>
                                <span class="prob-draw">{pred['draw']:.0%}</span>
                                <span class="prob-away">{pred['away']:.0%}</span>
                            </div>
                        </div>
                        
                        <div class="team away-team">
                            <div class="team-crest">✈️</div>
                            <span class="team-name">{match['away']}</span>
                            <div class="strength-bar">
                                <div class="strength-fill" style="width:{away_str*40}%"></div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # ─── PREDICTION TABS ─────────────────────────────────────────
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "🎯 Main Bets", "⚽ Goals", "📊 Corners & Cards", 
                    "🎯 Correct Score", "🔮 Cosmic"
                ])
                
                # TAB 1: Main Bets (1X2, Double Chance)
                with tab1:
                    c1, c2, c3 = st.columns(3)
                    
                    # 1X2
                    with c1:
                        st.markdown("**Match Result (1X2)**")
                        h_edge, h_val = calculate_value(pred['home'], pred['h_odds'])
                        d_edge, d_val = calculate_value(pred['draw'], pred['d_odds'])
                        a_edge, a_val = calculate_value(pred['away'], pred['a_odds'])
                        
                        for label, prob, odds, edge, is_val in [
                            ("1", pred['home'], pred['h_odds'], h_edge, h_val),
                            ("X", pred['draw'], pred['d_odds'], d_edge, d_val),
                            ("2", pred['away'], pred['a_odds'], a_edge, a_val)
                        ]:
                            val_tag = "✅" if is_val else ""
                            st.markdown(f"""
                            <div class="bet-row" onclick="addToSlip('{label}', {odds})">
                                <span class="bet-label">{label} {val_tag}</span>
                                <span class="bet-odds">{odds:.2f}</span>
                                <span class="bet-prob">{prob:.0%}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Double Chance
                    with c2:
                        st.markdown("**Double Chance**")
                        dc_1x = pred['home'] + pred['draw']
                        dc_x2 = pred['draw'] + pred['away']
                        dc_12 = pred['home'] + pred['away']
                        
                        for label, prob in [("1X", dc_1x), ("X2", dc_x2), ("12", dc_12)]:
                            odds = 1 / prob if prob > 0 else 1
                            st.markdown(f"""
                            <div class="bet-row">
                                <span class="bet-label">{label}</span>
                                <span class="bet-odds">{odds:.2f}</span>
                                <span class="bet-prob">{prob:.0%}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Both Teams To Score
                    with c3:
                        st.markdown("**Both Teams To Score**")
                        btts_yes = pred['btts']
                        btts_no = 1 - btts_yes
                        
                        for label, prob in [("BTTS Yes", btts_yes), ("BTTS No", btts_no)]:
                            odds = 1 / prob if prob > 0 else 1
                            st.markdown(f"""
                            <div class="bet-row">
                                <span class="bet-label">{label}</span>
                                <span class="bet-odds">{odds:.2f}</span>
                                <span class="bet-prob">{prob:.0%}</span>
                            </div>
                            """, unsafe_allow_html=True)
                
                # TAB 2: Goals
                with tab2:
                    c1, c2, c3 = st.columns(3)
                    
                    with c1:
                        st.markdown("**Over/Under 2.5**")
                        for label, prob in [("Over 2.5", pred['over25']), ("Under 2.5", 1-pred['over25'])]:
                            odds = pred.get('over25_odds', 1.85) if 'Over' in label else pred.get('under25_odds', 1.95)
                            st.markdown(f"""
                            <div class="bet-row">
                                <span class="bet-label">{label}</span>
                                <span class="bet-odds">{odds:.2f}</span>
                                <span class="bet-prob">{prob:.0%}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with c2:
                        st.markdown("**Over/Under 3.5**")
                        over35 = pred.get('over35', 0.35)
                        for label, prob in [("Over 3.5", over35), ("Under 3.5", 1-over35)]:
                            odds = 2.10 if 'Over' in label else 1.70
                            st.markdown(f"""
                            <div class="bet-row">
                                <span class="bet-label">{label}</span>
                                <span class="bet-odds">{odds:.2f}</span>
                                <span class="bet-prob">{prob:.0%}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with c3:
                        st.markdown("**First Half Goals**")
                        fh_over = pred.get('fh_over15', 0.60)
                        for label, prob in [("Over 1.5 HT", fh_over), ("Under 1.5 HT", 1-fh_over)]:
                            odds = 2.05 if 'Over' in label else 1.75
                            st.markdown(f"""
                            <div class="bet-row">
                                <span class="bet-label">{label}</span>
                                <span class="bet-odds">{odds:.2f}</span>
                                <span class="bet-prob">{prob:.0%}</span>
                            </div>
                            """, unsafe_allow_html=True)
                
         