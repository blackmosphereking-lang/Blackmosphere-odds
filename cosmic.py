# cosmic.py - Cosmic prediction enhancements

from datetime import datetime
from typing import Dict, Any

def cosmic_verdict(home_team: str, away_team: str, base_prediction: Dict[str, float]) -> Dict[str, float]:
    """
    Apply cosmic factors to adjust base prediction probabilities.
    Currently a placeholder that makes minor adjustments based on team names.
    """
    try:
        # In a real implementation, this would use actual cosmic data
        # For now, we'll make very minor adjustments based on team name length
        # as a placeholder for more sophisticated logic
        
        home_factor = len(home_team) % 3 / 100
        away_factor = len(away_team) % 3 / 100
        
        # Adjust probabilities slightly
        home_prob = base_prediction["home"] + home_factor - away_factor
        away_prob = base_prediction["away"] + away_factor - home_factor
        
        # Ensure probabilities stay within bounds
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
        
        return {
            "home": home_prob,
            "draw": draw_prob,
            "away": away_prob
        }
    except Exception as e:
        print(f"Cosmic verdict error: {str(e)}")
        # Return the original prediction if cosmic calculation fails
        return base_prediction