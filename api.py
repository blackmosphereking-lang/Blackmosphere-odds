# config.py — Blackmosphere FootMob Edition (COMPLETE)

import streamlit as st

# ════════════════════════════════════════════════════════════════════════════
# API KEYS & SETTINGS (loaded from Streamlit secrets)
# ════════════════════════════════════════════════════════════════════════════

FOOTBALL_DATA_API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")
COSMIC_API_KEY = st.secrets.get("COSMIC_API_KEY", "")
COSMIC_ENABLED = True

# ════════════════════════════════════════════════════════════════════════════
# LEAGUE CODES (Football-Data.org competition codes)
# ════════════════════════════════════════════════════════════════════════════

LEAGUE_CODES = {
    "Premier League": "PL",
    "La Liga": "PD",
    "Bundesliga": "BL1",
    "Serie A": "SA",
    "Ligue 1": "FL1",
    "Eredivisie": "DED",
    "Primeira Liga": "PPL",
    "Championship": "ELC",
    "Champions League": "CL",
    "Europa League": "EL",
    "FIFA World Cup": "WC",
}

# ════════════════════════════════════════════════════════════════════════════
# LEAGUE PARAMS (per-league tuning for prediction model)
# ════════════════════════════════════════════════════════════════════════════

LEAGUE_PARAMS = {
    "PL":  {"home_adv": 1.25, "draw_base": 0.24, "avg_goals": 2.85},
    "PD":  {"home_adv": 1.20, "draw_base": 0.26, "avg_goals": 2.65},
    "BL1": {"home_adv": 1.28, "draw_base": 0.23, "avg_goals": 3.10},
    "SA":  {"home_adv": 1.22, "draw_base": 0.27, "avg_goals": 2.60},
    "FL1": {"home_adv": 1.23, "draw_base": 0.25, "avg_goals": 2.70},
    "DED": {"home_adv": 1.20, "draw_base": 0.24, "avg_goals": 3.00},
    "PPL": {"home_adv": 1.22, "draw_base": 0.25, "avg_goals": 2.55},
    "ELC": {"home_adv": 1.24, "draw_base": 0.27, "avg_goals": 2.60},
    "CL":  {"home_adv": 1.15, "draw_base": 0.25, "avg_goals": 2.90},
    "EL":  {"home_adv": 1.15, "draw_base": 0.26, "avg_goals": 2.75},
    "WC":  {"home_adv": 1.10, "draw_base": 0.26, "avg_goals": 2.50},
}

# Default params for unknown leagues
DEFAULT_LEAGUE_PARAMS = {"home_adv": 1.20, "draw_base": 0.26, "avg_goals": 2.70}

# ════════════════════════════════════════════════════════════════════════════
# CSS STYLES
# ════════════════════════════════════════════════════════════════════════════

CSS = """
<style>
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px;
    }
    .sidebar-logo .logo-icon {
        font-size: 2rem;
    }
    .sidebar-logo .logo-text h2 {
        margin: 0;
        color: #FFFFFF;
    }
    .sidebar-logo .logo-text span {
        color: #AAAAAA;
        font-size: 0.85rem;
    }
    .bankroll-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        text-align: center;
    }
    .bankroll-card .label {
        color: #AAAAAA;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    .bankroll-card .amount {
        color: #00FF88;
        font-size: 1.6rem;
        font-weight: bold;
    }
    .responsible-banner {
        background: rgba(255, 80, 80, 0.15);
        border: 1px solid rgba(255, 80, 80, 0.3);
        border-radius: 8px;
        padding: 12px;
        margin: 12px 0;
        font-size: 0.8rem;
        color: #FFAAAA;
    }
    .main-header {
        text-align: center;
        padding: 24px 0;
    }
    .main-header h1 {
        font-size: 2.4rem;
        margin: 0;
    }
    .main-header p {
        color: #AAAAAA;
        margin: 4px 0 0;
    }
</style>
"""

# ════════════════════════════════════════════════════════════════════════════
# RESPONSIBLE GAMBLING WARNING
# ════════════════════════════════════════════════════════════════════════════

RG_WARNING = (
    "⚠️ Gamble Responsibly: This tool is for entertainment and informational "
    "purposes only. It is not affiliated with any bookmaker. Never bet more "
    "than you can afford to lose. If you or someone you know has a gambling "
    "problem, please seek help at www.begambleaware.org or call 1-800-GAMBLER."
)