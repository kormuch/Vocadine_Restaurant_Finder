#german_cities.py
from german_cities_list import GERMAN_CITIES_LIST


GERMAN_CITIES = {}
for city in GERMAN_CITIES_LIST:
    GERMAN_CITIES[city.lower()] = city

# Schritt 2: Wichtigste englische Namen manuell hinzufügen
ENGLISH_ALIASES = {
    "munich": "München",
    "cologne": "Köln",
    "nuremberg": "Nürnberg",
    "hanover": "Hannover",
    "brunswick": "Braunschweig",
    "mayence": "Mainz",
    "ratisbon": "Regensburg",
    "trier": "Trier",  # Trier ist schon drin, aber Touristen sagen oft englisch
}

GERMAN_CITIES.update(ENGLISH_ALIASES)

# ─────────────────────────────────────────────
# NLU SETUP (Städte & Phonetik-Aliase)
# ─────────────────────────────────────────────
GERMAN_CITIES = {city.lower(): city for city in GERMAN_CITIES_LIST}
# Manuelle Korrekturen für häufige Hörfehler (Phonetic Mapping)
PHONETIC_ALIASES = {
    "munich": "München",
    "cologne": "Köln",
    "mayence": "Mainz",
    "gerlach": "Haigerloch",   # Dein spezifischer Fehler-Fix
    "girl": "Haigerloch",      # Dein spezifischer Fehler-Fix
    "higher lock": "Haigerloch",
    "bear lough": "Balingen",
    "bärlauch": "Balingen"
}
GERMAN_CITIES.update({k.lower(): v for k, v in PHONETIC_ALIASES.items()})