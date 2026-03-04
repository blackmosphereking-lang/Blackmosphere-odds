# config.py - Configuration constants for Blackmosphere FootMob

# CSS styling for the app
CSS = """
<style>
    .sidebar-logo {
        display: flex;
        align-items: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid #444;
    }
    .logo-icon {
        font-size: 2.5rem;
        margin-right: 0.5rem;
    }
    .logo-text h2 {
        margin: 0;
        font-size: 1.5rem;
        color: #FFD700;
    }
    .logo-text span {
        color: #AAA;
        font-size: 0.85rem;
    }
    .bankroll-card {
        background: #1E1E1E;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    .bankroll-card .label {
        color: #AAA;
        font-size: 0.9rem;
    }
    .bankroll-card .amount {
        font-size: 1.8rem;
        font-weight: bold;
        color: #FFD700;
    }
    .responsible-banner {
        background: #3A0E0E;
        color: #FFAAAA;
        padding: 0.75rem;
        border-radius: 6px;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    .main-header {
        background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.2rem;
    }
    .main-header p {
        color: #DDD;
        margin: 0.5rem 0 0;
    }
    .stMetric {
        background: #1E1E1E;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .stMetric label {
        font-size: 1rem;
        color: #AAA;
    }
    .stMetric .st-emotion-cache-1wivap2 {
        font-size: 1.8rem;
        color: #FFD700;
    }
</style>
"""

# League codes mapping (display name -> API code)
LEAGUE_CODES = {
    "Premier League": "PL",
    "La Liga": "PD",
    "Serie A": "SA",
    "Bundesliga": "BL1",
    "Ligue 1": "FL1",
    "Champions League": "CL",
    "Europa League": "EL",
    "EFL Championship": "CH",
    "Other": "OT"
}

# Responsible gambling warning
RG_WARNING = "⚠️ This app is for entertainment purposes only. Gambling involves risk. Never bet more than you can afford to lose."