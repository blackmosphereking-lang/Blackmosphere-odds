# cosmic.py — Esoteric & Cosmic Prediction Layer
# Systems: Numerology · Astrology · Napoleon Hill (Outwitting the Devil)
#          Samael Aun Weor (Law of Three) · Yogic Nakshatras · Biorhythms

from datetime import date
import math
from typing import Dict

# ══════════════════════════════════════════════════════════════════════════════
# NUMEROLOGY — Pythagorean System
# ══════════════════════════════════════════════════════════════════════════════

def _reduce(n: int) -> int:
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n

def name_number(name: str) -> int:
    table = {
        'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8,'i':9,
        'j':1,'k':2,'l':3,'m':4,'n':5,'o':6,'p':7,'q':8,'r':9,
        's':1,'t':2,'u':3,'v':4,'w':5,'x':6,'y':7,'z':8
    }
    return _reduce(sum(table.get(c.lower(), 0) for c in name if c.isalpha()))

def date_number(d: date) -> int:
    return _reduce(sum(int(c) for c in d.strftime('%d%m%Y') if c.isdigit()))

# Compatibility matrix [home_num][away_num] → bias (-0.5 to +0.5)
# Positive = home favoured | Negative = away favoured | 0 = draw energy
_COMPAT = {
    1:{1:0.0,  2:-0.3,3:0.4,  4:-0.2,5:0.5,  6:0.1, 7:-0.1,8:0.3, 9:0.2, 11:0.0, 22:-0.2,33:0.1},
    2:{1:0.3,  2:0.0, 3:-0.2, 4:0.4, 5:-0.3, 6:0.5, 7:0.2, 8:-0.1,9:0.3, 11:0.2, 22:0.4, 33:-0.1},
    3:{1:-0.4, 2:0.2, 3:0.0,  4:-0.1,5:0.3,  6:-0.2,7:0.5, 8:0.2, 9:-0.3,11:0.1, 22:-0.1,33:0.3},
    4:{1:0.2,  2:-0.4,3:0.1,  4:0.0, 5:-0.2, 6:0.3, 7:-0.4,8:0.5, 9:0.1, 11:-0.2,22:0.3, 33:-0.2},
    5:{1:-0.5, 2:0.3, 3:-0.3, 4:0.2, 5:0.0,  6:-0.4,7:0.3, 8:-0.2,9:0.5, 11:0.3, 22:-0.3,33:0.2},
    6:{1:-0.1, 2:-0.5,3:0.2,  4:-0.3,5:0.4,  6:0.0, 7:-0.3,8:0.3, 9:-0.4,11:-0.1,22:0.2, 33:0.4},
    7:{1:0.1,  2:-0.2,3:-0.5, 4:0.4, 5:-0.3, 6:0.3, 7:0.0, 8:-0.4,9:0.2, 11:0.4, 22:-0.4,33:-0.3},
    8:{1:-0.3, 2:0.1, 3:-0.2, 4:-0.5,5:0.2,  6:-0.3,7:0.4, 8:0.0, 9:-0.5,11:-0.3,22:0.5, 33:0.1},
    9:{1:-0.2, 2:-0.3,3:0.3,  4:-0.1,5:-0.5, 6:0.4, 7:-0.2,8:0.5, 9:0.0, 11:0.2, 22:-0.5,33:0.4},
    11:{1:0.0, 2:-0.2,3:-0.1, 4:0.2, 5:-0.3, 6:0.1, 7:-0.4,8:0.3, 9:-0.2,11:0.0, 22:0.1, 33:-0.1},
    22:{1:0.2, 2:-0.4,3:0.1,  4:-0.3,5:0.3,  6:-0.2,7:0.4, 8:-0.5,9:0.5, 11:-0.1,22:0.0, 33:0.2},
    33:{1:-0.1,2:0.1, 3:-0.3, 4:0.2, 5:-0.2, 6:-0.4,7:0.3, 8:-0.1,9:-0.4,11:0.1, 22:-0.2,33:0.0},
}

def numerology_bias(home: str, away: str, match_date: date) -> Dict:
    hn  = name_number(home)
    an  = name_number(away)
    dn  = date_number(match_date)
    row = _COMPAT.get(hn, _COMPAT[1])
    bias = row.get(an, 0.0)
    if dn in (11, 22, 33):  bias *= 0.7    # Master numbers balance
    elif dn in (1, 9):      bias += 0.10   # Leadership/completion → home
    elif dn == 7:           bias *= -1.0   # Spiritual → upsets
    bias = max(-0.5, min(0.5, bias))
    verdict = ("🏠 Home Favoured" if bias > 0.1 else
               "✈️ Away Favoured"  if bias < -0.1 else "⚖️ Balanced Draw Energy")
    return {"home_number": hn, "away_number": an, "date_vibration": dn,
            "bias": round(bias, 3), "verdict": verdict,
            "insight": f"Home #{hn} vs Away #{an} on vibration day #{dn}"}


# ══════════════════════════════════════════════════════════════════════════════
# ASTROLOGY — Planetary Rulers, Moon Phase, Mercury Retrograde
# ══════════════════════════════════════════════════════════════════════════════

_DAY_RULERS = {
    0:{"planet":"Moon",    "symbol":"🌙","energy":"Fluid, emotional, home comfort",     "bias": 0.15},
    1:{"planet":"Mars",    "symbol":"♂️","energy":"Aggressive, high tempo, goals & cards","bias": 0.05},
    2:{"planet":"Mercury", "symbol":"☿", "energy":"Quick transitions, technical play",   "bias": 0.00},
    3:{"planet":"Jupiter", "symbol":"♃", "energy":"Expansion, high scoring, favourites", "bias": 0.10},
    4:{"planet":"Venus",   "symbol":"♀️","energy":"Harmony, entertaining, draw energy",  "bias":-0.10},
    5:{"planet":"Saturn",  "symbol":"♄", "energy":"Discipline, low scoring, upsets",     "bias":-0.15},
    6:{"planet":"Sun",     "symbol":"☀️","energy":"Dominant, home glory, favourites win", "bias": 0.20},
}

_NEW_MOON_REF = date(2000, 1, 6)
_LUNAR_CYCLE  = 29.53058867

_MOON_PHASES = [
    (1.85,  "🌑 New Moon",        "New beginnings; upsets; low scoring",        -0.05, -0.15),
    (7.38,  "🌒 Waxing Crescent", "Building momentum; home teams strengthen",    0.10,  0.05),
    (11.08, "🌓 First Quarter",   "Tension & action; bookings; goals scored",    0.05,  0.10),
    (14.77, "🌔 Waxing Gibbous",  "High energy; favourites assert; Over 2.5",    0.15,  0.15),
    (18.47, "🌕 Full Moon",       "Peak drama; high scoring; favourites win",    0.05,  0.25),
    (22.16, "🌖 Waning Gibbous",  "Energy drops; draws; goals still flow",       0.00,  0.10),
    (25.85, "🌗 Last Quarter",    "Tipping point; away upsets; surprises",      -0.15,  0.05),
    (29.53, "🌘 Waning Crescent", "Defensive play; under likely; endings",      -0.10, -0.10),
]

def moon_phase(d: date) -> Dict:
    days = (d - _NEW_MOON_REF).days % _LUNAR_CYCLE
    for threshold, phase, meaning, h_bias, g_bias in _MOON_PHASES:
        if days <= threshold:
            return {"phase": phase, "meaning": meaning,
                    "days_into_cycle": round(days, 1),
                    "home_bias": h_bias, "goal_bias": g_bias}
    return {"phase":"🌑 New Moon","meaning":"Reset","days_into_cycle":0,
            "home_bias":-0.05,"goal_bias":-0.15}

_RETRO_PERIODS = [
    (date(2025,3,15), date(2025,4,7)),  (date(2025,7,18), date(2025,8,11)),
    (date(2025,11,9), date(2025,12,1)), (date(2026,3,14), date(2026,4,6)),
    (date(2026,7,9),  date(2026,8,1)),
]

def mercury_retrograde(d: date) -> bool:
    return any(s <= d <= e for s, e in _RETRO_PERIODS)

def day_ruler(d: date) -> Dict:
    return _DAY_RULERS[d.weekday()]


# ══════════════════════════════════════════════════════════════════════════════
# NAPOLEON HILL — Outwitting the Devil: Definiteness of Purpose
# ══════════════════════════════════════════════════════════════════════════════

def napoleon_hill_analysis(home: str, away: str,
                            home_str: float, away_str: float) -> Dict:
    ratio    = home_str / max(away_str, 0.01)
    home_num = name_number(home)
    away_num = name_number(away)

    principles = {
        "Definiteness of Purpose":  home_num in (1, 4, 8),
        "Mastermind Alliance":      abs(home_num - away_num) <= 2,
        "Applied Faith":            home_str > 1.2,
        "Going the Extra Mile":     ratio > 1.3,
        "Pleasing Personality":     home_num in (2, 6, 9),
        "Personal Initiative":      home_str > 1.0,
        "Self Discipline":          away_str < 1.2,
    }
    score = sum(1 for v in principles.values() if v)

    if ratio > 1.4 and score >= 5:
        state = "🔥 Definite Purpose — Home Dominant"; bias = 0.30
    elif ratio < 0.7 and score <= 2:
        state = "🌀 Drifting — Away Takes Control";    bias = -0.30
    elif 0.9 <= ratio <= 1.1:
        state = "⚖️ Equal Vibration — Mastermind Clash"; bias = 0.0
    else:
        state = "📈 Gradual Assertion — Slight Home Edge"
        bias  = 0.10 * (ratio - 1.0)

    return {"state": state, "bias": round(bias, 3),
            "principles_active": score, "devil_drifter": score < 3,
            "insight": f"{score}/7 Hill Principles align with home team"}


# ══════════════════════════════════════════════════════════════════════════════
# SAMAEL AUN WEOR — Law of Three
# ══════════════════════════════════════════════════════════════════════════════

def weor_law_of_three(home: str, away: str, match_date: date) -> Dict:
    h_vib = name_number(home)    % 3 or 3
    a_vib = name_number(away)    % 3 or 3
    d_vib = date_number(match_date) % 3 or 3

    forces = {1:"☀️ Holy Affirming (Active/Home)",
              2:"🌊 Holy Denying  (Passive/Away)",
              3:"⚡ Holy Reconciling (Draw/Balance)"}

    if d_vib == 1:
        verdict = f"Active Force Dominant: {home} asserts will"; bias = 0.20
    elif d_vib == 2:
        verdict = f"Denying Force Rises: {away} neutralises home"; bias = -0.20
    else:
        verdict = "Reconciling Force: Neither yields — Draw likely"; bias = 0.0

    if h_vib == 2: bias -= 0.10; verdict += " | Home ego-dissolution risk"
    if a_vib == 1: bias -= 0.10; verdict += " | Away active assertion"

    return {"home_force": forces[h_vib], "away_force": forces[a_vib],
            "date_force": forces[d_vib], "verdict": verdict,
            "bias": round(max(-0.4, min(0.4, bias)), 3)}


# ══════════════════════════════════════════════════════════════════════════════
# YOGIC TEXTS — 27 Nakshatras (Lunar Mansions) & Tri-Guna
# ══════════════════════════════════════════════════════════════════════════════

_NAKSHATRAS = [
    ("Ashwini",        "Swift starts, fast play, early goals",            0.10,  0.15),
    ("Bharani",        "Intensity, struggle, narrow results",             -0.05,  0.05),
    ("Krittika",       "Sharp cutting, red cards, decisive winner",        0.15,  0.00),
    ("Rohini",         "Fertile goals, entertaining, Over 2.5",           0.05,  0.20),
    ("Mrigashira",     "Searching energy, cautious, late goals",          0.00,  0.05),
    ("Ardra",          "Storm energy, chaotic, many bookings",           -0.10,  0.10),
    ("Punarvasu",      "Return, recovery, comeback energy",               0.10,  0.05),
    ("Pushya",         "Nourishing, home strength, clean sheet likely",   0.20, -0.10),
    ("Ashlesha",       "Cunning, tactical, counter-attack away wins",    -0.15,  0.05),
    ("Magha",          "Royal power, favourites dominate",                0.25, -0.05),
    ("Purva Phalguni", "Pleasure, high scoring, entertaining",            0.05,  0.25),
    ("Uttara Phalguni","Reliable, structured, narrow home win",           0.15, -0.10),
    ("Hasta",          "Skill, technical play, set pieces decide",        0.10,  0.05),
    ("Chitra",         "Brilliance, stunning goals, beauty",              0.05,  0.15),
    ("Swati",          "Flexible, draws likely, equalizers",             -0.05,  0.00),
    ("Vishakha",       "Goal-oriented, determined, winner emerges",       0.10,  0.10),
    ("Anuradha",       "Loyalty, home fans matter, team spirit",          0.15,  0.05),
    ("Jyeshtha",       "Experience wins, discipline, clean sheet",        0.20, -0.15),
    ("Mula",           "Root upheaval, massive upset possible",          -0.20,  0.10),
    ("Purva Ashadha",  "Early victory, fast start, HT lead",             0.15,  0.10),
    ("Uttara Ashadha", "Final victory, late goals, last-minute drama",    0.10,  0.15),
    ("Shravana",       "Listening, adaptability, defensive draw",        -0.05, -0.10),
    ("Dhanishtha",     "Rhythm & goals, free flowing, BTTS",              0.05,  0.20),
    ("Shatabhisha",    "Healing, statistical anomaly, surprise result",  -0.10,  0.05),
    ("Purva Bhadra",   "Intense passion, controversy, bookings heavy",    0.00,  0.05),
    ("Uttara Bhadra",  "Deep calm, low scoring, disciplined defence",    -0.05, -0.20),
    ("Revati",         "Journey's end, balanced, draw contest",          -0.10,  0.00),
]

def nakshatra_of_day(d: date) -> Dict:
    days = (d - _NEW_MOON_REF).days
    idx  = days % 27
    n    = _NAKSHATRAS[idx]
    return {"index": idx+1, "name": n[0], "meaning": n[1],
            "home_bias": n[2], "goal_bias": n[3]}

_WEEKDAY_GUNA = {
    0:{"guna":"Tamas 🌑", "quality":"Inertia, defensive, low goals",       "bias":-0.10,"goal_mod":-0.20},
    1:{"guna":"Rajas 🔥", "quality":"Passion, action, goals & bookings",   "bias": 0.05,"goal_mod": 0.20},
    2:{"guna":"Rajas 🔥", "quality":"Quick movement, technical play",       "bias": 0.05,"goal_mod": 0.10},
    3:{"guna":"Sattva ✨","quality":"Clarity, excellence, clean results",   "bias": 0.15,"goal_mod": 0.05},
    4:{"guna":"Rajas 🔥", "quality":"Desire, scoring, high tempo football", "bias": 0.00,"goal_mod": 0.15},
    5:{"guna":"Tamas 🌑", "quality":"Heaviness, draws, defensive blocks",   "bias":-0.15,"goal_mod":-0.15},
    6:{"guna":"Sattva ✨","quality":"Solar excellence, home dominance",     "bias": 0.20,"goal_mod": 0.10},
}

def triguna_reading(d: date) -> Dict:
    return _WEEKDAY_GUNA[d.weekday()]


# ══════════════════════════════════════════════════════════════════════════════
# BIORHYTHMS — Cosmic Energy Cycles
# ══════════════════════════════════════════════════════════════════════════════

def _pseudo_birthdate(name: str) -> date:
    num   = name_number(name)
    year  = 1900 + (num * 11)
    month = (num * 3 % 12) + 1
    day_v = (num * 7 % 28) + 1
    return date(year, month, day_v)

def biorhythm(name: str, match_date: date) -> Dict:
    bd    = _pseudo_birthdate(name)
    days  = (match_date - bd).days
    phys  = math.sin(2 * math.pi * days / 23)
    emot  = math.sin(2 * math.pi * days / 28)
    intel = math.sin(2 * math.pi * days / 33)
    return {"physical": round(phys,3), "emotional": round(emot,3),
            "intellectual": round(intel,3),
            "composite": round((phys + emot + intel) / 3, 3)}

def biorhythm_bias(home: str, away: str, match_date: date) -> Dict:
    h_bio = biorhythm(home, match_date)
    a_bio = biorhythm(away, match_date)
    diff  = h_bio['composite'] - a_bio['composite']
    bias  = max(-0.4, min(0.4, diff * 0.35))
    if diff > 0.4:    verdict = f"⚡ {home} riding cosmic peak energy"
    elif diff < -0.4: verdict = f"⚡ {away} riding cosmic peak energy"
    elif abs(diff) < 0.1: verdict = "🌀 Both teams in equal cosmic rhythm — Draw energy"
    else:             verdict = f"📈 Slight edge to {'Home' if diff > 0 else 'Away'}"
    return {"home_composite": h_bio['composite'], "away_composite": a_bio['composite'],
            "differential": round(diff,3), "bias": round(bias,3), "verdict": verdict}


# ══════════════════════════════════════════════════════════════════════════════
# MASTER COSMIC VERDICT — All Eight Systems Combined
# ══════════════════════════════════════════════════════════════════════════════

def cosmic_verdict(home: str, away: str,
                   home_str: float, away_str: float,
                   match_date: date = None) -> Dict:
    if match_date is None:
        match_date = date.today()

    num   = numerology_bias(home, away, match_date)
    ruler = day_ruler(match_date)
    moon  = moon_phase(match_date)
    retro = mercury_retrograde(match_date)
    hill  = napoleon_hill_analysis(home, away, home_str, away_str)
    weor  = weor_law_of_three(home, away, match_date)
    guna  = triguna_reading(match_date)
    naks  = nakshatra_of_day(match_date)
    bio   = biorhythm_bias(home, away, match_date)

    weights = {"num":0.15,"ruler":0.10,"moon":0.12,"hill":0.18,
               "weor":0.15,"guna":0.10,"naks":0.10,"bio":0.10}

    raw_bias = (
        num['bias']       * weights['num']   +
        ruler['bias']     * weights['ruler'] +
        moon['home_bias'] * weights['moon']  +
        hill['bias']      * weights['hill']  +
        weor['bias']      * weights['weor']  +
        guna['bias']      * weights['guna']  +
        naks['home_bias'] * weights['naks']  +
        bio['bias']       * weights['bio']
    )

    if retro:
        raw_bias *= 0.5  # Mercury retro compresses toward uncertainty

    goal_mod = (moon['goal_bias'] * 0.35 +
                guna['goal_mod']  * 0.30 +
                naks['goal_bias'] * 0.35)

    booking_signal = (
        "🟨 HIGH BOOKINGS LIKELY" if (
            naks['name'] in ("Ardra","Krittika","Purva Bhadra") or
            ruler['planet'] == "Mars"
        ) else "🟩 Normal Discipline Expected"
    )

    signals    = [num['bias'], moon['home_bias'], hill['bias'],
                  weor['bias'], bio['bias'], naks['home_bias']]
    agree_home = sum(1 for s in signals if s >  0.05)
    agree_away = sum(1 for s in signals if s < -0.05)
    confidence = max(agree_home, agree_away) / len(signals)

    if raw_bias > 0.18:
        master_pick = f"🏠 {home} WIN"; pick_color = "#0d2a0d"
    elif raw_bias < -0.18:
        master_pick = f"✈️ {away} WIN"; pick_color = "#2a0d2a"
    else:
        master_pick = "⚖️ DRAW";         pick_color = "#