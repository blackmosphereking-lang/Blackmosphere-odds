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
            h_sel     = st.selectbox("Select Home Team", team_list, key="h_sel")
            a_sel     = st.selectbox("Select Away Team", team_list, key="a_sel")
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

    if st.button("⚡ CALCULATE PREDICTION", use_container_width=True):
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

    # ── Results — rendered outside button block to avoid nesting issues ────────
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

        # Top correct scores table
        st.markdown("#### 🎯 Most Likely Correct Scores")
        score_df = pd.DataFrame(r['top_scores'], columns=['H', 'A', 'Prob'])
        score_df['Score']       = score_df.apply(lambda row: f"{int(row.H)}-{int(row.A)}", axis=1)
        score_df['Probability'] = score_df['Prob'].map('{:.2%}'.format)
        st.dataframe(score_df[['Score', 'Probability']], use_container_width=True, hide_index=True)

        # Value bet analysis
        st.markdown("#### 💰 Value Bet Analysis")
        markets = [
            ("Home Win", r['home'], d['bh']),
            ("Draw",     r['draw'], d['bd']),
            ("Away Win", r['away'], d['ba']),
        ]
        for label, prob, b_odds in markets:
            edge, is_val = value_analysis(prob, b_odds)
            kelly        = kelly_stake(prob, b_odds, st.session_state.bankroll)
            css          = "value-box" if is_val else "no-value"
            icon         = "✅" if is_val else "❌"
            st.markdown(
                f"<div class='{css}'>"
                f"{icon} <b>{label}</b> &nbsp;|&nbsp; "
                f"Model: {prob:.1%} &nbsp;|&nbsp; "
                f"Bookie implied: {1/b_odds:.1%} &nbsp;|&nbsp; "
                f"Edge: {edge:+.1%} &nbsp;|&nbsp; "
                f"Kelly Stake: <b>${kelly}</b>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # Add to Gold Ticket
        st.markdown("#### ➕ Add Leg to Gold Ticket")
        market_opts = {
            "Home Win":  (r['home'],   r['h_odds']),
            "Draw":      (r['draw'],   r['d_odds']),
            "Away Win":  (r['away'],   r['a_odds']),
            "BTTS":      (r['btts'],   r['btts_odds']),
            "Over 2.5":  (r['over25'], r['over25_odds']),
        }
        chosen = st.selectbox("Select Market", list(market_opts.keys()), key="mkt_sel")
        sel_prob, sel_odds = market_opts[chosen]

        if st.button("➕ ADD TO GOLD TICKET", use_container_width=True):
            st.session_state.parlay.append({
                'name': f"{hn} vs {an} — {chosen}",
                'odds': sel_odds,
                'prob': sel_prob,
            })
            st.toast(f"Added: {chosen} @ {sel_odds:.2f}", icon="🎯")
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FIXTURES
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### ⚽ Upcoming Fixtures")

    col_slider, col_refresh = st.columns([4, 1])
    days = col_slider.slider("Days ahead", 1, 14, 7)
    if col_refresh.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

    matches = fetch_matches(API_KEY, days)

    if not API_KEY:
        st.error("API key missing. Add FOOTBALL_API_KEY to `.streamlit/secrets.toml`.")
    elif not matches:
        st.warning("No fixtures returned. You may have hit the free-tier rate limit — try again in a minute.")
    else:
        st.caption(f"{len(matches)} fixtures found")
        for m in matches[:20]:
            comp  = m['competition']['name']
            hteam = m['homeTeam']['name']
            ateam = m['awayTeam']['name']
            utc   = m.get('utcDate', '')[:16].replace('T', ' ')

            with st.expander(f"⚽  {hteam}  vs  {ateam}   |   {comp}   |   {utc} UTC"):
                fa1, fa2 = st.columns(2)

                if fa1.button("🔮 Analyze", key=f"an_{m['id']}"):
                    code = LEAGUE_CODES.get(comp, 'PL')
                    r    = predict_match(code)
                    mc1, mc2, mc3, mc4 = st.columns(4)
                    mc1.metric("Home",    f"{r['home']:.1%}")
                    mc2.metric("Draw",    f"{r['draw']:.1%}")
                    mc3.metric("Away",    f"{r['away']:.1%}")
                    mc4.metric("BTTS",    f"{r['btts']:.1%}")
                    st.plotly_chart(prob_bar(r, hteam, ateam), use_container_width=True)

                if fa2.button("➕ Add Home Win", key=f"add_{m['id']}"):
                    code = LEAGUE_CODES.get(comp, 'PL')
                    r    = predict_match(code)
                    st.session_state.parlay.append({
                        'name': f"{hteam} vs {ateam} — Home Win",
                        'odds': r['h_odds'],
                        'prob': r['home'],
                    })
                    st.toast(f"Added {hteam} Home Win @ {r['h_odds']:.2f}", icon="🎯")
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — GOLD TICKET
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🎯 YOUR GOLD TICKET")

    if not st.session_state.parlay:
        st.info("No legs added yet. Use the Predictor or Fixtures tabs to build your ticket.")
    else:
        total_odds    = 1.0
        combined_prob = 1.0

        for i, leg in enumerate(st.session_state.parlay):
            lc1, lc2, lc3 = st.columns([6, 1, 1])
            lc1.write(f"🔸 {leg['name']}")
            lc2.markdown(f"**{leg['odds']:.2f}**")
            if lc3.button("✕", key=f"rm_{i}", help="Remove this leg"):
                st.session_state.parlay.pop(i)
                st.rerun()
            total_odds    *= leg['odds']
            combined_prob *= leg.get('prob', 0.5)

        st.divider()
        tm1, tm2, tm3 = st.columns(3)
        tm1.metric("TOTAL ODDS",    f"{total_odds:.2f}")
        tm2.metric("COMBINED PROB", f"{combined_prob:.2%}")
        tm3.metric("EXPECTED VALUE", f"{combined_prob * total_odds:.3f}x",
                   delta="Value" if combined_prob * total_odds >= 1.0 else "No value",
                   delta_color="normal" if combined_prob * total_odds >= 1.0 else "inverse")

        st.divider()
        stake     = st.number_input("Stake ($)", min_value=1.0, max_value=10000.0,
                                    value=10.0, step=1.0)
        potential = stake * total_odds
        profit    = potential - stake

        st.markdown(
            f"<h3>💰 Potential Return: ${potential:,.2f} "
            f"<span style='color:#888;font-size:16px;'>(Profit: ${profit:,.2f})</span></h3>",
            unsafe_allow_html=True,
        )

        bc1, bc2 = st.columns(2)
        if bc1.button("✅ LOG BET", use_container_width=True):
            st.session_state.bet_history.append({
                'Date':       datetime.now().strftime('%Y-%m-%d %H:%M'),
                'Legs':       len(st.session_state.parlay),
                'Odds':       round(total_odds, 2),
                'Stake ($)':  stake,
                'Potential':  round(potential, 2),
                'Model Prob': f"{combined_prob:.2%}",
                'Result':     'Pending',
            })
            # Deduct stake from bankroll immediately on logging
            st.session_state.bankroll  -= stake
            st.session_state.parlay     = []
            st.toast("Bet logged! Settle it in the Bankroll tab.", icon="✅")
            st.rerun()

        if bc2.button("🗑️ CLEAR TICKET", use_container_width=True):
            st.session_state.parlay = []
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — BANKROLL
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 📊 Bankroll Management")

    br1, br2 = st.columns(2)
    with br1:
        new_br = st.number_input(
            "Set / Reset Bankroll ($)",
            min_value=0.0, max_value=1_000_000.0,
            value=st.session_state.bankroll,
            step=50.0,
        )
        if st.button("💾 UPDATE BANKROLL"):
            st.session_state.bankroll = new_br
            st.toast(f"Bankroll updated to ${new_br:,.2f}", icon="💰")
            st.rerun()
    br2.metric("Current Bankroll", f"${st.session_state.bankroll:,.2f}")

    st.divider()
    st.markdown("### 📋 Bet History")

    if not st.session_state.bet_history:
        st.info("No bets logged yet. Build a ticket and click LOG BET.")
    else:
        # Settle bets
        st.markdown("**Settle a bet:**")
        sc1, sc2, sc3 = st.columns(3)
        idx    = sc1.number_input("Row #", min_value=0,
                                  max_value=max(0, len(st.session_state.bet_history) - 1),
                                  step=1, value=0)
        result = sc2.selectbox("Result", ["Pending", "Won", "Lost", "Void"])

        if sc3.button("✅ SETTLE"):
            bet = st.session_state.bet_history[int(idx)]
            if bet['Result'] != 'Pending':
                st.warning("This bet is already settled.")
            else:
                bet['Result'] = result
                if result == 'Won':
                    # Return full payout (stake was already deducted on log)
                    st.session_state.bankroll += bet['Potential']
                    st.toast(f"Bet settled as WON! +${bet['Potential']:,.2f}", icon="🏆")
                elif result == 'Void':
                    # Stake refunded
                    st.session_state.bankroll += bet['Stake ($)']
                    st.toast("Bet voided — stake refunded.", icon="↩️")
                else:
                    st.toast("Bet settled as LOST.", icon="❌")
                st.rerun()

        # History table
        hist_df = pd.DataFrame(st.session_state.bet_history)
        st.dataframe(hist_df, use_container_width=True, hide_index=True)

        # Summary metrics
        st.divider()
        total_staked = sum(b['Stake ($)']  for b in st.session_state.bet_history)
        won_count    = sum(1 for b in st.session_state.bet_history if b['Result'] == 'Won')
        lost_count   = sum(1 for b in st.session_state.bet_history if b['Result'] == 'Lost')
        pending      = sum(1 for b in st.session_state.bet_history if b['Result'] == 'Pending')

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Total Staked",   f"${total_staked:,.2f}")
        s2.metric("Bets Won",       won_count)
        s3.metric("Bets Lost",      lost_count)
        s4.metric("Pending",        pending)

        # P&L chart
        fig = pnl_chart(st.session_state.bet_history)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        # CSV export
        st.divider()
        csv = hist_df.to_csv(index=False)
        st.download_button(
            label="📥 Export Bet History as CSV",
            data=csv,
            file_name=f"blackmosphere_bets_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
)
