# config.py — Blackmosphere FootMob Edition

# ════════════════════════════════════════════════════════════════════════════
# CSS STYLES
# ════════════════════════════════════════════════════════════════════════════

CSS = """
<style>
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px;
    }
    .sidebar-logo .logo-icon {
        font-size: 2rem;
    }
    .sidebar-logo .logo-text h2 {
        margin: 0;
        color: #FFFFFF;
    }
    .sidebar-logo .logo-text span {
        color: #AAAAAA;
        font-size: 0.85rem;
    }
    .bankroll-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        text-align: center;
    }
    .bankroll-card .label {
        color: #AAAAAA;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    .bankroll-card .amount {
        color: #00FF88;
        font-size: 1.6rem;
        font-weight: bold;
    }
    .responsible-banner {
        background: rgba(255, 80, 80, 0.15);
        border: 1px solid rgba(255, 80, 80, 0.3);
        border-radius: 8px;
        padding: 12px;
        margin: 12px 0;
        font-size: 0.8rem;
        color: #FFAAAA;
    }
    .main-header {
        text-align: center;
        padding: 24px 0;
    }
    .main-header h1 {
        font-size: 2.4rem;
        margin: 0;
    }
    .main-header p {
        color: #AAAAAA;
        margin: 4px 0 0;
    }
</style>
"""

# ════════════════════════════════════════════════════════════════════════════
# LEAGUE CODES (Football-Data.org competition codes)
# ════════════════════════════════════════════════════════════════════════════

LEAGUE_CODES = {
    "Premier League": "PL",
    "La Liga": "PD",
    "Bundesliga": "BL1",
    "Serie A": "SA",
    "Ligue 1": "FL1",
    "Eredivisie": "DED",
    "Primeira Liga": "PPL",
    "Championship": "ELC",
    "Champions League": "CL",
    "Europa League": "EL",
    "FIFA World Cup": "WC",
}

# ════════════════════════════════════════════════════════════════════════════
# LEAGUE Odds API Keys (Pinnacle, SofaScore, etc.)            <-- LINE 27 FIX
# ════════════════════════════════════════════════════════════════════════════

# Add any odds-related API keys or mappings here as needed.
# Example:
# ODDS_API_KEYS = {
#     "pinnacle": "your-pinnacle-key",
#     "sofascore": "your-sofascore-key",
# }

# ════════════════════════════════════════════════════════════════════════════
# RESPONSIBLE GAMBLING WARNING
# ════════════════════════════════════════════════════════════════════════════

RG_WARNING = (
    "⚠️ Gamble Responsibly: This tool is for entertainment and informational "
    "purposes only. It is not affiliated with any bookmaker. Never bet more "
    "than you can afford to lose. If you or someone you know has a gambling "
    "problem, please seek help at www.begambleaware.org or call 1-800-GAMBLER."
)