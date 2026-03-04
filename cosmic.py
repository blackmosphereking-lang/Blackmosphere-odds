# ════════════════════════════════════════════════════════════════════════════
# FILE 3: cosmic.py
# ════════════════════════════════════════════════════════════════════════════

import hashlib
from datetime import date

# ── Cosmic Themes ─────────────────────────────────────────────────────────

_PLANETS = [
    "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Neptune", "Uranus", "Pluto", "Moon", "Sun",
]

_ELEMENTS = ["Fire", "Water", "Earth", "Air"]

_VERDICTS = [
    "The celestial alignment strongly favors the home side today.",
    "Away energy is surging — the visitors carry cosmic momentum.",
    "A tense equilibrium in the stars suggests a hard-fought draw.",
    "Mars in retrograde hints at defensive masterclasses on both sides.",
    "Jupiter's expansion energy points toward a high-scoring affair.",
    "Saturn's discipline suggests a tight, low-scoring contest.",
    "Venus brings harmony — expect beautiful football from both teams.",
    "Mercury's speed favors the team with the faster counterattack.",
    "The Moon's phase amplifies home crowd energy tonight.",
    "Neptune clouds judgment — an upset is written in the stars.",
    "Pluto's transformative energy signals a turning point for the underdog.",
    "Uranus brings chaos — expect the unexpected in this fixture.",
    "Sun energy radiates confidence for the league leaders.",
    "A fire-water clash in the zodiac — passion meets composure.",
    "Earth signs dominate — the more grounded team will prevail.",
    "Air signs are ascendant — creativity and flair will decide this one.",
]

_CONFIDENCE = [
    "🌟 Cosmic Confidence: HIGH",
    "✨ Cosmic Confidence: MODERATE",
    "🌙 Cosmic Confidence: LOW — tread carefully",
    "☄️ Cosmic Confidence: VOLATILE — anything can happen",
]


def cosmic_verdict(home_team: str, away_team: str) -> str:
    """
    Generate a deterministic cosmic verdict for a match.

    Uses a hash of the team names + today's date so the same matchup
    on the same day always returns the same verdict, but changes daily.

    Args:
        home_team: Home team name
        away_team: Away team name

    Returns:
        A cosmic verdict string with planet, element, and confidence.
    """
    today = date.today().isoformat()
    seed = f"{home_team}|{away_team}|{today}"
    digest = hashlib.sha256(seed.encode()).hexdigest()

    # Use different parts of the hash for each selection
    planet_idx = int(digest[:4], 16) % len(_PLANETS)
    element_idx = int(digest[4:8], 16) % len(_ELEMENTS)
    verdict_idx = int(digest[8:12], 16) % len(_VERDICTS)
    confidence_idx = int(digest[12:16], 16) % len(_CONFIDENCE)

    planet = _PLANETS[planet_idx]
    element = _ELEMENTS[element_idx]
    verdict = _VERDICTS[verdict_idx]
    confidence = _CONFIDENCE[confidence_idx]

    return (
        f"🪐 **Ruling Planet:** {planet}  |  "
        f"🜂 **Element:** {element}\n\n"
        f"{verdict}\n\n"
        f"{confidence}"
    )