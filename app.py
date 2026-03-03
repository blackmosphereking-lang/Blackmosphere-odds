def predict_match_outcome(match, market):
    """
    Predict the outcome of a match based on various betting markets.

    Args:
        match (dict): Information about the match.
        market (str): The betting market to consider.

    Returns:
        str: Prediction for the specified market.
    """
    if market == '1X2':
        # Prediction logic for 1X2
        prediction = "Home Win" if match['home_score'] > match['away_score'] else "Away Win" if match['home_score'] < match['away_score'] else "Draw"
    elif market == 'Double Chance':
        # Prediction logic for Double Chance
        prediction = "Home or Draw" if match['home_score'] >= match['away_score'] else "Away or Draw"
    elif market == 'Draw No Bet':
        # Prediction logic for Draw No Bet
        prediction = "Home Win" if match['home_score'] > match['away_score'] else "Away Win" if match['home_score'] < match['away_score'] else "Void"
    elif market == 'Over/Under Goals':
        # Prediction logic for Over/Under Goals
        prediction = "Over" if match['total_goals'] > match['threshold'] else "Under"
    elif market == 'Correct Score':
        # Prediction logic for Correct Score
        prediction = f"{match['home_score']}:{match['away_score']}"
    elif market == 'Asian Handicap':
        # Prediction logic for Asian Handicap
        if match['home_score'] + match['handicap'] > match['away_score']:
            prediction = "Home Win"
        else:
            prediction = "Away Win"
    elif market == 'BTTS':  # Both Teams To Score
        prediction = "Yes" if match['home_score'] > 0 and match['away_score'] > 0 else "No"
    else:
        raise ValueError(f"Unknown market: {market}")
    return prediction
