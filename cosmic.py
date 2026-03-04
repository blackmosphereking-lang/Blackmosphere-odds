# cosmic.py — 8-System Esoteric Prediction Layer

from datetime import date
import math
from typing import Dict

# ══════════════════════════════════════════════════════════════════════════════
# NUMEROLOGY
# ══════════════════════════════════════════════════════════════════════════════

def _reduce(n: int) -> int:
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n

def name_number(name: str) -> int:
    t = {'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8,'i':9,
         'j':1,'k':2,'l':3,'m':4,'n':5,'o':6,'p':7,'q':8,'r':9,
         's':1,'t':2,'u':3,'v':4,'w':5,'x':6,'y':7,'z':8}
    return _reduce(sum(t.get(c.lower(), 0) for c in name if c.isalpha()))

def date_number(d: date) -> int:
    return _reduce(sum(int(c) for c in d.strftime('%d%m%Y') if c.isdigit()))

_COMPAT = {
    1:{1:0.0,2:-.3,3:.4,4:-.2,5:.5,6:.1,7:-.1,8:.3,9:.2},
    2:{1:.3,2:0.0,3:-.2,4:.4,5:-.3,6:.5,7:.2,8:-.1,9:.3},
    3:{1:-.4,2:.2,3:0.0,4:-.1,5:.3,6:-.2,7:.5,8:.2,9:-.3},
    4:{1:.2,2:-.4,3:.1,4:0.0,5:-.2,6:.3,7:-.4,8:.5,9:.1},
    5:{1:-.5,2:.3,3:-.3,4:.2,5:0.0,6:-.4,7:.3,8:-.2,9:.5},
    6:{1:-.1,2:-.5,3:.2,4:-.3,5:.4,6:0.0,7:-.3,8:.3,9:-.4},
    7:{1:.1,2:-.2,3:-.5,4:.4,5:-.3,6:.3,7:0.0,8:-.4,9:.2},
    8:{1:-.3,2:.1,3:-.2,4:-.5,5:.2,6:-.3,7:.4,8:0.0,9:-.5},
    9:{1:-.2,2:-.3,3:.3,4:-.1,5:-.5,6:.4,7:-.2,8:.5,9:0.0},
}

def numerology_bias(home: str, away: str, d: date) -> Dict:
    hn = name_number(home)
    an = name_number(away)
    dn = date_number(d)
    b = _COMPAT.get(hn, _COMPAT[1]).get(an, 0.0)
    if dn in (11,22,33): b *= 0.7
    elif dn in (1,9): b += 0.10
    elif dn == 7: b *= -1.0
    b = max(-0.5, min(0.5, b))
    verdict = "🏠 Home" if b > 0.1 else "✈️ Away" if b < -0.1 else "⚖️ Draw"
    return {"hn": hn, "an": an, "dn": dn, "bias": round(b, 3), "verdict": verdict}

# ══════════════════════════════════════════════════════════════════════════════
# ASTROLOGY
# ══════════════════════════════════════════════════════════════════════════════

_RULERS = {
    0: {"p": "Moon", "sym": "🌙", "bias": 0.15},
    1: {"p": "Mars", "sym": "♂️", "bias": 0.05},
    2: {"p": "Mercury", "sym": "☿", "bias": 0.00},
    3: {"p": "Jupiter", "sym": "♃", "bias": 0.10},
    4: {"p": "Venus", "sym": "♀️", "bias": -0.10},
    5: {"p": "Saturn", "sym": "♄", "bias": -0.15},
    6: {"p": "Sun", "sym": "☀️", "bias": 0.20},
}

_NEW_MOON = date(2000, 1, 6)
_LUNAR = 29.53058867
_PHASES = [
    (1.85, "🌑 New Moon", "Upsets + low scoring", -0.05, -0.15),
    (7.38, "🌒 Waxing Crescent", "Home builds momentum", 0.10, 0.05),
    (11.08, "🌓 First Quarter", "Tension + bookings", 0.05, 0.10),
    (14.77, "🌔 Waxing Gibbous", "Favourites + Over 2.5", 0.15, 0.15),
    (18.47, "🌕 Full Moon", "Peak drama + high goals", 0.05, 0.25),
    (22.16, "🌖 Waning Gibbous", "Draws + goals flow", 0.00, 0.10),
    (25.85, "🌗 Last Quarter", "Away upsets", -0.15, 0.05),
    (29.53, "🌘 Waning Crescent", "Defensive + Under", -0.10, -0.10),
]

def day_ruler(d: date) -> Dict:
    return _RULERS[d.weekday()]

def moon_phase(d: date) -> Dict:
    days = (d - _NEW_MOON).days % _LUNAR
    for thresh, name, meaning, hb, gb in _PHASES:
        if days <= thresh:
            return {"phase": name, "meaning": meaning, "days": round(days, 1), "home_bias": hb, "goal_bias": gb}
    return {"phase": "🌑 New Moon", "meaning": "Reset", "days": 0, "home_bias": -0.05, "goal_bias": -0.15}

def mercury_retrograde(d: date) -> bool:
    periods = [
        (date(2025, 3, 15), date(2025, 4, 7)),
        (date(2025, 7, 18), date(2025, 8, 11)),
        (date(2025, 11, 9), date(2025, 12, 1)),
        (date(2026, 3, 14), date(2026, 4, 6)),
        (date(2026, 7, 9), date(2026, 8, 1)),
    ]
    return any(s <= d <= e for s, e in periods)

# ══════════════════════════════════════════════════════════════════════════════
# NAPOLEON HILL
# ══════════════════════════════════════════════════════════════════════════════

def napoleon_hill(home: str, away: str, hs: float, as_: float) -> Dict:
    ratio = hs / max(as_, 0.01)
    hn = name_number(home)
    score = sum([hn in (1, 4, 8), hs > 1.2, ratio > 1.3, hn in (2, 6, 9), hs > 1.0, as_ < 1.2])
    
    if ratio > 1.4 and score >= 5:
        state = "🔥 Definiteness — Home Dominant"
        b = 0.30
    elif ratio < 0.7 and score <= 2:
        state = "🌀 Drifting — Away Takes Control"
        b = -0.30
    elif 0.9 <= ratio <= 1.1:
        state = "⚖️ Mastermind Clash — Draw"
        b = 0.0
    else:
        state = "📈 Slight Home Assertion"
        b = 0.10 * (ratio - 1.0)
    
    return {"state": state, "bias": round(b, 3), "score": score}

# ══════════════════════════════════════════════════════════════════════════════
# SAMAEL AUN WEOR - LAW OF THREE
# ══════════════════════════════════════════════════════════════════════════════

_FORCES = {1: "☀️ Holy Affirming", 2: "🌊 Holy Denying", 3: "⚡ Holy Reconciling"}

def law_of_three(home: str, away: str, d: date) -> Dict:
    h = name_number(home) % 3 or 3
    a = name_number(away) % 3 or 3
    x = date_number(d) % 3 or 3
    
    if x == 1:
        verdict = f"Active Force: {home} asserts"
        b = 0.20
    elif x == 2:
        verdict = f"Denying Force: {away} neutralises"
        b = -0.20
    else:
        verdict = "Reconciling: Draw likely"
        b = 0.00
    
    if h == 2: b -= 0.10
    if a == 1: b -= 0.10
    
    return {
        "home_force": _FORCES[h],
        "away_force": _FORCES[a],
        "date_force": _FORCES[x],
        "verdict": verdict,
        "bias": round(max(-0.4, min(0.4, b)), 3)
    }

# ══════════════════════════════════════════════════════════════════════════════
# YOGIC NAKSHATRAS
# ══════════════════════════════════════════════════════════════════════════════

_NAK = [
    ("Ashwini", "Swift starts, early goals", 0.10, 0.15),
    ("Bharani", "Intensity, narrow results", -0.05, 0.05),
    ("Krittika", "Sharp, decisive winner", 0.15, 0.00),
    ("Rohini", "Fertile goals, Over 2.5", 0.05, 0.20),
    ("Mrigashira", "Cautious, late goals", 0.00, 0.05),
    ("Ardra", "Chaotic, many bookings", -0.10, 0.10),
    ("Punarvasu", "Comeback energy", 0.10, 0.05),
    ("Pushya", "Home strength, clean sheet", 0.20, -0.10),
    ("Ashlesha", "Counter-attack away", -0.15, 0.05),
    ("Magha", "Royal favourites dominate", 0.25, -0.05),
    ("Purva Phalguni", "High scoring", 0.05, 0.25),
    ("Uttara Phalguni", "Narrow home win", 0.15, -0.10),
    ("Hasta", "Skill, set pieces", 0.10, 0.05),
    ("Chitra", "Stunning goals", 0.05, 0.15),
    ("Swati", "Draws likely", -0.05, 0.00),
    ("Vishakha", "Winner emerges", 0.10, 0.10),
    ("Anuradha", "Home spirit", 0.15, 0.05),
    ("Jyeshtha", "Experience, clean sheet", 0.20, -0.15),
    ("Mula", "Major upset possible", -0.20, 0.10),
    ("Purva Ashadha", "Fast start", 0.15, 0.10),
    ("Uttara Ashadha", "Late goals", 0.10, 0.15),
    ("Shravana", "Defensive draw", -0.05, -0.10),
    ("Dhanishtha", "Free-flowing, BTTS", 0.05, 0.20),
    ("Shatabhisha", "Statistical surprise", -0.10, 0.05),
    ("Purva Bhadra", "Controversy, heavy bookings", 0.00, 0.05),
    ("Uttara Bhadra", "Calm, low scoring", -0.05, -0.20),
    ("Revati", "Balanced draw", -0.10, 0.00),
]

def nakshatra(d: date) -> Dict:
    idx = (d - _NEW_MOON).days % 27
    n = _NAK[idx]
    return {"index": idx + 1, "name": n[0], "meaning": n[1], "home_bias": n[2], "goal_bias": n[3]}

_GUNA = {
    0: {"guna": "Tamas 🌑", "quality": "Inertia, defensive", "bias": -0.10, "gm": -0.20},
    1: {"guna": "Rajas 🔥", "quality": "Action, goals", "bias": 0.05, "gm": 0.20},
    2: {"guna": "Rajas 🔥", "quality": "Quick movement", "bias": 0.05, "gm": 0.10},
    3: {"guna": "Sattva ✨", "quality": "Clarity, excellence", "bias": 0.15, "gm": 0.05},
    4: {"guna": "Rajas 🔥", "quality": "Desire, high tempo", "bias": 0.00, "gm": 0.15},
    5: {"guna": "Tamas 🌑", "quality": "Heaviness, draws", "bias": -0.15, "gm": -0.15},
    6: {"guna": "Sattva ✨", "quality": "Solar excellence", "bias": 0.20, "gm": 0.10},
}

def triguna(d: date) -> Dict:
    return _GUNA[d.weekday()]

# ══════════════════════════════════════════════════════════════════════════════
# BIORHYTHMS
# ══════════════════════════════════════════════════════════════════════════════

def _pseudo_birth(name: str) -> date:
    n = name_number(name)
    return date(1900 + (n * 11), (n * 3 % 12) + 1, (n * 7 % 28) + 1)

def biorhythm_bias(home: str, away: str, d: date) -> Dict:
    def bio(name):
        days = (d - _pseudo_birth(name)).days
        p = math.sin(2 * math.pi * days / 23)
        e = math.sin(2 * math.pi * days / 28)
        i = math.sin(2 * math.pi * days / 33)
        return round((p + e + i) / 3, 3)
    
    hb = bio(home)
    ab = bio(away)
    diff = hb - ab
    bias = max(-0.4, min(0.4, diff * 0.35))
    
    if diff > 0.4:
        verdict = f"⚡ {home} at cosmic peak"
    elif diff < -0.4:
        verdict = f"⚡ {away} at cosmic peak"
    elif abs(diff) < 0.1:
        verdict = "🌀 Equal rhythm — Draw energy"
    else:
        verdict = f"📈 Slight {'Home' if diff > 0 else 'Away'} edge"
    
    return {"home": hb, "away": ab, "diff": round(diff, 3), "bias": round(bias, 3), "verdict": verdict}

# ══════════════════════════════════════════════════════════════════════════════
# MASTER COSMIC VERDICT
# ══════════════════════════════════════════════════════════════════════════════

def cosmic_verdict(home: str, away: str, hs: float = 1.0, as_: float = 1.0, d: date = None) -> Dict:
    if d is None:
        d = date.today()
    
    num = numerology_bias(home, away, d)
    ruler = day_ruler(d)
    moon = moon_phase(d)
    retro = mercury_retrograde(d)
    hill = napoleon_hill(home, away, hs, as_)
    weor = law_of_three(home, away, d)
    guna = triguna(d)
    naks = nakshatra(d)
    bio = biorhythm_bias(home, away, d)
    
    W = {"num": 0.15, "ruler": 0.10, "moon": 0.12, "hill": 0.18,
         "weor": 0.15, "guna": 0.10, "naks": 0.10, "bio": 0.10}
    
    bias = (
        num['bias'] * W['num'] +
        ruler['bias'] * W['ruler'] +
        moon['home_bias'] * W['moon'] +
        hill['bias'] * W['hill'] +
        weor['bias'] * W['weor'] +
        guna['bias'] * W['guna'] +
        naks['home_bias'] * W['naks'] +
        bio['bias'] * W['bio']
    )
    
    if retro:
        bias *= 0.5
    
    goal_mod = moon['goal_bias'] * 0.35 + guna['gm'] * 0.35 + naks['goal_bias'] * 0.30
    
    sigs = [num['bias'], moon['home_bias'], hill['bias'], weor['bias'], bio['bias'], naks['home_bias']]
    confidence = max(sum(s > 0.05 for s in sigs), sum(s < -0.05 for s in sigs)) / len(sigs)
    
    booking_signal = "🟨 HIGH BOOKINGS" if naks['name'] in ("Ardra", "Krittika", "Purva Bhadra") or ruler['p'] == "Mars" else "🟩 Normal"
    
    if bias > 0.18:
        pick = f"🏠 {home} WIN"
        col = "#0d2a0d"
    elif bias < -0.18:
        pick = f"✈️ {away} WIN"
        col = "#1a0a2a"
    else:
        pick = "⚖️ DRAW"
        col = "#1a1a0a"
    
    return {
        "pick": pick,
        "pick_color": col,
        "bias": round(bias, 3),
        "confidence": round(min(confidence, 0.95), 3),
        "goal_modifier": round(goal_mod, 3),
        "booking_signal": booking_signal,
        "retro": retro,
        "systems": {
            "Numerology": f"{num['verdict']} (#{num['hn']} vs #{num['an']})",
            "Day Ruler": f"{ruler['sym']} {ruler['p']}",
            "Moon Phase": f"{moon['phase']}",
            "Napoleon Hill": f"{hill['state']}",
            "Weor Law of ③": f"{weor['verdict']}",
            "Triguna": f"{guna['guna']}",
            "Nakshatra": f"{naks['name']}",
            "Biorhythm": f"{bio['verdict']}",
        }
    }