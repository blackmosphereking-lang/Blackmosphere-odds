# api.py – Data Sources & Odds API Integration

import requests
import pandas as pd
from datetime import date
from config import FOOTBALL_DATA_API_KEY, LEAGUE_PARAMS, COSMIC_ENABLED, COSMIC_API_KEY
from models import predict_match

# ──足球数据.org API Clients ────────────────────────────────────────────────
# Fixed for app.py import

def fetch_matches(league_code: str, date_from: str, date_to: str) -> pd.DataFrame:
    """Fetch matches from football-data.org API."""
    try:
        url = f"https://v4.api.football-data.org/v4/competitions/{league_code}/matches"
        params = {"dateFrom": date_from, "dateTo": date_to, "status": "SCHEDULED"}
        headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return pd.json_normalize(response.json().get("matches", []))
    except Exception as e:
        st.error(f"Football-data.org API Error: {e}")
        return pd.DataFrame()

def fetch_standings(league_code: str) -> pd.DataFrame:
    """Fetch league standings from football-data.org API."""
    try:
        url = f"https://v4.api.football-data.org/v4/competitions/{league_code}/standings"
        headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return pd.json_normalize(response.json().get("standings", []))
    except Exception as e:
        st.error(f"Football-data.org Error: {e}")
        return pd.DataFrame()