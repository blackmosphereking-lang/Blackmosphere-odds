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
    1:{1:0.0,  2:-0.3,3:0.4,