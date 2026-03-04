# config.py – App Configurations

import os
from typing import Dict, Optional

# ── API Keys ─────────────────────────────────────────────────────────────────

FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "")
SOFA_SCORE_API_KEY = os.getenv("SOFA_SCORE_API_KEY", "")
Pinnacle_API_KEY = os.getenv("PINNACLE_API_KEY", "")
STATSBOMB_API_KEY = os.getenv("STATSBOMB_API_KEY", "")

# ── League Parameters ────────────────────────────────────────────────────────
# (Fix for models.py)
LEAGUE_PARAMS = {
    "EPL": {"home_advantage": 1.4, "avg_goals": 2.7, "corner_base": 10.8, "booking_base": 3.2, "hha": 0.35},
    "La Liga": {"home_advantage": 1.3, "avg_goals": 2.5, "corner_base": 9.6, "booking_base": 3.5, "hha": 0.32},
    "Bundesliga": {"home_advantage": 1.2, "avg_goals": 2.0, "corner_base": 10.0, "booking_base": 3.0, "hha": 0.28},
    "Serie A": {"home_advantage": 1.1, "avg_goals": 2.2, "corner_base": 9.2, "booking_base": 3.8, "hha": 0.28},
    "Ligue 1": {"home_advantage": 1.0, "avg_goals": 2.3, "corner_base": 9.5, "booking_base": 3.6, "hha": 0.30},
    "Champions League": {"home_advantage": 1.5, "avg_goals": 2.4, "corner_base": 10.0, "booking_base": 2.8, "hha": 0.25},
    "UEFA Cup": {"home_advantage": 1.3, "avg_goals": 2.1, "corner_base": 9.7, "booking_base": 3.4, "hha": 0.29}
}

# ── Odds API Configuration ────────────────────────────────────────────────
# (Fix for api.py)
LEAGUE Odds API Keys (Pinnacle, SofaScore, etc.)
LEAGUE Odds API Base URLs
LEAGUE Odds API Endpoint Templates

# ── Prediction Calibration ────────────────────────────────────────────────
# (Fix for models.py)
LEAGUE Home Team Strength Multipliers
LEAGUE Away Team Strength Multipliers
LEAGUE Defensive Adjustments

# ── Responsible Gaming ────────────────────────────────────────────────
# (Fix for app.py)
RG_WARNING = """
⚠️ Gambling can be addictive. Play responsibly. View betting limits and help at:
<a href='https://www.gamblersanonymous.org' style='color:#D5A021;'>Gambler's Anonymous</a>
"""

# ── Cosmic Toggle ────────────────────────────────────────────────────────
# (Fix for cosmic.py)
COSMIC_ENABLED = True
COSMIC_BASE_URL = "https://cosmic.api.blackmosphere.ai"
COSMIC_API_KEY = os.getenv("COSMIC_API_KEY", "")

# ── UI Config ────────────────────────────────────────────────────────
# (Fix for app.py)
PRIMARY_COLOR = "#D5A021"  # Gold
PRIMARY_URL = "https://blackmosphere.ai"
BRANDING_URL = "https://blackmosphere.ai/branding/"

# ── Data Paths ────────────────────────────────────────────────────────
# (Fix for app.py)
DATA_PATHS = {
    "history": "data/history.parquet",
    "predictions": "data/predictions.parquet",
    "cosmic_cache": "data/cosmic.json"
}