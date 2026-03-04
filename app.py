# app.py — Blackmosphere FootMob Edition (hardened for Streamlit Cloud)

import streamlit as st
from datetime import datetime, date
from typing import Dict, List, Any, Callable, Tuple, Optional

# --------------------------------------------------------------------
# Safe imports (so the UI can still load even if a module is broken)
# --------------------------------------------------------------------

def _safe_import_config() -> Dict[str, Any]:
    """
    Returns a dict-like object of config values with sane defaults.
    Avoids hard-crashing if config.py has missing names or import issues.
    """
    cfg: Dict[str, Any] = {
        "CSS": "",
        "LEAGUE_CODES": {},          # mapping display league name -> code (e.g., "Premier League"->"PL")
        "RG_WARNING": "",
    }
    try:
        import config as _config
        cfg["CSS"] = getattr(_config, "CSS", cfg["CSS"])
        cfg["LEAGUE_CODES"] = getattr(_config, "LEAGUE_CODES", cfg["LEAGUE_CODES"])
        cfg["RG_WARNING"] = getattr(_config, "RG_WARNING", cfg["RG_WARNING"])
    except Exception as e:
        st.sidebar.error(f"⚠️ Config import failed: {type(e).__name__}: {str(e)}")
    return cfg

def _safe_import_models() -> Tuple[Callable, Callable]:
    """
    Returns predict_match and kelly_stake callables (or safe fallbacks).
    """
    def _fallback_predict_match(league: str, home_strength: float, away_strength: float) -> Dict[str, float]:
        # very simple fallback so app stays alive
        home = 0.40
        draw = 0.30
        away = 0.30
        # naive odds from probability (avoid division by zero)
        h_odds = round(1 / max(home, 1e-9), 2)
        return {"home": home, "draw": draw, "away": away, "h_odds": h_odds}

    def _fallback_kelly_stake(*_args, **_kwargs) -> float:
        return 0.0

    predict = _fallback_predict_match
    kelly = _fallback_kelly_stake

    try:
        from models import predict_match as _predict_match, kelly_stake as _kelly_stake
        predict = _predict_match
        kelly = _kelly_stake
    except Exception as e:
        st.sidebar.warning(f"⚠️ Models import failed (using fallback): {type(e).__name__}: {str(e)}")

    return predict, kelly

def _safe_import_api() -> Tuple[Callable, Callable]:
    """
    Returns fetch_matches and fetch_standings callables (or safe fallbacks).
    """
    def _fallback_fetch_matches(_api_key: str, days: int = 7) -> List[Dict[str, Any]]:
        return []

    def _fallback_fetch_standings(_api_key: str, _league_code: str) -> Dict[str, float]:
        return {}

    fetch_m = _fallback_fetch_matches
    fetch_s = _fallback_fetch_standings

    try:
        from api import fetch_matches as _fetch_matches, fetch_standings as _fetch_standings
        fetch_m = _fetch_matches
        fetch_s = _fetch_standings
    except Exception as e:
        st.sidebar.warning(f"⚠️ API import failed (using fallback): {type(e).__name__}: {str(e)}")

    return fetch_m, fetch_s

# Optional sources (SofaScore)
try:
    from sources import sofa_today_events
    SOFA_OK = True
except Exception:
    SOFA_OK = False

# --------------------------------------------------------------------
# Load config + functions (safe)
# --------------------------------------------------------------------
CFG = _safe_import_config()
CSS = CFG["CSS"]
LEAGUE_CODES = CFG["LEAGUE_CODES"] if isinstance(CFG["LEAGUE_CODES"], dict) else {}
RG_WARNING = CFG["RG_WARNING"]

predict_match, kelly_stake = _safe_import_models()
fetch_matches, fetch_standings = _safe_import_api()

# --------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------
st.set_page_config(
    page_title="Blackmosphere | AI + Cosmic Predictions",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

if CSS:
    st.markdown(CSS, unsafe_allow_html=True)

# --------------------------------------------------------------------
# SESSION STATE DEFAULTS
# --------------------------------------------------------------------
_defaults = {
    "parlay": [],
    "bankroll": 1000.0,
    "bet_history": [],
    "selected_date": date.today(),
    "cosmic_toggle": True,
    "value_threshold": 0.05,
    "filters": {"show_value_only": False, "min_probability": 0.0},
}

for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")

# --------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------
def load_today_matches() -> Dict[str, List[Dict[str, Any]]]:
    """Load matches grouped by league."""
    # If no API key, attempt SofaScore
    if not API_KEY:
        if SOFA_OK:
            events = sofa_today_events()
            if not events:
                return {}
            grouped: Dict[str, List[Dict[str, Any]]] = {}
            for e in events:
                league = (
                    e.get("tournament", {})
                    .get("category", {})
                    .get("name", "Other")
                )
                grouped.setdefault(league, [])
                grouped[league].append(
                    {
                        "id": e.get("id") or f"sofa_{league}_{len(grouped[league])}",
                        "home": e.get("homeTeam", {}).get("name", "TBD"),
                        "away": e.get("awayTeam", {}).get("name", "TBD"),
                        "home_id": e.get("homeTeam", {}).get("id", 0),
                        "away_id": e.get("awayTeam", {}).get("id", 0),
                        "time": e.get("time", "00:00"),
                        "league": league,
                        "venue": e.get("venue", {}).get("name", "TBD"),
                        "status": "Scheduled",
                    }
                )
            return grouped
        return {}

    # Use your API wrapper
    matches = fetch_matches(API_KEY, days=7) or []
    if not isinstance(matches, list):
        return {}

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for m in matches:
        league = m.get("competition", "Other")
        grouped.setdefault(league, [])

        utc = m.get("utcDate", "")
        try:
            dt = datetime.fromisoformat(str(utc).replace("Z", "+00:00"))
            time_str = dt.strftime("%H:%M")
        except (ValueError, TypeError):
            time_str = "00:00"

        status_val = m.get("status")
        # handle both string status and dict status shapes
        if isinstance(status_val, dict):
            status_str = status_val.get("description", "Scheduled")
        else:
            status_str = str(status_val) if status_val is not None else "Scheduled"

        grouped[league].append(
            {
                "id": m.get("id") or f"api_{league}_{len(grouped[league])}",
                "home": m.get("homeTeam", {}).get("name", "TBD"),
                "away": m.get("awayTeam", {}).get("name", "TBD"),
                "home_id": m.get("homeTeam", {}).get("id", 0),
                "away_id": m.get("awayTeam", {}).get("id", 0),
                "time": time_str,
                "league": league,
                "venue": "Stadium",
                "status": status_str,
            }
        )
    return grouped


def get_team_strength(team_name: str, league_code: str = "PL") -> float:
    """Get team strength from standings map; fallback to 1.0."""
    if not API_KEY:
        return 1.0
    standings = fetch_standings(API_KEY, league_code) or {}
    if not isinstance(standings, dict):
        return 1.0
    return float(standings.get(team_name, 1.0))


def calculate_value(prob: float, odds: float) -> Tuple[float, bool]:
    """Calculate edge and value status."""
    if odds <= 0:
        return 0.0, False
    implied = 1 / odds
    edge = prob - implied
    is_value = edge > float(st.session_state.value_threshold)
    return float(edge), bool(is_value)


def add_to_slip(name: str, odds: float, prob: float) -> None:
    """Add selection to bet slip."""
    st.session_state.parlay.append(
        {"name": name, "odds": round(float(odds), 2), "prob": round(float(prob), 4)}
    )

# --------------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------------
st.sidebar.markdown(
    """
    <div class="sidebar-logo">
        <div class="logo-icon">⚽</div>
        <div class="logo-text">
            <h2>Blackmosphere</h2>
            <span>AI + Cosmic Predictions</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    f"""
    <div class="bankroll-card">
        <div class="label">Bankroll</div>
        <div class="amount">${st.session_state.bankroll:.2f}</div>
    </div>
 