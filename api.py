# api.py - Football data API integration

import requests
import time
from typing import Dict, List, Any

def fetch_matches(api_key: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    Fetch upcoming matches from Football Data API.
    Returns empty list on failure to prevent app crashes.
    """
    try:
        headers = {"X-Auth-Token": api_key}
        url = f"http://api.football-data.org/v4/matches?dateFrom={time.strftime('%Y-%m-%d')}&dateTo={time.strftime('%Y-%m-%d', time.localtime(time.time() + days * 86400))}"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "matches" in data:
            return data["matches"]
        return []
    except Exception as e:
        print(f"API Error fetching matches: {str(e)}")
        return []

def fetch_standings(api_key: str, league_code: str) -> Dict[str, float]:
    """
    Fetch league standings and calculate team strength metrics.
    Returns empty dict on failure.
    """
    try:
        headers = {"X-Auth-Token": api_key}
        url = f"http://api.football-data.org/v4/competitions/{league_code}/standings"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        standings = {}
        if "standings" in data and len(data["standings"]) > 0:
            for team in data["standings"][0]["table"]:
                team_name = team["team"]["name"]
                # Simple strength metric: points + goal difference / 10
                points = team["points"]
                goal_diff = team["goalDifference"]
                standings[team_name] = points + (goal_diff / 10.0)
                
        return standings
    except Exception as e:
        print(f"API Error fetching standings: {str(e)}")
        return {}