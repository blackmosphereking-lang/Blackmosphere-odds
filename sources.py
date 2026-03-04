# sources.py - Optional SofaScore integration

import requests
from typing import List, Dict, Any

def sofa_today_events() -> List[Dict[str, Any]]:
    """
    Fetch today's events from SofaScore API (free tier).
    Returns empty list on failure.
    """
    try:
        url = "https://api.sofascore.com/api/v1/sport/football/events/live"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        events = []
        if "events" in data:
            for event in data["events"]:
                events.append({
                    "id": event["id"],
                    "time": event.get("startTimestamp", 0),
                    "homeTeam": {
                        "id": event["homeTeam"]["id"],
                        "name": event["homeTeam"]["name"]
                    },
                    "awayTeam": {
                        "id": event["awayTeam"]["id"],
                        "name": event["awayTeam"]["name"]
                    },
                    "tournament": {
                        "category": {
                            "name": event["tournament"]["category"]["name"]
                        }
                    },
                    "venue": {
                        "name": event.get("venue", {}).get("stadium", {}).get("name", "Unknown Venue")
                    }
                })
        return events
    except Exception as e:
        print(f"SofaScore API error: {str(e)}")
        return []

def sofa_team_last5(team_id: int) -> List[Dict[str, Any]]:
    """
    Fetch last 5 matches for a team from SofaScore.
    Returns empty list on failure.
    """
    try:
        url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/5"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        events = []
        if "events" in data:
            for event in data["events"]:
                events.append({
                    "id": event["id"],
                    "homeTeam": event["homeTeam"]["name"],
                    "awayTeam": event["awayTeam"]["name"],
                    "homeScore": event["homeScore"]["current"],
                    "awayScore": event["awayScore"]["current"],
                    "tournament": event["tournament"]["name"]
                })
        return events
    except Exception as e:
        print(f"SofaScore team history error: {str(e)}")
        return []