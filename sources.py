# ════════════════════════════════════════════════════════════════════════════
# FILE 5: sources.py (optional — SofaScore fallback)
# ════════════════════════════════════════════════════════════════════════════

import requests
from typing import Dict, List, Optional
from datetime import date

# ── SofaScore API (unofficial, may break) ─────────────────────────────────

SOFA_BASE = "https://api.sofascore.com/api/v1"


def sofa_today_events() -> List[Dict]:
    """
    Fetch today's football events from SofaScore.

    Returns:
        List of event dicts, or empty list on failure.
    """
    today = date.today().isoformat()
    url = f"{SOFA_BASE}/sport/football/scheduled-events/{today}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("events", [])
    except requests.RequestException:
        return []
    except (ValueError, KeyError):
        return []


def sofa_team_last5(team_id: int) -> List[Dict]:
    """
    Fetch the last 5 matches for a team from SofaScore.

    Args:
        team_id: SofaScore team ID.

    Returns:
        List of recent match dicts, or empty list on failure.
    """
    if not team_id:
        return []
    url = f"{SOFA_BASE}/team/{team_id}/events/last/0"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        events = data.get("events", [])
        return events[:5]
    except requests.RequestException:
        return []
    except (ValueError, KeyError):
        return []