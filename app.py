# app.py — Main Streamlit entry point

import streamlit as st
import pandas as pd
from datetime import datetime

from config import LEAGUE_CODES, CSS
from api import fetch_matches, fetch_standings
from models import predict_match, kelly_stake, value_analysis
from charts import prob_bar, score_heatmap, team_radar, pnl_chart

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Blackmosphere Gold", page_icon="🏆", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

# ── API Key ────────────────────────────────────────────────────────────────────
API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")

# ── Session State Init ─────────────────────────────────────────────────────────
_defaults = {
    'parlay':      [],
    'bankroll':    1000.0,
    'bet_history': [],
    'standings':   {},
    'last_res':    None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h3 style='text-align:center;'>🎯 Gold Ticket</h3>", unsafe_allow_html=True)
    if st.session_state.parlay:
        running_odds = 1.0
        for leg in st.session_state.parlay:
            st.markdown(f"🔸 {leg['name']}  \n**@ {leg['odds']:.2f}**")
            running_odds *= leg['odds']
        st.divider()
        st.markdown(f"**Combined: {running_odds:.2f}**")
    else:
        st.caption("No legs added yet.")
    st.divider()
    st.metric("Bankroll", f"${st.session_state.bankroll:,.2f}")
    if not API_KEY:
        st.warning("⚠️ No API key found.\nAdd it to `.streamlit/secrets.toml`.")

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;'>🏆 BLACKMOSPHERE GOLD</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#D4AF37;letter-spacing:4px;font-size:13px;'>"
    "PREMIUM SPORTS PREDICTION ENGINE</p>",
    unsafe_allow_html=True,
)
st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["🔮 Predictor", "⚽ Fixtures", "🎯 Gold Ticket", "📊 Bankroll"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### ⚙️ Match Setup")
    c1, c2, c3 = st.columns(3)

    with c1:
        league    = st.selectbox("League", list(LEAGUE_CODES.keys()))
        home_name = st.text_input("Home Team Name", "Home Team")
        away_name = st.text_input("Away Team Name", "Away Team")

    with c2:
        if st.button("📊 Auto-Load Strengths from Standings"):
            data = fetch_standings(API_KEY, LEAGUE_CODES[league])
            if data:
                st.session_state.standings = data
                st.toast(f"Loaded {len(data)} teams!", icon="📊")
            else:
                st.warning("Could not load standings. Check your API key and free-tier limits.")

        if st.session_state.standings:
            team_list = list(st.session_state.standings.keys())
            h_sel = st.selectbox("Select Home Team", team_list, key="h_sel")
            a_sel = st.selectbox("Select Away Team", team_list, key="a_sel")
            home_str  = st.session_state.standings.get(h_sel, 1.0)
            away_str  = st.session_state.standings.get(a_sel, 1.0)
            home_name = h_sel
            away_name = a_sel
            st.caption(f"Derived — Home: **{home_str:.3f}** | Away: **{away_str:.3f}**")
        else:
            home_str = st.slider("Home Strength", 0.5, 2.5, 1.0, 0.05,
                                 help="1.0 = league average. Click Auto-Load for real data.")
            away_str = st.slider("Away Strength", 0.5, 2.5, 1.0, 0.05)

    with c3:
        st.markdown("**Bookmaker Odds (for value detection)**")
        bookie_home = st.number_input("Home Win Odds", 1.01, 50.0, 2.00, 0.05, key="bh")
        bookie_draw = st.number_input("Draw Odds",     1.01, 50.0, 3.30, 0.05, key="bd")
        bookie_away = st.number_input("Away Win Odds", 1.01, 50.0, 3.80, 0.05, key="ba")

    if st.button("⚡  CALCULATE PREDICTION", use_container_width=True):
        res = predict_match(LEAGUE_CODES[league], home_str, away_str)
        st.session_state.last_res = {
            'res':  res,
            'home': home_name,
            'away': away_name,
            'bh':   bookie_home,
            'bd':   bookie_draw,
            'ba':   bookie_away,
            'hs':   home_str,
            'as_':  away_str,
        }
        st.toast("Prediction ready!", icon="🔮")

    # ── Results (rendered outside button block to avoid nesting) ──────────────
    if st.session_state.last_res:
        d  = st.session_state.last_res
        r  = d['res']
        hn = d['home']
        an = d['away']

        # Probability metrics
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("HOME WIN",  f"{r['home']:.1%}",  f"Fair odds: {r['h_odds']:.2f}")
        m2.metric("DRAW",      f"{r['draw']:.1%}",  f"Fair odds: {r['d_odds']:.2f}")
        m3.metric("AWAY WIN",  f"{r['away']:.1%}",  f"Fair odds: {r['a_odds']:.2f}")
        m4.metric("BTTS",      f"{r['btts']:.1%}")
        m5.metric("OVER 2.5",  f"{r['over25']:.1%}")

        # Charts
        ch1, ch2, ch3 = st.columns(3)
        with ch1:
            st.plotly_chart(prob_bar(r, hn, an), use_container_width=True)
        with ch2:
            st.plotly_chart(score_heatmap(r['matrix']), use_container_width=True)
        with ch3:
            st.plotly_chart(team_radar(hn, an, d['hs'], d['as_']), use_container_width=True)

        # Top correct scores
        st.markdown("#### 🎯 Most Likely Correct Scores")
        score_df = pd.DataFrame(r['top_scores'], columns=['H', 'A', 'Prob'])
        score_df['Score']       = score_df.apply(lambda row: f"{int(row.H)}-{int(row.A)}", axis=1)
        score_df['Probability'] = score_df['Prob'].map('{:.2%}'.format)
        st.dataframe(score_df[['Score', 'Probability']], use_container_width=True, hide_index=True)

        # Value analysis
        st.markdown("#### 💰 Value Bet Analysis")
        for label, prob, b_odds in [
            ("Home Win", r['home'], d['bh']),
            ("Draw",     r['draw'], d['bd']),
            ("Away Win", r['away'], d['ba']),
        ]:
            edge, is_val = value_analysis(prob, b_odds)
            kelly        = kelly_stake(prob, b_odds, st.session_state.bankroll)
            css, icon    = ("value-box", "✅") if is_val else ("no-value", "❌")
            st.markdown(
                f
