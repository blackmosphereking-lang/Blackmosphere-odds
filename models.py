# models.py — Poisson prediction engine, Kelly Criterion, value analysis

import numpy as np
from scipy.stats import poisson
from config import LEAGUE_PARAMS


def predict_match(league_code: str, home_str: float = 1.0, away_str: float = 1.0) -> dict:
    """
    Bivariate Poisson model with league-calibrated home advantage.

    λ_home = (avg_goals/2) × home_str × exp(home_adv/2) / away_str
    λ_away = (avg_goals/2) × away_str / (home_str × exp(home_adv/2))

    Returns probabilities, fair odds, 9×9 score matrix, and top correct scores.
    """
    p    = LEAGUE_PARAMS.get(league_code, LEAGUE_PARAMS['PL'])
    base = p['avg_goals'] / 2
    adv  = np.exp(p['home_adv'] / 2)

    h_lam = base * home_str * adv / away_str
    a_lam = base * away_str / (home_str * adv)

    N      = 9
    matrix = np.outer(
        poisson.pmf(np.arange(N), h_lam),
        poisson.pmf(np.arange(N), a_lam),
    )

    p_home = float(np.sum(np.tril(matrix, -1)))
    p_draw = float(np.sum(np.diag(matrix)))
    p_away = float(np.sum(np.triu(matrix, 1)))
    btts   = float(np.sum(matrix[1:, 1:]))
    over25 = float(sum(
        matrix[i, j] for i in range(N) for j in range(N) if i + j > 2
    ))

    top_scores = sorted(
        [(i, j, matrix[i, j]) for i in range(6) for j in range(6)],
        key=lambda x: x[2],
        reverse=True,
    )[:6]

    def fair_odds(p):
        return round(1 / p, 2) if p > 0 else 99.0

    return {
        'home':        p_home,
        'draw':        p_draw,
        'away':        p_away,
        'h_odds':      fair_odds(p_home),
        'd_odds':      fair_odds(p_draw),
        'a_odds':      fair_odds(p_away),
        'btts':        btts,
        'btts_odds':   fair_odds(btts),
        'over25':      over25,
        'over25_odds': fair_odds(over25),
        'matrix':      matrix,
        'top_scores':  top_scores,
        'h_lam':       h_lam,
        'a_lam':       a_lam,
    }


def kelly_stake(prob: float, bookie_odds: float, bankroll: float, fraction: float = 0.25) -> float:
    """
    Quarter-Kelly criterion for conservative stake sizing.
    Returns 0.0 when there is no positive edge.
    """
    if bookie_odds <= 1:
        return 0.0
    edge = prob * bookie_odds - 1
    if edge <= 0:
        return 0.0
    return round(bankroll * (edge / (bookie_odds - 1)) * fraction, 2)


def value_analysis(model_prob: float, bookie_odds: float):
    """
    Returns (edge, is_value).
    A bet has value when the model edge is >= 5% above the bookmaker's implied probability.
    """
    edge = model_prob - (1 / bookie_odds)
    return edge, edge >= 0.05
