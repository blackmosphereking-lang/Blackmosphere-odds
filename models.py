# models.py - Prediction models for match outcomes

from typing import Dict, Any
import random

def predict_match(league: str, home_strength: float, away_strength: float) -> Dict[str, Any]:
    """
    Predict match outcome probabilities based on team strengths.
    Returns a dictionary with probabilities and calculated odds.
    """
    try:
        # Base probabilities (will be adjusted by strength difference)
        base_home = 0.45
        base_draw = 0.28
        base_away = 0.27
        
        # Calculate strength difference (normalized)
        strength_diff = (home_strength - away_strength) / max(home_strength + away_strength, 1)
        
        # Adjust probabilities based on strength difference
        home_prob = base_home + (strength_diff * 0.3)
        away_prob = base_away - (strength_diff * 0.3)
        
        # Ensure probabilities stay within reasonable bounds
        home_prob = max(0.1, min(0.8, home_prob))
        away_prob = max(0.1, min(0.8, away_prob))
        
        # Calculate draw probability as the remainder
        draw_prob = 1.0 - home_prob - away_prob
        draw_prob = max(0.1, min(0.4, draw_prob))
        
        # Recalculate to ensure sum is exactly 1.0
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        draw_prob /= total
        away_prob /= total
        
        # Calculate implied odds (with margin)
        home_odds = round(1.0 / home_prob * 1.05, 2)  # 5% margin
        
        return {
            "home": home_prob,
            "draw": draw_prob,
            "away": away_prob,
            "h_odds": home_odds,
            "d_odds": round(1.0 / draw_prob * 1.05, 2),
            "a_odds": round(1.0 / away_prob * 1.05, 2)
        }
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        # Return safe fallback values
        return {
            "home": 0.40,
            "draw": 0.30,
            "away": 0.30,
            "h_odds": 2.50,
            "d_odds": 3.33,
            "a_odds": 3.33
        }

def kelly_stake(probability: float, odds: float, bankroll: float = 1000.0, kelly_fraction: float = 0.5) -> float:
    """
    Calculate optimal stake using the Kelly Criterion.
    Returns stake as a percentage of bankroll.
    """
    try:
        if odds <= 1.0 or probability <= 0 or probability >= 1:
            return 0.0
            
        # Kelly formula: f = (bp - q) / b
        # where b = odds - 1, p = probability, q = 1 - p
        b = odds - 1
        p = probability
        q = 1 - p
        
        kelly_percent = (b * p - q) / b
        
        # Only bet if positive expectation
        if kelly_percent <= 0:
            return 0.0
            
        # Apply fraction of Kelly (to reduce volatility)
        stake_percent = kelly_percent * kelly_fraction
        
        return min(stake_percent, 0.1)  # Cap at 10% of bankroll
    except Exception as e:
        print(f"Kelly calculation error: {str(e)}")
        return 0.0