# models.py — Poisson-Based Statistical Prediction Engine

import math
from typing import Dict, List, Tuple, Optional

# ══════════════════════════════════════════════════════════════════════════════
# LEAGUE PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════

_LEAGUE = {
    "PL": {"hg": 1.53, "ag": 1.17, "hha": 0.35, "corner_base": 10.8, "booking_base": 3.2},
    "PD": {"hg": 1.62, "ag": 1.20, "hha": 0.30, "corner_base": 9.8, "booking_base": 3.5},
    "BL1": {"hg": 1.65, "ag": 1.30, "hha": 0.32, "corner_base": 10.2, "booking_base": 3.0},
    "SA": {"hg": 1.45, "ag": 1.12, "hha": 0.28, "corner_base": 9.6, "booking_base": 3.8},
    "FL1": {"hg": 1.48, "ag": 1.18, "hha": 0.30, "corner_base": 9.4, "booking_base": 3.6},
    "UCL": {"hg": 1.72, "ag": 1.25, "hha": 0.25, "corner_base": 10.0, "booking_base": 2.8},
    "UEL": {"hg": 1.60, "ag": 1.22, "hha": 0.28, "corner_base": 9.5, "booking_base": 3.0},
}
_DEF = {"hg": 1.50, "ag": 1.15, "hha": 0.30, "corner_base": 10.0, "booking_base": 3.2}

# ══════════════════════════════════════════════════════════════════════════════
# POISSON FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def poisson_prob(lam: float, k: int) -> float:
    """Calculate Poisson probability P(X=k) for lambda."""
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def _matrix(h: float, a: float, mx: int = 8) -> List[List[float]]:
    """Build probability matrix for all score combinations."""
    return [[poisson_prob(h, i) * poisson_prob(a, j) for j in range(mx + 1)] for i in range(mx + 1)]

def _outcomes(M: List[List[float]]) -> Tuple[float, float, float]:
    """Extract 1X2 probabilities from score matrix."""
    n = len(M)
    hw = sum(M[i][j] for i in range(1, n) for j in range(i))
    d = sum(M[i][i] for i in range(n))
    aw = sum(M[i][j] for j in range(1, n) for i in range(j))
    tot = hw + d + aw
    return hw / tot, d / tot, aw / tot

def _over(M: List[List[float]], line: float = 2.5) -> float:
    """Calculate over probability for a given line."""
    n = len(M)
    return sum(M[i][j] for i in range(n) for j in range(n) if i + j > line)

def _btts(M: List[List[float]]) -> float:
    """Both teams to score probability."""
    n = len(M)
    return sum(M[i][j] for i in range(1, n) for j in range(1, n))

def _top_scores(M: List[List[float]], n: int = 8) -> List[Tuple]:
    """Get top N most likely correct scores."""
    scores = [(M[i][j], i, j) for i in range(len(M)) for j in range(len(M[0]))]
    scores.sort(reverse=True)
    return [(i, j, round(p, 4)) for p, i, j in scores[:n]]

# ══════════════════════════════════════════════════════════════════════════════
# HALFTIME / HIGHEST HALF
# ══════════════════════════════════════════════════════════════════════════════

def _halftime(h_lam: float, a_lam: float) -> Dict:
    """Calculate halftime probabilities (45% of full time)."""
    hh, ah = h_lam * 0.45, a_lam * 0.45
    M = _matrix(hh, ah, 5)
    hw, d, aw = _outcomes(M)
    over05 = 1 - M[0][0]
    return {
        "home": round(hw, 4), "draw": round(d, 4), "away": round(aw, 4),
        "over05": round(over05, 4),
        "h_odds": round(1 / max(hw, 0.01), 2),
        "d_odds": round(1 / max(d, 0.01), 2),
        "a_odds": round(1 / max(aw, 0.01), 2)
    }

def _highest_half(h_lam: float, a_lam: float) -> Dict:
    """Calculate which half has more goals."""
    h1, a1 = h_lam * 0.45, a_lam * 0.45
    h2, a2 = h_lam * 0.55, a_lam * 0.55
    exp1, exp2 = h1 + a1, h2 + a2
    denom = exp1 + exp2 + 0.5
    p_first = round(exp1 / denom, 4)
    p_equal = round(0.5 / denom, 4)
    p_second = round(exp2 / denom, 4)
    return {
        "first": p_first, "equal": p_equal, "second": p_second,
        "first_odds": round(1 / max(p_first, 0.01), 2),
        "equal_odds": round(1 / max(p_equal, 0.01), 2),
        "second_odds": round(1 / max(p_second, 0.01), 2),
        "pick": "1st Half" if p_first > p_second else "2nd Half"
    }

# ══════════════════════════════════════════════════════════════════════════════
# CORNERS & BOOKINGS
# ══════════════════════════════════════════════════════════════════════════════

def _corners(league: str, hs: float, as_: float) -> Dict:
    """Calculate corner probabilities."""
    L = _LEAGUE.get(league, _DEF)
    base = L['corner_base']
    exp = base * ((hs + as_) / 2.0)
    markets = {}
    for line in (8.5, 9.5, 10.5, 11.5, 12.5):
        over = sum(poisson_prob(exp, k) for k in range(int(line) + 1, 30))
        under = 1.0 - over
        markets[line] = {
            "over": round(over, 4), "over_odds": round(1 / max(over, 0.01), 2),
            "under": round(under, 4), "under_odds": round(1 / max(under, 0.01), 2),
        }
    return {"expected": round(exp, 2), "markets": markets}

def _bookings(league: str, hs: float, as_: float) -> Dict:
    """Calculate booking probabilities."""
    L = _LEAGUE.get(league, _DEF)
    base = L['booking_base']
    exp_y = base * ((hs + as_) / 2.0)
    exp_bp = exp_y * 10 * 1.05
    cards = {}
    for line in (1.5, 2.5, 3.5, 4.5):
        ov = sum(poisson_prob(exp_y, k) for k in range(int(line) + 1, 20))
        cards[line] = {
            "over": round(ov, 4), "over_odds": round(1 / max(ov, 0.01), 2),
            "under": round(1 - ov, 4), "under_odds": round(1 / max(1 - ov, 0.01), 2),
        }
    bp = {}
    for line in (19.5, 29.5, 39.5, 49.5):
        ov = sum(poisson_prob(exp_bp / 10, k) for k in range(int(line / 10) + 1, 30))
        bp[line] = {
            "over": round(ov, 4), "over_odds": round(1 / max(ov, 0.01), 2),
            "under": round(1 - ov, 4), "under_odds": round(1 / max(1 - ov, 0.01), 2),
        }
    return {"exp_yellows": round(exp_y, 2), "exp_bp": round(exp_bp, 1), "cards": cards, "points": bp}

# ══════════════════════════════════════════════════════════════════════════════
# MAIN PREDICTION FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def predict_match(
    league: str = "PL",
    home_str: float = 1.0,
    away_str: float = 1.0,
    xg_home: Optional[float] = None,
    xg_away: Optional[float] = None,
    cosmic_bias: float = 0.0,
    goal_modifier: float = 0.0
) -> Dict:
    """Generate full prediction for a match."""
    
    L = _LEAGUE.get(league, _DEF)
    
    # Calculate expected goals (lambda)
    hl = (xg_home if xg_home else L['hg'] * home_str) * (1 + L['hha'])
    al = (xg_away if xg_away else L['ag'] * away_str)
    
    # Apply cosmic bias
    hl = max(0.1, hl * (1 + cosmic_bias * 0.15))
    al = max(0.1, al * (1 - cosmic_bias * 0.10))
    
    # Build score matrix
    M = _matrix(hl, al)
    hw, d, aw = _outcomes(M)
    tot = hw + d + aw
    hw, d, aw = hw / tot, d / tot, aw / tot
    
    # Goals markets
    btts = _btts(M)
    o25 = _over(M, 2.5)
    o15 = _over(M, 1.5)
    o35 = _over(M, 3.5)
    o45 = _over(M, 4.5)
    o05 = _over(M, 0.5)
    
    # Halftime
    ht = _halftime(hl, al)
    hh = _highest_half(hl, al)
    
    # Corners & Bookings
    corner = _corners(league, home_str, away_str)
    book = _bookings(league, home_str, away_str)
    
    # Top scores
    top_sc = _top_scores(M)
    
    # Double chance
    dc_1x = hw + d
    dc_x2 = d + aw
    dc_12 = hw + aw
    
    return {
        # 1X2
        "home": hw, "draw": d, "away": aw,
        "h_odds": round(1 / max(hw, 0.001), 2),
        "d_odds": round(1 / max(d, 0.001), 2),
        "a_odds": round(1 / max(aw, 0.001), 2),
        
        # Double Chance
        "dc_1x": dc_1x, "dc_x2": dc_x2, "dc_12": dc_12,
        "dc_1x_odds": round(1 / max(dc_1x, 0.001), 2),
        "dc_x2_odds": round(1 / max(dc_x2, 0.001), 2),
        "dc_12_odds": round(1 / max(dc_12, 0.001), 2),
        
        # BTTS
        "btts": btts, "btts_odds": round(1 / max(btts, 0.001), 2),
        "no_btts_odds": round(1 / max(1 - btts, 0.001), 2),
        
        # Goals
        "over05": o05, "over15": o15, "over25": o25, "over35": o35, "over45": o45,
        "over05_odds": round(1 / max(o05, 0.001), 2),
        "over15_odds": round(1 / max(o15, 0.001), 2),
        "over25_odds": round(1 / max(o25, 0.001), 2),
        "over35_odds": round(1 / max(o35, 0.001), 2),
        "over45_odds": round(1 / max(o45, 0.001), 2),
        "under25": 1 - o25, "under25_odds": round(1 / max(1 - o25, 0.001), 2),
        
        # Halftime
        "halftime": ht,
        
        # Highest Half
        "highest_half": hh,
        
        # Corners & Bookings
        "corners": corner,
        "bookings": book,
        
        # Correct Scores
        "top_scores": top_sc,
        "matrix": M,
        
        # Expected Goals
        "h_lam": round(hl, 3), "a_lam": round(al, 3),
    }

# ══════════════════════════════════════════════════════════════════════════════
# KELLY CRITERION
# ══════════════════════════════════════════════════════════════════════════════

def kelly_stake(prob: float, odds: float, bankroll: float, fraction: float = 0.25) -> float:
    """Calculate Kelly stake amount."""
    edge = prob * odds - 1.0
    if edge <= 0:
        return 0.0
    k = edge / (odds - 1.0)
    return round(k * fraction * bankroll, 2)