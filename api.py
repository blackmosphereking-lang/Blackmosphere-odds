# api.py — Football-Data.org API wrappers

import streamlit as st
import requests
from datetime import datetime, timedelta
from config import BASE_URL


def _headers(api_key: str) -> dict:
    return {'X-Auth-Token': api_key} if api_key else {}


@st.cache_data(ttl=600)
def fetch_matches(api_key: str, days_ahead: int = 7) -> list:
    """Fetch SCHEDULED matches for the next N days."""
    if not api_key:
        return []
    try:
        r = requests.get(
            f"{BASE_URL}/matches",
            headers=_headers(api_key),
            params={
                'dateFrom': datetime.now().strftime('%Y-%m-%d'),
                'dateTo':   (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d'),
                'status':   'SCHEDULED',
            },
            timeout=10,
        )
        r.raise_for_status()
        return r.json().get('matches', [])
    except Exception:
        return []


@st.cache_data(ttl=3600)
def fetch_standings(api_key: str, competition_code: str) -> dict:
    """
    Returns {team_name: strength_rating} derived from goals for/against
    relative to the league average.  1.0 = perfectly average team.
    """
    if not api_key:
        return {}
    try:
        r = requests.get(
            f"{BASE_URL}/competitions/{competition_code}/standings",
            headers=_headers(api_key),
            timeout=10,
        )
        r.raise_for_status()
        standings = r.json().get('standings', [])

        # Prefer TOTAL standings; fall back to first entry
        table = next(
            (s['table'] for s in standings if s.get('type') == 'TOTAL'),
            standings[0].get('table', []) if standings else [],
        )
        if not table:
            return {}

        avg_gf = sum(t['goalsFor']     for t in table) / len(table)
        avg_ga = sum(t['goalsAgainst'] for t in table) / len(table)

        strengths = {}
        for team in table:
            attack   = team['goalsFor']     / avg_gf if avg_gf > 0 else 1.0
            defense  = avg_ga / team['goalsAgainst'] if team['goalsAgainst'] > 0 else 1.0
            strengths[team['team']['name']] = round((attack + defense) / 2, 3)

        return strengths
    except Exception:
        return {}
