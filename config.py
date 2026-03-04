# config.py

LEAGUE_CODES = {
    "Premier League": "PL", "La Liga": "PD", "Bundesliga": "BL1",
    "Serie A": "SA", "Ligue 1": "FL1", "Champions League": "UCL",
    "Europa League": "UEL", "FA Cup": "FA", "Other": "OT"
}

PINNACLE_LEAGUE_IDS = {
    "Premier League": 1980, "La Liga": 2627, "Bundesliga": 1922,
    "Serie A": 2036, "Ligue 1": 2234, "Champions League": 1517
}

STATSBOMB_COMPS = {
    "Premier League 2015/16": (2, 27), "La Liga 2020/21": (11, 90),
    "Champions League 2019/20": (16, 76)
}

MARKET_ICONS = {
    "1X2": "🎯", "Over/Under": "⚽", "BTTS": "🎯",
    "Corners": "📐", "Cards": "🟨", "Correct Score": "🎯"
}

RG_WARNING = """
<div class="responsible-banner">
    ⚠️ <strong>Gamble Responsibly:</strong> This is for entertainment only. 
    Not affiliated with any bookmaker. Never bet more than you can afford to lose.
    <a href="#" style="color:#FFDADA;">Get Help</a>
</div>
"""

CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
<style>
/* ─── BASE STYLES ─── */
:root {
    --bg-primary: #0C0F17;
    --bg-secondary: #151924;
    --bg-tertiary: #1A1F2E;
    --accent-gold: #D5A021;
    --accent-cyan: #2FD9C5;
    --accent-purple: #8B5CF6;
    --text-primary: #FFFFFF;
    --text-secondary: #9BA0B5;
    --text-muted: #5C6370;
    --success: #10B981;
    --danger: #EF4444;
    --border: rgba(255,255,255,0.08);
}

* { box-sizing: border-box; }

body {
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, sans-serif;
}

.stApp { background: var(--bg-primary); }

/* ─── SIDEBAR ─── */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 20px 0;
}

.logo-icon { font-size: 36px; }

.logo-text h2 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 18px;
    margin: 0;
    color: var(--accent-gold);
    letter-spacing: 1px;
}

.logo-text span {
    font-size: 10px;
    color: var(--text-secondary);
    letter-spacing: 2px;
}

.bankroll-card {
    background: linear-gradient(135deg, var(--bg-tertiary), var(--bg-secondary));
    border: 1px solid var(--accent-gold);
    border-radius: 16px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.bankroll-card .label { font-size: 12px; color: var(--text-secondary); }
.bankroll-card .amount { font-size: 28px; font-weight: 700; color: var(--accent-gold); }

.slip-leg {
    display: flex;
    justify-content: space-between;
    padding: 10px 12px;
    background: var(--bg-tertiary);
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 13px;
}

.slip-total {
    display: flex;
    justify-content: space-between;
    padding: 12px;
    border-top: 1px solid var(--border);
    margin-top: 8px;
}

.potential-return {
    text-align: center;
    padding: 16px;
    background: rgba(45, 217, 197, 0.1);
    border-radius: 12px;
    margin-top: 12px;
    font-size: 15px;
}

/* ─── MAIN HEADER ─── */
.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px 32px;
    background: linear-gradient(180deg, var(--bg-secondary) 0%, transparent 100%);
    border-bottom: 1px solid var(--border);
    margin-bottom: 32px;
}

.header-content h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 32px;
    margin: 0;
    background: linear-gradient(90deg, var(--text-primary), var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header-content p {
    color: var(--text-secondary);
    margin: 4px 0 0;
    font-size: 14px;
}

.header-stats {
    display: flex;
    gap: 16px;
}

.stat-box {
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 24px;
    text-align: center;
}

.stat-value {
    display: block;
    font-size: 24px;
    font-weight: 700;
    color: var(--accent-cyan);
}

.stat-label {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ─── LEAGUE HEADER ─── */
.league-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px 24px;
    background: var(--bg-secondary);
    border-radius: 16px;
    margin: 24px 0 16px;
    border: 1px solid var(--border);
}

.league-badge {
    background: var(--accent-gold);
    color: var(--bg-primary);
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 12px;
}

.league-header h2 {
    flex: 1;
    margin: 0;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 20px;
}

.match-count {
    color: var(--text-muted);
    font-size: 13px;
}

/* ─── MATCH CARD ─── */
.match-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 20px;
    transition: all 0.3s ease;
}

.match-card:hover {
    border-color: var(--accent-cyan);
    box-shadow: 0 8px 32px rgba(47, 217, 197, 0.1);
}

.card-top {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
}

.match-info {
    display: flex;
    gap: 12px;
    align-items: center;
}

.match-time {
    font-weight: 700;
    font-size: 16px;
    color: var(--accent-cyan);
}

.match-status {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
}

.match-venue {
    font-size: 13px;
    color: var(--text-secondary);
}

/* ─── TEAMS ROW ─── */
.teams-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 0;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
}

.team {
    flex: 1;
    text-align: center;
}

.team-crest {
    font-size: 40px;
    margin-bottom: 8px;
}

.team-name {
    display: block;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 12px;
}

.strength-bar {
    width: 100px;
    height: 4px;
    background: var(--bg-tertiary);
    border-radius: 2px;
    margin: 0 auto;
    overflow: hidden;
}

.strength-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-gold), var(--accent-cyan));
    border-radius: 2px;
}

.match-center {
    text-align: center;
    padding: 0 32px;
}

.vs {
    font-size: 14px;
    font-weight: 700;
    color: var(--text-muted);
    letter-spacing: 4px;
}

.prob-summary {
    display: flex;
    gap: 16px;
    margin-top: 16px;
    font-size: 13px;
}

.prob-home { color: var(--success); }
.prob-draw { color: var(--accent-gold); }
.prob-away { color: var(--danger); }

/* ─── BET ROWS ─── */
.bet-row {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    background: var(--bg-tertiary);
    border-radius: 10px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.bet-row:hover {
    background: rgba(47, 217, 197, 0.15);
    transform: translateX(4px);
}

.bet-label {
    flex: 1;
    font-weight: 500;
}

.bet-odds {
    font-weight: 700;
    color: var(--accent-cyan);
    margin-right: 16px;
}

.bet-prob {
    font-size: 12px;
    color: var(--text-muted);
    width: 45px;
    text-align: right;
}

/* ─── TABS ─── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: var(--bg-tertiary);
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    background: var(--accent-gold) !important;
    color: var(--bg-primary) !important;
}

/* ─── COSMIC DASHBOARD ─── */
.cosmic-dashboard {
    background: linear-gradient(135deg, #1a1033 0%, #0d1a26 100%);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 16px;
    padding: 24px;
}

.cosmic-master {
    text-align: center;
    padding: 24px;
    background: rgba(139, 92, 246, 0.2);
    border-radius: 12px;
    margin-bottom: 20px;
}

.cosmic-label {
    display: block;
    font-size: 11px;
    letter-spacing: 2px;
    color: var(--accent-purple);
    margin-bottom: 8px;
}

.cosmic-pick {
    display: block;
    font-size: 28px;
    font-weight: 700;
    background: linear-gradient(90deg, #fff, var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.cosmic-conf {
    display: block;
    margin-top: 8px;
    color: var(--text-secondary);
}

.cosmic-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}

.cosmic-item {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 14px;
    text-align: center;
}

.cosmic-icon { font-size: 20px; display: block; margin-bottom: 6px; }
.cosmic-title { display: block; font-size: 11px; color: var(--text-muted); margin-bottom: 4px; }
.cosmic-value { display: block; font-size: 12px; color: var(--accent-purple); }

/* ─── EMPTY STATE ─── */
.empty-state {
    text-align: center;
    padding: 80px 40px;
    background: var(--bg-secondary);
    border-radius: 20px;
    border: 1px dashed var(--border);
}

.empty-icon { font-size: 64px; display: block; margin-bottom: 16px; }
.empty-state h3 { margin: 0 0 8px; }
.empty-state p { color: var(--text-secondary); margin: 0; }

/* ─── RESPONSIBLE BANNER ─── */
.responsible-banner {
    background: rgba(139, 0, 0, 0.85);
    border-radius: 12px;
    padding: 16px;
    margin-top: 32px;
    text-align: center;
    color: #FFDADA;
    font-size: 13px;
}

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--bg-tertiary); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-gold); }
</style>
"""