# sources.py — Multi-source data integration
# Free sources: SofaScore (unofficial), StatsBomb Open Data
# Key required: Pinnacle
# Enterprise:   Betgenius, Modelo/Sportradar, Betegy

import requests
import streamlit as st
from datetime import date
from typing import Dict, List, Optional, Any, Tuple

# ══════════════════════════════════════════════════════════════════════════════
# SOFASCORE  — Unofficial public API (no key required)
# ══════════════════════════════════════════════════════════════════════════════
_SOFA     = "https://api.sofascore.com/api/v1"
_SOFA_HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept":     "application/json",
    "Referer":    "https://www.sofascore.com/",
}

@st.cache_data(ttl=300)
def sofa_today_events() -> List[Dict]:
    """All football events scheduled for today."""
    try:
        r = requests.get(
            f"{_SOFA}/sport/football/scheduled-events/{date.today().isoformat()}",
            headers=_SOFA_HDR, timeout=10,
        )
        r.raise_for_status()
        return r.json().get("events", [])
    except Exception:
        return []

@st.cache_data(ttl=300)
def sofa_event_prediction(event_id: int) -> Optional[Dict]:
    """SofaScore AI prediction for a specific event."""
    try:
        r = requests.get(
            f"{_SOFA}/event/{event_id}/prediction",
            headers=_SOFA_HDR, timeout=8,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

@st.cache_data(ttl=300)
def sofa_search_team(name: str) -> Optional[int]:
    """Search SofaScore and return team ID."""
    try:
        r = requests.get(f"{_SOFA}/search/all/", params={"q": name},
                         headers=_SOFA_HDR, timeout=8)
        r.raise_for_status()
        for item in r.json().get("results", []):
            if item.get("type") == "team":
                return item["entity"]["id"]
    except Exception:
        pass
    return None

@st.cache_data(ttl=300)
def sofa_team_last5(team_id: int) -> Optional[Dict]:
    """Goal averages from last 5 matches via SofaScore."""
    try:
        r = requests.get(f"{_SOFA}/team/{team_id}/events/last/0",
                         headers=_SOFA_HDR, timeout=8)
        r.raise_for_status()
        events = r.json().get("events", [])[:5]
        gf = gc = 0
        for e in events:
            hs  = e.get("homeScore", {}).get("current", 0) or 0
            as_ = e.get("awayScore", {}).get("current", 0) or 0
            if e.get("homeTeam", {}).get("id") == team_id:
                gf += hs;  gc += as_
            else:
                gf += as_; gc += hs
        n = len(events)
        return {
            "goals_scored_avg":   round(gf / n, 2) if n else None,
            "goals_conceded_avg": round(gc / n, 2) if n else None,
            "games": n,
        }
    except Exception:
        return None

@st.cache_data(ttl=300)
def sofa_h2h(event_id: int) -> Optional[Dict]:
    """Head-to-head data for a SofaScore event."""
    try:
        r = requests.get(f"{_SOFA}/event/{event_id}/h2h",
                         headers=_SOFA_HDR, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# STATSBOMB OPEN DATA  — GitHub raw JSON (no key required)
# ══════════════════════════════════════════════════════════════════════════════
_SB = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

@st.cache_data(ttl=3600)
def sb_competitions() -> List[Dict]:
    try:
        r = requests.get(f"{_SB}/competitions.json", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []

@st.cache_data(ttl=3600)
def sb_matches(competition_id: int, season_id: int) -> List[Dict]:
    try:
        r = requests.get(f"{_SB}/matches/{competition_id}/{season_id}.json", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []

@st.cache_data(ttl=3600)
def sb_team_xg(team_name: str, competition_id: int = 2, season_id: int = 27) -> Dict:
    """
    Derive xG proxies from StatsBomb open data match scores.
    (True xG is in event-level data; this uses match scores as a calibration proxy.)
    """
    matches = sb_matches(competition_id, season_id)
    xg_for = xg_against = n = 0

    for m in matches:
        ht = m.get("home_team", {}).get("home_team_name", "")
        at = m.get("away_team", {}).get("away_team_name", "")
        hs = m.get("home_score", 0) or 0
        as_ = m.get("away_score", 0) or 0

        if team_name.lower() in ht.lower():
            xg_for += hs;  xg_against += as_;  n += 1
        elif team_name.lower() in at.lower():
            xg_for += as_; xg_against += hs;   n += 1

    if n == 0:
        return {"xg_for": None, "xg_against": None, "games": 0}
    return {
        "xg_for":     round(xg_for / n, 3),
        "xg_against": round(xg_against / n, 3),
        "games":      n,
    }


# ══════════════════════════════════════════════════════════════════════════════
# PINNACLE  — Public odds API (requires free Pinnacle account)
# Register: https://www.pinnacle.