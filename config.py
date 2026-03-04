# config.py

LEAGUE_CODES = {
    "Premier League":   "PL",
    "La Liga":          "PD",
    "Bundesliga":       "BL1",
    "Serie A":          "SA",
    "Ligue 1":          "FL1",
    "Champions League": "UCL",
    "Europa League":    "UEL",
}

# Pinnacle Soccer (sport_id=29) league IDs
PINNACLE_LEAGUE_IDS = {
    "Premier League":   1980,
    "La Liga":          2627,
    "Bundesliga":       1922,
    "Serie A":          2036,
    "Ligue 1":          2234,
    "Champions League": 1517,
    "Europa League":    1518,
}

# StatsBomb Open Data — (competition_id, season_id) pairs
STATSBOMB_COMPS = {
    "Premier League 2015/16":     (2,  27),
    "La Liga 2020/21":            (11, 90),
    "Champions League 2019/20":   (16, 76),
    "FA WSL 2020/21":             (37, 90),
    "NWSL 2018":                  (49,  3),
}

CSS = """
<style>
    .value-box      { background:#1a3a1a; border-left:4px solid #00cc44;
                      padding:10px 14px; border-radius:6px; margin:6px 0; }
    .no-value       { background:#2a1a1a; border-left:4px solid #cc2200;
                      padding:10px 14px; border-radius:6px; margin:6px 0; }
    .src-active     { display:inline-block; background:#1e2a1e; border:1px solid #D4AF37;
                      border-radius:12px; padding:2px 10px; margin:2px 3px;
                      font-size:12px; color:#D4AF37; }
    .src-inactive   { display:inline-block; background:#1e1e1e; border:1px solid #444;
                      border-radius:12px; padding:2px 10px; margin:2px 3px;
                      font-size:12px; color:#555; }
    .xg-tag         { background:#0d2137; border:1px solid #1e6aa0; border-radius:6px;
                      padding:3px 10px; font-size:13px; color:#5bb8f5;
                      display:inline-block; margin:3px; }
    .conf-bar-wrap  { background:#111; border-radius:8px; overflow:hidden; height:10px; margin:6px 0; }
    .conf-bar-fill  { height:10px; background:linear-gradient(90deg,#D4AF37,#00cc44); }
    .stat-card      { background:#1a1a2e; border:1px solid #2a2a4e;
                      border-radius:8px; padding:12px; margin:4px 0; }
</style>
"""