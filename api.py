# ════════════════════════════════════════════════════════════════════════════
# FILE 4: api.py
# ════════════════════════════════════════════════════════════════════════════

import requests
from typing import Dict, List
from config import FOOTBALL_DATA_API_KEY, LEAGUE_PARAMS, DEFAULT_LEAGUE_PARAMS

# ── Football Data API ────────────────────────────────────────────────────


def fetch_matches(api_key: str = None, days: int = 7) -> List[Dict]:
    """
    Fetch upcoming matches from Football-Data.org.

    Args:
        api_key: Optional override; defaults to config value.
        days: Not used by the v4 endpoint but kept for compatibility.

    Returns:
        List of match dicts, or empty list on failure.
    """
    key = api_key or FOOTBALL_DATA_API_KEY
    if not key:
        return []
    try:
        url = "https://api.football-data.org/v4/matches"
        headers = {"X-Auth-Token": key}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("matches", [])
    except requests.RequestException:
        return []
    except (ValueError, KeyError):
        return []


def fetch_standings(api_key: str = None, league_code: str = "PL") -> Dict[str, float]:
    """
    Fetch league standings and return team strength ratings.

    Strength is derived from table position:
        1st place ≈ 2.0, last place ≈ 0.1

    Args:
        api_key: Optional override; defaults to config value.
        league_code: Football-Data.org competition code (e.g. "PL").

    Returns:
        Dict mapping team name -> strength float, or empty dict on failure.
    """
    key = api_key or FOOTBALL_DATA_API_KEY
    if not key:
        return {}
    try:
        url = (
            f"https://api.football-data.org/v4/competitions/"
            f"{league_code}/standings"
        )
        headers = {"X-Auth-Token": key}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        standings: Dict[str, float] = {}
        tables = data.get("standings", [])
        if tables:
            table = tables[0].get("table", [])
            total_teams = len(table) if table else 20
            for entry in table:
                team_name = entry.get("team", {}).get("name", "")
                position = entry.get("position", total_teams)
                strength = round(
                    2.0 * (1.0 - (position - 1) / total_teams), 2
                )
                strength = max(strength, 0.1)
                standings[team_name] = strength
        return standings
    except requests.RequestException:
        return {}
    except (ValueError, KeyError):
        return {}


def get_league_params(league_code: str) -> Dict:
    """Get prediction parameters for a specific league."""
    return LEAGUE_PARAMS.get(league_code, DEFAULT_LEAGUE_PARAMS)