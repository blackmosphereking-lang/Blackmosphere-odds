# models.py — Blackmosphere FootMob Edition
# Match prediction model and Kelly Criterion staking

import math
from typing import Dict

# ════════════════════════════════════════════════════════════════════════════
# MATCH PREDICTION
# ════════════════════════════════════════════════════════════════════════════

def predict_match(league: str, home_strength: float, away_strength: float) -> Dict[str, float]:
    """
    Predict match outcome probabilities using strength ratings.

    Args:
        league: League name (e.g. "Premier League")
        home_strength: Home team strength rating (0.0 - 2.0+)
        away_strength: Away team strength rating (0.0 - 2.0+)

    Returns:
        Dict with keys: 'home', 'draw', 'away', 'h_odds', 'd_odds', 'a_odds'
    """
    # Home advantage factor
    HOME_ADVANTAGE = 1.25

    # Adjusted strengths
    adj_home = home_strength * HOME_ADVANTAGE
    adj_away = away_strength

    # Prevent division by zero
    total = adj_home + adj_away
    if total <= 0:
        total = 2.0
        adj_home = 1.0
        adj_away = 1.0

    # Raw win probabilities
    home_raw = adj_home / total
    away_raw = adj_away / total

    # Draw probability derived from how close the teams are in strength
    strength_diff = abs(adj_home - adj_away)
    draw_base = 0.26  # Average draw rate in top leagues
    draw_prob = max(0.08, draw_base - (strength_diff * 0.12))

    # Scale home/away to account for draw probability
    remaining = 1.0 - draw_prob
    home_prob = home_raw * remaining
    away_prob = away_raw * remaining

    # Normalize to ensure probabilities sum to 1.0
    prob_total = home_prob + draw_prob + away_prob
    home_prob /= prob_total
    draw_prob /= prob_total
    away_prob /= prob_total

    # Convert to decimal odds (with margin for realism)
    margin = 1.05  # 5% bookmaker margin
    h_odds = round(margin / home_prob, 2) if home_prob > 0 else 99.0
    d_odds = round(margin / draw_prob, 2) if draw_prob > 0 else 99.0
    a_odds = round(margin / away_prob, 2) if away_prob > 0 else 99.0

    return {
        'home': round(home_prob, 4),
        'draw': round(draw_prob, 4),
        'away': round(away_prob, 4),
        'h_odds': h_odds,
        'd_odds': d_odds,
        'a_odds': a_odds,
    }


# ════════════════════════════════════════════════════════════════════════════
# KELLY CRITERION STAKING
# ════════════════════════════════════════════════════════════════════════════

def kelly_stake(
    probability: float,
    odds: float,
    bankroll: float,
    fraction: float = 0.25
) -> float:
    """
    Calculate recommended stake using fractional Kelly Criterion.

    Args:
        probability: Estimated true probability of outcome (0.0 - 1.0)
        odds: Decimal odds offered by bookmaker (e.g. 2.50)
        bankroll: Current bankroll amount
        fraction: Kelly fraction to use (default 0.25 = quarter-Kelly)

    Returns:
        Recommended stake amount (floored to 0 if negative edge)
    """
    if odds <= 1.0 or probability <= 0.0 or probability >= 1.0 or bankroll <= 0:
        return 0.0

    # Kelly formula: f* = (bp - q) / b
    # where b = odds - 1, p = win probability, q = 1 - p
    b = odds - 1.0
    p = probability
    q = 1.0 - p

    kelly_fraction = (b * p - q) / b

    # No bet if negative edge
    if kelly_fraction <= 0:
        return 0.0

    # Apply fractional Kelly and round to 2 decimal places
    stake = round(bankroll * kelly_fraction * fraction, 2)

    # Cap at bankroll
    return min(stake, bankroll)