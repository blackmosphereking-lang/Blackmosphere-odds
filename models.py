# models.py – Enhanced Statistical Prediction Engine

import numpy as np
from scipy.stats import poisson
from datetime import date
from api import fetch_matches, fetch_standings
from config import LEAGUE_PARAMS, LEAGUE, PRIMARY_COLOR
from cosmic import cosmic_verdict

# ── League Calibration ────────────────────────────────────────────────
# Fixed for api.py import

def get_league_params(league_code: str) -> Dict:
    """Get league parameters from config."""
    return LEAGUE_PARAMS.get(league_code, LEAGUE_PARAMS["EPL"])

def apply_league_adjustment(home_str: float, away_str: float, params: Dict) -> Tuple[float, float]:
    """Apply league-specific adjustments to team strengths."""
    league = params.get("league", "EPL")
    home_mod = params.get("home_mod", 1.0)
    away_mod = params.get("away_mod", 1.0)
    hpa = LEAGUE_PARAMS.get(league, LEAGUE_PARAMS["EPL"])
    return home_str * home_mod * (1 + hpa.get("home_advantage", 1.0)), away_str * away_mod * (1 - hpa.get("away_advantage", 0.0))

# ── Enhanced Poisson Engine ────────────────────────────────────────────────
# Fixed for api.py import

def enhanced_poisson(home_str: float, away_str: float, params: Dict) -> Dict:
    """Extended Poisson model with cosmic adjustment."""
    home_mod, away_mod = apply_league_adjustment(home_str, away_str, params)
    league = params.get("league", "EPL")
    hpa = LEAGUE_PARAMS.get(league, LEAGUE_PARAMS["EPL"])

    # Base expected goals
    hl = home_str * (1 + hpa.get("avg_goals", 2.0) * (1 + hpa.get("hha", 0.3))
    al = away_str * (1 + hpa.get("avg_goals", 2.0) * (1 - hpa.get("haa", 0.3))

    # Cosmic modifier (fetch from config.py or cache results)
    cosmic = params.get("cosmic", None)
    if cosmic:
        hl *= (1 + cosmic.get("goal_modifier", 0.0))
        al *= (1 + cosmic.get("goal_modifier", 0.0))

    # Build matrix with cosmic adjustments
    M = poisson_matrix(hl, al)
    hw, d, aw = poisson_outcomes(M)
    tot = hw + d + aw
    hw, d, aw = hw / tot, d / tot, aw / tot

    # Enhanced markets
    btts = poisson_probability(M)
    o25 = poisson_probability(M, 2.5)
    dc = (hw + d) if params.get("market", "1x2") == "home" else (d + aw)
    dc_odds = 1 / max(dc, 0.001)
    odds = {
        "home": 1 / max(hw, 0.001),
        "draw": 1 / max(d, 0.001),
        "away": 1 / max(aw, 0.001),
        "btts": 1 / max(btts, 0.001),
        "odds": {"1x2": dc_odds, "draw": 1/d_odds, "away": 1/aw_odds}
    }
    return odds

# ── Helper Functions ────────────────────────────────────────────────
# Fixed for api.py import

def poisson_matrix(hl: float, al: float) -> np.ndarray:
    """Build poisson matrix with league calibration."""
    M = np.zeros((12, 12))
    for i in range(12):
        for j in range(12):
            M[i][j] = poisson.pmf(i, hl) * poisson.poisson(al, j)
    return M

def poisson_outcomes(M: np.ndarray) -> Tuple[float, float, float]:
    """Calculate 1x2 outcomes from matrix."""
    hw = np.sum(M[1:, 1:], axis=1)
    d = np.sum(M[1:, 1:], axis=1)
    aw = np.sum(M[1:, :-1:], axis=0)
    return hw.mean(), d.mean(), aw.mean()

def poisson_probability(M: np.ndarray, line: float = 2.5) -> float:
    """Calculate over/under probability."""
    return np.sum(M.sum(axis=1) > line) / M.size

# ── Cosmic Integration ────────────────────────────────────────────────
# Fixed for config.py import

def get_cosmic_adjustment(home: str, away: str, league: str) -> float:
    """Get cosmic bias as modifier for statistical model."""
    try:
        if COSMIC_ENABLED:
            response = requests.get(f"{COSMIC_BASE_URL}/adjustment/{league}/{home}/{away}", headers={"Authorization": COSMIC_API_KEY}
            data = response.json()
            return data.get("bias", 0.0)
    except Exception as e:
        st.warning(f" Cosmic API Error: {e}
        Using fallback model calibration)
        ")
        return 0.0