# ════════════════════════════════════════════════════════════════════════════
# FILE 6: app.py (main Streamlit application)
# ════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Dict, List

from config import (
    CSS,
    LEAGUE_CODES,
    RG_WARNING,
    FOOTBALL_DATA_API_KEY,
    LEAGUE_PARAMS,
    DEFAULT_LEAGUE_PARAMS,
    COSMIC_ENABLED,
)
from models import predict_match, kelly_stake
from cosmic import cosmic_verdict
from api import fetch_matches, fetch_standings

# Try importing sources (optional)
try:
    from sources import sofa_today_events, sofa_team_last5
    SOFA_OK = True
except Exception:
    SOFA_OK = False

# ── Page Config ───────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Blackmosphere | AI + Cosmic Predictions",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CSS, unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────

_defaults = {
    "parlay": [],
    "bankroll": 1000.0,
    "bet_history": [],
    "selected_date": date.today(),
    "cosmic_toggle": True,
    "value_threshold": 0.05,
    "filters": {"show_value_only": False, "min_probability": 0.0},
}

for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helper Functions ──────────────────────────────────────────────────────


def load_today_matches() -> Dict[str, List[Dict]]:
    """Load today's matches grouped by league."""
    if not FOOTBALL_DATA_API_KEY:
        if SOFA_OK:
            events = sofa_today_events()
            if not events:
                return {}
            grouped: Dict[str, List[Dict]] = {}
            for e in events:
                league = (
                    e.get("tournament", {})
                    .get("category", {})
                    .get("name", "Other")
                )
                if league not in grouped:
                    grouped[league] = []
                grouped[league].append(
                    {
                        "id": e.get("id"),
                        "home": e.get("homeTeam", {}).get("name", "TBD"),
                        "away": e.get("awayTeam", {}).get("name", "TBD"),
                        "home_id": e.get("homeTeam", {}).get("id", 0),
                        "away_id": e.get("awayTeam", {}).get("id", 0),
                        "time": e.get("time", "00:00"),
                        "league": league,
                        "venue": e.get("venue", {}).get("name", "TBD"),
                        "status": "Scheduled",
                    }
                )
            return grouped
        return {}

    matches = fetch_matches()

    grouped: Dict[str, List[Dict]] = {}
    for m in matches:
        league = m.get("competition", "Other")
        if league not in grouped:
            grouped[league] = []

        utc = m.get("utcDate", "")
        try:
            dt = datetime.fromisoformat(utc.replace("Z", "+00:00"))
            time_str = dt.strftime("%H:%M")
        except (ValueError, AttributeError):
            time_str = "00:00"

        raw_status = m.get("status", "Scheduled")
        if isinstance(raw_status, dict):
            status_str = raw_status.get("description", "Scheduled")
        else:
            status_str = str(raw_status)

        grouped[league].append(
            {
                "id": m.get("id"),
                "home": m.get("homeTeam", {}).get("name", "TBD"),
                "away": m.get("awayTeam", {}).get("name", "TBD"),
                "home_id": m.get("homeTeam", {}).get("id", 0),
                "away_id": m.get("awayTeam", {}).get("id", 0),
                "time": time_str,
                "league": league,
                "venue": "Stadium",
                "status": status_str,
            }
        )
    return grouped


def get_team_strength(team_name: str, league_code: str = "PL") -> float:
    """Get team strength from standings."""
    if not FOOTBALL_DATA_API_KEY:
        return 1.0
    standings = fetch_standings(league_code=league_code)
    return standings.get(team_name, 1.0)


def calculate_value(prob: float, odds: float) -> tuple:
    """Calculate edge and value status."""
    if odds <= 0:
        return 0.0, False
    implied = 1.0 / odds
    edge = prob - implied
    is_value = edge > st.session_state.value_threshold
    return edge, is_value


def add_to_slip(name: str, odds: float, prob: float):
    """Add selection to bet slip (no duplicates)."""
    for existing in st.session_state.parlay:
        if existing["name"] == name:
            return
    st.session_state.parlay.append(
        {"name": name, "odds": round(odds, 2), "prob": round(prob, 2)}
    )


# ── Sidebar ───────────────────────────────────────────────────────────────

st.sidebar.markdown(
    """
    <div class="sidebar-logo">
        <div class="logo-icon">⚽</div>
        <div class="logo-text">
            <h2>Blackmosphere</h2>
            <span>AI + Cosmic Predictions</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    f"""
    <div class="bankroll-card">
        <div class="label">Bankroll</div>
        <div class="amount">${st.session_state.bankroll:,.2f}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")

st.session_state.cosmic_toggle = st.sidebar.checkbox(
    "🌌 Enable Cosmic Verdicts", value=st.session_state.cosmic_toggle
)

st.session_state.value_threshold = st.sidebar.slider(
    "Value Edge Threshold", 0.0, 0.30, st.session_state.value_threshold, 0.01
)

show_value_only = st.sidebar.checkbox(
    "Show Value Bets Only", value=st.session_state.filters["show_value_only"]
)
st.session_state.filters["show_value_only"] = show_value_only

st.sidebar.markdown("---")

st.sidebar.markdown(
    f"""
    <div class="responsible-banner">
        {RG_WARNING}
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Main Header ───────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="main-header">
        <div class="header-content">
            <h1>FootMob AI</h1>
            <p>AI + Cosmic Predictions for Football Betting</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Match Display ─────────────────────────────────────────────────────────

matches = load_today_matches()

if not matches:
    st.info("No matches found for today. Please check back later.")
else:
    for league, games in matches.items():
        st.markdown(f"### 🏆 {league}")

        for game in games:
            league_code = LEAGUE_CODES.get(league, "PL")

            home_strength = get_team_strength(game["home"], league_code)
            away_strength = get_team_strength(game["away"], league_code)

            prediction = predict_match(league, home_strength, away_strength)

            home_prob = prediction["home"]
            draw_prob = prediction["draw"]
            away_prob = prediction["away"]
            h_odds = prediction.get("h_odds", 0.0)
            d_odds = prediction.get("d_odds", 0.0)
            a_odds = prediction.get("a_odds", 0.0)

            h_edge, h_value = calculate_value(home_prob, h_odds)
            d_edge, d_value = calculate_value(draw_prob, d_odds)
            a_edge, a_value = calculate_value(away_prob, a_odds)

            has_value = h_value or d_value or a_value

            if st.session_state.filters["show_value_only"] and not has_value:
                continue

            bankroll = st.session_state.bankroll
            h_stake = kelly_stake(home_prob, h_odds, bankroll)
            d_stake = kelly_stake(draw_prob, d_odds, bankroll)
            a_stake = kelly_stake(away_prob, a_odds, bankroll)

            # Match card
            with st.expander(
                f"⚽ {game['home']}  vs  {game['away']}  —  {game['time']}",
                expanded=False,
            ):
                info_c1, info_c2, info_c3 = st.columns(3)
                with info_c1:
                    st.caption(f"🕐 Kick-off: {game['time']}")
                with info_c2:
                    st.caption(f"🏟️ Venue: {game['venue']}")
                with info_c3:
                    st.caption(f"📋 Status: {game['status']}")

                st.markdown("---")
                st.markdown("#### 📊 Probabilities & Odds")

                col_h, col_d, col_a = st.columns(3)

                with col_h:
                    tag = " ✅ VALUE" if h_value else ""
                    st.metric(
                        label=f"🏠 {game['home']}{tag}",
                        value=f"{home_prob * 100:.1f}%",
                        delta=(
                            f"Edge {h_edge * 100:+.1f}%"
                            if h_odds > 0
                            else None
                        ),
                    )
                    st.caption(f"Odds: {h_odds:.2f}")
                    if h_stake > 0:
                        st.caption(f"Kelly Stake: ${h_stake:.2f}")

                with col_d:
                    tag = " ✅ VALUE" if d_value else ""
                    st.metric(
                        label=f"🤝 Draw{tag}",
                        value=f"{draw_prob * 100:.1f}%",
                        delta=(
                            f"Edge {d_edge * 100:+.1f}%"
                            if d_odds > 0
                            else None
                        ),
                    )
                    st.caption(f"Odds: {d_odds:.2f}")
                    if d_stake > 0:
                        st.caption(f"Kelly Stake: ${d_stake:.2f}")

                with col_a:
                    tag = " ✅ VALUE" if a_value else ""
                    st.metric(
                        label=f"✈️ {game['away']}{tag}",
                        value=f"{away_prob * 100:.1f}%",
                        delta=(
                            f"Edge {a_edge * 100:+.1f}%"
                            if a_odds > 0
                            else None
                        ),
                    )
                    st.caption(f"Odds: {a_odds:.2f}")
                    if a_stake > 0:
                        st.caption(f"Kelly Stake: ${a_stake:.2f}")

                # Cosmic verdict
                if st.session_state.cosmic_toggle and COSMIC_ENABLED:
                    st.markdown("---")
                    st.markdown("#### 🌌 Cosmic Verdict")
                    verdict = cosmic_verdict(game["home"], game["away"])
                    st.info(verdict)

                # Add-to-slip buttons
                st.markdown("---")
                match_id = game.get("id", f"{game['home']}_{game['away']}")
                btn_c1, btn_c2, btn_c3 = st.columns(3)

                with btn_c1:
                    if st.button(
                        f"Add {game['home']} Win",
                        key=f"home_{match_id}",
                    ):
                        add_to_slip(
                            f"{game['home']} to beat {game['away']}",
                            h_odds,
                            home_prob,
                        )
                        st.rerun()

                with btn_c2:
                    if st.button("Add Draw", key=f"draw_{match_id}"):
                        add_to_slip(
                            f"{game['home']} vs {game['away']} — Draw",
                            d_odds,
                            draw_prob,
                        )
                        st.rerun()

                with btn_c3:
                    if st.button(
                        f"Add {game['away']} Win",
                        key=f"away_{match_id}",
                    ):
                        add_to_slip(
                            f"{game['away']} to beat {game['home']}",
                            a_odds,
                            away_prob,
                        )
                        st.rerun()

# ── Bet Slip ──────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("### 🎫 Bet Slip")

if not st.session_state.parlay:
    st.caption("Your bet slip is empty. Add selections from the matches above.")
else:
    combined_odds = 1.0
    combined_prob = 1.0

    for i, bet in enumerate(st.session_state.parlay):
        col_info, col_odds, col_remove = st.columns([5, 2, 1])
        with col_info:
            st.write(f"**{bet['name']}**")
        with col_odds:
            st.write(f"Odds: {bet['odds']}  |  {bet['prob'] * 100:.1f}%")
        with col_remove:
            if st.button("❌", key=f"remove_{i}"):
                st.session_state.parlay.pop(i)
                st.rerun()

        combined_odds *= bet["odds"]
        combined_prob *= bet["prob"]

    st.markdown("---")

    sum_c1, sum_c2, sum_c3 = st.columns(3)
    with sum_c1:
        st.metric("Combined Odds", f"{combined_odds:.2f}")
    with sum_c2:
        st.metric("Combined Probability", f"{combined_prob * 100:.2f}%")
    with sum_c3:
        parlay_stake = kelly_stake(
            combined_prob, combined_odds, st.session_state.bankroll
        )
        st.metric("Suggested Stake", f"${parlay_stake:.2f}")

    if parlay_stake > 0:
        payout = parlay_stake * combined_odds
        st.success(f"💰 Potential payout: ${payout:.2f}")

    if st.button("🗑️ Clear Bet Slip"):
        st.session_state.parlay = []
        st.rerun()