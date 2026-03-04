# sources.py — External Data Sources Integration
# SofaScore (unofficial), StatsBomb Open Data

import requests
import streamlit as st
from datetime import date
from typing import Dict, List, Optional

# ══════════════════════════════════════════════════════════════════════════════
# SOFASCORE - Unofficial Public API
# ══════════════════════════════════════════════════════════════════════════════

_SOFA = "https://api.sofascore.com/api/v1"
_SOFA_HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.sofascore.com/",
}

@st.cache_data(ttl=300)
def sofa_today_events() -> List[Dict]:
    """Get all football events for today."""
    try:
        r = requests.get(
            f"{_SOFA}/sport/football/scheduled-events/{date.today().isoformat()}",
            headers=_SOFA_HDR, timeout=10
        )
        r.raise_for_status()
        return r.json().get("events", [])
    except Exception as e:
        st.warning(f"SofaScore error: {e}")
        return []

@st.cache_data(ttl=300)
def sofa_event_prediction(event_id: int) -> Optional[Dict]:
    """Get AI prediction for a specific event."""
    try:
        r = requests.get(f"{_SOFA}/event/{event_id}/prediction", headers=_SOFA_HDR, timeout=8)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

@st.cache_data(ttl=300)
def sofa_team_last5(team_id: int) -> Optional[Dict]:
    """Get last 5 matches for a team."""
    try:
        r = requests.get(f"{_SOFA}/team/{team_id}/events/last/0", headers=_SOFA_HDR, timeout=8)
        r.raise_for_status()
        events = r.json().get("events", [])[:5]
        gf = gc = 0
        for e in events:
            hs = e.get("homeScore", {}).get("current", 0) or 0
            as_ = e.get("awayScore", {}).get("current", 0) or 0
            if e.get("homeTeam", {}).get("id") == team_id:
                gf += hs
                gc += as_
            else:
                gf += as_
                gc += hs
        n = len(events)
        if n == 0:
            return None
        return {
            "goals_scored_avg": round(gf / n, 2),
            "goals_conceded_avg": round(gc / n, 2),
            "games": n,
        }
    except:
        return None

@st.cache_data(ttl=300)
def sofa_search_team(name: str) -> Optional[int]:
    """Search for team ID by name."""
    try:
        r = requests.get(f"{_SOFA}/search/all/", params={"q": name}, headers=_SOFA_HDR, timeout=8)
        r.raise_for_status()
        for item in r.json().get("results", []):
            if item.get("type") == "team":
                return item["entity"]["id"]
    except:
        pass
    return None

@st.cache_data(ttl=300)
def sofa_h2h(event_id: int) -> Optional[Dict]:
    """Get head-to-head data."""
    try:
        r = requests.get(f"{_SOFA}/event/{event_id}/h2h", headers=_SOFA_HDR, timeout=8)
        r.raise_for_status()
        return r.json()
    except:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# STATSBOMB - Open Data (Free)
# ══════════════════════════════════════════════════════════════════════════════

_SB = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

@st.cache_data(ttl=3600)
def sb_competitions() -> List[Dict]:
    """Get available competitions."""
    try:
        r = requests.get(f"{_SB}/competitions.json", timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return []

@st.cache_data(ttl=3600)
def sb_matches(competition_id: int, season_id: int) -> List[Dict]:
    """Get matches for a competition season."""
    try:
        r = requests.get(f"{_SB}/matches/{competition_id}/{season_id}.json", timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return []

@st.cache_data(ttl=3600)
def sb_team_xg(team_name: str, competition_id: int = 2, season_id: int = 27) -> Dict:
    """Derive xG from StatsBomb match data."""
    matches = sb_matches(competition_id, season_id)
    xg_for = xg_against = n = 0
    
    for m in matches:
        ht = m.get("home_team", {}).get("home_team_name", "")
        at = m.get("away_team", {}).get("away_team_name", "")
        hs = m.get("home_score", 0) or 0
        as_ = m.get("away_score", 0) or 0
        
        if team_name.lower() in ht.lower():
            xg_for += hs
            xg_against += as_
            n += 1
        elif team_name.lower() in at.lower():
            xg_for += as_
            xg_against += hs
            n += 1
    
    if n == 0:
        return {"xg_for": None, "xg_against": None, "games": 0}
    return {
        "xg_for": round(xg_for / n, 3),
        "xg_against": round(xg_against / n, 3),
        "games": n,
    }


# ══════════════════════════════════════════════════════════════════════════════
# PINNACLE - Odds API (Requires Account)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def pinnacle_odds(api_key: str, sport_id: int = 29) -> List[Dict]:
    """Get live odds from Pinnacle."""
    if not api_key:
        return []
    
    try:
        import base64
        auth = base64.b64encode(api_key.encode()).decode()
        hdr = {"Authorization": f"Basic {auth}"}
        r = requests.get(
            f"https://api.pinnacle.com/v1/odds?sportId={sport_id}",
            headers=hdr, timeout=10
        )
        r.raise_for_status()
        return r.json().get("leagues", [])
    except:
        return []