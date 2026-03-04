# ════════════════════════════════════════════════════════════════════════════
# FILE 2: models.py
# ════════════════════════════════════════════════════════════════════════════

from typing import Dict
from config import LEAGUE_CODES, LEAGUE_PARAMS, DEFAULT_LEAGUE_PARAMS

# ── Match Prediction ──────────────────────────────────────────────────────


def predict_match(
    league: str, home_strength: float, away_strength: float
) -> Dict[str, float]:
    """
    Predict match outcome probabilities using strength ratings.

    Args:
        league: League name (e.g. "Premier League")
        home_strength: Home team strength rating (0.0 - 2.0+)
        away_strength: Away team strength rating (0.0 - 2.0+)

    Returns:
        Dict with keys: home, draw, away, h_odds, d_odds, a_odds
    """
    # Look up league-specific parameters
    league_code = LEAGUE_CODES.get(league, "PL")
    params = LEAGUE_PARAMS.get(league_code, DEFAULT_LEAGUE_PARAMS)

    home_adv = params["home_adv"]
    draw_base = params["draw_base"]

    # Adjusted strengths
    adj_home = home_strength * home_adv
    adj_away = away_strength

    # Prevent division by zero
    total = adj_home + adj_away
    if total <= 0:
        adj_home = 1.0
        adj_away = 1.0
        total = 2.0

    # Raw win probabilities
    home_raw = adj_home / total
    away_raw = adj_away / total

    # Draw probability — closer teams draw more often
    strength_diff = abs(adj_home - adj_away)
    draw_prob = max(0.08, draw_base - (strength_diff * 0.12))

    # Scale home/away to fill remaining probability
    remaining = 1.0 - draw_prob
    home_prob = home_raw * remaining
    away_prob = away_raw * remaining

    # Normalize so all three sum to 1.0
    prob_total = home_prob + draw_prob + away_prob
    home_prob /= prob_total
    draw_prob /= prob_total
    away_prob /= prob_total

    # Convert to decimal odds (5% bookmaker margin)
    margin = 1.05
    h_odds = round(margin / home_prob, 2) if home_prob > 0 else 99.0
    d_odds = round(margin / draw_prob, 2) if draw_prob > 0 else 99.0
    a_odds = round(margin / away_prob, 2) if away_prob > 0 else 99.0

    return {
        "home": round(home_prob, 4),
        "draw": round(draw_prob, 4),
        "away": round(away_prob, 4),
        "h_odds": h_odds,
        "d_odds": d_odds,
        "a_odds": a_odds,
    }


# ── Kelly Criterion Staking ──────────────────────────────────────────────


def kelly_stake(
    probability: float,
    odds: float,
    bankroll: float,
    fraction: float = 0.25,
) -> float:
    """
    Calculate recommended stake using fractional Kelly Criterion.

    Args:
        probability: Estimated true probability of outcome (0.0 - 1.0)
        odds: Decimal odds offered by bookmaker (e.g. 2.50)
        bankroll: Current bankroll amount
        fraction: Kelly fraction (default 0.25 = quarter-Kelly)

    Returns:
        Recommended stake amount (0.0 if negative edge)
    """
    if odds <= 1.0 or probability <= 0.0 or probability >= 1.0 or bankroll <= 0:
        return 0.0

    # Kelly formula: f* = (bp - q) / b
    b = odds - 1.0
    p = probability
    q = 1.0 - p

    kelly_f = (b * p - q) / b

    if kelly_f <= 0:
        return 0.0

    stake = round(bankroll * kelly_f * fraction, 2)
    return min(stake, bankroll)