# config.py — League data, constants, and CSS theme

LEAGUE_CODES = {
    'Premier League': 'PL',
    'Bundesliga':     'BL1',
    'Serie A':        'SA',
    'La Liga':        'PD',
    'Ligue 1':        'FL1',
    'Eredivisie':     'DED',
}

LEAGUE_PARAMS = {
    'PL':  {'home_adv': 0.32, 'avg_goals': 2.85},
    'BL1': {'home_adv': 0.45, 'avg_goals': 3.25},
    'SA':  {'home_adv': 0.35, 'avg_goals': 2.45},
    'PD':  {'home_adv': 0.38, 'avg_goals': 2.60},
    'FL1': {'home_adv': 0.33, 'avg_goals': 2.75},
    'DED': {'home_adv': 0.42, 'avg_goals': 3.40},
}

BASE_URL = "https://api.football-data.org/v4"

CSS = """
<style>
    .stApp {
        background-color: #000000;
        background-image: radial-gradient(circle at 50% -20%, #1a1a1a, #000000);
    }
    h1, h2, h3 {
        color: #D4AF37 !important;
        text-shadow: 0 0 15px rgba(212,175,55,0.3);
        font-family: serif;
        letter-spacing: 2px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #AA8418 100%) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 5px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        width: 100%;
    }
    [data-testid="stMetric"] {
        background: rgba(212,175,55,0.05) !important;
        border: 1px solid #D4AF37 !important;
        padding: 15px !important;
        border-radius: 10px !important;
    }
    .stMarkdown, p, span { color: #e0e0e0 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #000; }
    .stTabs [data-baseweb="tab"]      { color: #888; }
    .stTabs [aria-selected="true"]    { color: #D4AF37 !important;
                                        border-bottom-color: #D4AF37 !important; }
    .value-box {
        background: rgba(212,175,55,0.12);
        border-left: 4px solid #D4AF37;
        padding: 12px; border-radius: 6px; margin: 8px 0;
    }
    .no-value {
        background: rgba(255,60,60,0.08);
        border-left: 4px solid #c0392b;
        padding: 12px; border-radius: 6px; margin: 8px 0;
    }
</style>
"""
