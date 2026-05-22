"""
VocaDine Germany — Portfolio Prototype  v0.3
Usecase: English-speaking tourist in Germany.
Architecture: STT (English) → Dialog Management → Google Places API → ML Ranking → TTS (English)

Changelog v0.3 (Phase 3):
  - [#16] Venue type filter: exclude non-restaurant place types from results
  - [#17] Radius search: apply 3km locationBias when specific city is known
"""

import os
import re
import time
import asyncio
import nltk
import tempfile
import requests
import logging
from datetime import datetime
import speech_recognition as sr
import edge_tts
import pygame
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ─────────────────────────────────────────────
# CONFIGURATION & ENV LOADING
# ─────────────────────────────────────────────
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_KEY")

# ─────────────────────────────────────────────
# SESSION LOGGING
# ─────────────────────────────────────────────
_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
_sessions_dir = os.path.join(os.path.dirname(__file__), "sessions")
os.makedirs(_sessions_dir, exist_ok=True)
_log_path = os.path.join(_sessions_dir, f"session_{_session_id}.log")
logging.basicConfig(
    filename=_log_path,
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S",
)
def _log(msg: str):
    logging.info(msg)
    print(msg)

if not GOOGLE_API_KEY:
    print("❌ ERROR: GOOGLE_PLACES_KEY not found in .env file!")
    exit()

# City whitelist for STT correction (1000+ German cities + phonetic aliases)
from german_cities import GERMAN_CITIES

SLOTS = [
    "location", "past_experience", "datetime", "cuisine", "diet", 
    "budget", "group_size", "occasion", "distance", "special_features"
]

QUESTIONS = {
    "location":         "Which German city are you visiting right now? For example, Berlin, Munich, or Mainz.",
    "past_experience":  "Think of a restaurant you enjoyed recently. What did you like about it?",
    "datetime":         "When would you like to eat? For example, today at seven PM or Saturday for lunch.",
    "cuisine":          "What kind of food are you looking for? Italian, traditional German, or maybe Asian?",
    "diet":             "Do you have any dietary restrictions like vegan or gluten-free? Say 'none' if not.",
    "budget":           "How is your budget? Would you like it cheap, moderate, or fine dining?",
    "group_size":       "For how many people should I find a table?",
    "occasion":         "What is the occasion? Is it a casual meal, a date, or a business meeting?",
    "distance":         "How far do you want to travel? Within walking distance or anywhere in the city?",
    "special_features": "Any special requirements like outdoor seating or English menus? Say 'none' if not.",
}

# Short fragments used when bundling multiple slot questions into one utterance
SLOT_FRAGMENTS = {
    "location":         "which city are you in",
    "cuisine":          "what kind of food",
    "diet":             "any dietary restrictions",
    "budget":           "what is your budget — cheap, moderate, or fine dining",
    "group_size":       "how many people",
    "occasion":         "what is the occasion",
    "special_features": "any special requirements like outdoor seating",
    "datetime":         "when would you like to eat",
    "distance":         "how far are you willing to travel — walking distance or anywhere in the city",
}

HIGH_IMPACT_SLOTS = {"location", "cuisine", "diet"}

# Slots asked as targeted follow-ups if still empty after open question
CRITICAL_SLOTS = ["location", "cuisine", "diet", "budget"]
# Slots asked only if user hasn't volunteered them
OPTIONAL_SLOTS = ["group_size", "occasion", "special_features"]
# Slots auto-filled with "any" — not worth asking explicitly
AUTO_SKIP_SLOTS = set()  # all slots are now asked explicitly or in pairs

# ─────────────────────────────────────────────
# TTS ENGINE (edge-tts — Microsoft Neural Voice)
# ─────────────────────────────────────────────
class TTSEngine:
    def __init__(self):
        self.voice = "en-US-JennyNeural"
        pygame.mixer.init()

    def speak(self, text: str):
        import threading
        _log(f"\n[VocaDine] {text}")
        t = threading.Thread(target=lambda: asyncio.run(self._speak_async(text)))
        t.start()
        t.join()

    async def _speak_async(self, text: str):
        tmp_path = tempfile.mktemp(suffix=".mp3")
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(tmp_path)
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.unlink(tmp_path)

# ─────────────────────────────────────────────
# STT ENGINE (English Listening)
# ─────────────────────────────────────────────
class STTEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.5    # wait 1.5s of silence before cutting off
        self.recognizer.phrase_threshold = 0.3   # minimum speech length to count as a phrase

    def listen(self, language: str = "en-US") -> str | None:
        with sr.Microphone() as source:
            _log(f"[LISTENING] Please speak... ({language})")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=15)
                text = self.recognizer.recognize_google(audio, language=language)
                _log(f"[USER] {text}")
                return text.lower().strip()
            except:
                return None

# ─────────────────────────────────────────────
# GOOGLE PLACES CLIENT
# ─────────────────────────────────────────────
# [#16] Types that qualify a venue as a food/dining establishment.
# A venue must have at least one of these, or a type ending in '_restaurant',
# to pass the filter. Excludes shisha bars, nightclubs, and similar venues
# whose types contain only ["bar", "establishment"] or ["night_club"].
_FOOD_TYPES = frozenset({
    "restaurant", "food", "meal_takeaway", "meal_delivery", "cafe", "bakery",
})

def _is_food_venue(biz: dict) -> bool:
    """Return True if the venue is a food/dining establishment."""
    types = set(biz.get("types", []))
    return bool(
        types & _FOOD_TYPES
        or any(t.endswith("_restaurant") for t in types)
    )


class GooglePlacesClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self._geocode_cache: dict[str, tuple[float, float] | None] = {}

    def _geocode_city(self, city: str) -> tuple[float, float] | None:
        """[#17] Geocode a German city name to (lat, lng) using the Google Geocoding API.
        Result is cached per session — called at most once per city.
        Returns None on failure; caller falls back to text-only query."""
        if city in self._geocode_cache:
            return self._geocode_cache[city]
        try:
            resp = requests.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={"address": f"{city}, Germany", "key": self.api_key},
                timeout=5,
            )
            data = resp.json()
            if data.get("status") == "OK":
                loc = data["results"][0]["geometry"]["location"]
                coords = (loc["lat"], loc["lng"])
                self._geocode_cache[city] = coords
                _log(f"[GEOCODE] {city} → {coords[0]:.4f}, {coords[1]:.4f}")
                return coords
        except Exception as e:
            _log(f"[GEOCODE ERROR] {city}: {e}")
        self._geocode_cache[city] = None
        return None

    def _build_query(self, slots: dict) -> str:
        parts = []
        if slots.get("cuisine"): parts.append(slots["cuisine"])
        if slots.get("diet") and slots["diet"] != "none": parts.append(slots["diet"])
        parts.append("restaurant")
        if slots.get("location"): parts.append(f"in {slots['location']} Germany")
        if slots.get("special_features") and slots["special_features"] != "none":
            parts.append(slots["special_features"])
        return " ".join(parts)

    def probe(self, slots: dict) -> int:
        """Lightweight availability check using the same Places API (New) endpoint as full_fetch().
        Uses minimal FieldMask (places.id only) to minimise quota cost.
        Returns result count, 0 for ZERO_RESULTS, -1 on error."""
        if not slots.get("location"): return -1
        new_url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id",
        }
        body = {"textQuery": self._build_query(slots), "languageCode": "en"}
        try:
            resp = requests.post(new_url, headers=headers, json=body, timeout=5)
            data = resp.json()
            places = data.get("places", [])
            return len(places)
        except: return -1

    def full_fetch(self, slots: dict) -> list[dict]:
            new_url = "https://places.googleapis.com/v1/places:searchText"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.priceLevel,places.types,places.editorialSummary,places.reviews,places.outdoorSeating,places.goodForGroups,places.priceRange"
            }
            body = {
                "textQuery": self._build_query(slots),
                "languageCode": "en",
            }
            # [#17] Apply 3km radius bias when a specific city is known.
            # Prevents Berlin-Zehlendorf users from getting Charlottenburg results (6km away).
            # Falls back to text-only query if geocoding fails.
            city = slots.get("location")
            if city and city != "any":
                coords = self._geocode_city(city)
                if coords:
                    body["locationBias"] = {
                        "circle": {
                            "center": {"latitude": coords[0], "longitude": coords[1]},
                            "radius": 3000.0,
                        }
                    }
            try:
                resp = requests.post(new_url, headers=headers, json=body, timeout=10)
                data = resp.json()
                # Places API (New) returns results under the 'places' key
                results = data.get("places", [])
                # Normalise field names so downstream code can use biz['name'] consistently
                mapped_results = []
                for p in results:
                    p['name'] = p.get('displayName', {}).get('text', 'Unknown')
                    p['formatted_address'] = p.get('formattedAddress', '')
                    mapped_results.append(p)
                # [#16] Filter out non-food venues (shisha bars, nightclubs, etc.)
                before = len(mapped_results)
                mapped_results = [p for p in mapped_results if _is_food_venue(p)]
                filtered = before - len(mapped_results)
                if filtered:
                    _log(f"[FILTER] Removed {filtered} non-food venue(s) from results.")
                return mapped_results
            except Exception as e:
                print(f"[GOOGLE FETCH ERROR] {e}")
                return []

# ─────────────────────────────────────────────
# NLU & ML RANKING
# ─────────────────────────────────────────────

# spaCy entity label → dialog slot name
_SPACY_LABEL_TO_SLOT = {
    "LOCATION":   "location",
    "CUISINE":    "cuisine",
    "DIET":       "diet",
    "BUDGET":     "budget",
    "GROUP_SIZE": "group_size",
}

# Normalise raw spaCy entity text → canonical slot value
def _normalise_spacy_value(slot: str, raw: str) -> str | None:
    t = raw.lower().strip()

    if slot == "location":
        # Try city whitelist first; fall back to title-cased raw text
        for key, canonical in GERMAN_CITIES.items():
            if re.search(r'\b' + re.escape(key) + r'\b', t):
                return canonical
        return raw.strip().title()

    if slot == "cuisine":
        return raw.strip().title()

    if slot == "diet":
        norm = {
            "vegan": "vegan", "plant-based": "vegan", "plant based": "vegan",
            "vegetarian": "vegetarian", "veggie": "vegetarian",
            "gluten-free": "gluten-free", "gluten free": "gluten-free",
            "halal": "halal", "kosher": "kosher",
            "pescatarian": "pescatarian", "dairy-free": "dairy-free",
            "dairy free": "dairy-free", "lactose-free": "dairy-free",
            "nut-free": "nut-free",
        }
        for k, v in norm.items():
            if k in t:
                return v
        return t  # unknown diet restriction — keep as-is

    if slot == "budget":
        fine   = ["fine dining", "upscale", "luxury", "fancy", "upmarket", "splash out"]
        cheap  = ["cheap", "inexpensive", "affordable", "budget", "tight", "pennies",
                  "budget-friendly", "low budget"]
        mod    = ["moderate", "mid-range", "mid range", "reasonable", "average",
                  "not too expensive", "nothing fancy", "somewhere in between", "normal"]
        for kw in fine:
            if kw in t: return "fine dining"
        for kw in cheap:
            if kw in t: return "cheap"
        for kw in mod:
            if kw in t: return "moderate"
        return None  # unrecognised budget phrase — skip

    if slot == "group_size":
        word_nums = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
                     "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
                     "solo": "1", "just me": "1", "alone": "1",
                     "a couple": "2", "pair": "2", "the two of us": "2",
                     "family": "4", "large group": "6", "small group": "3"}
        for kw, num in word_nums.items():
            if kw in t: return num
        m = re.search(r'\b(\d+)\b', t)
        if m: return m.group(1)
        return None

    return None


class NLU:
    """
    Named Entity Recognition for VocaDine slot filling.

    Primary:  spaCy NER model trained on 600 domain utterances
              (models/vocadine_nlu/ — produced by train_nlu.py).
    Fallback: Rule-based extraction (city whitelist + keyword maps)
              used when the model directory is missing or on import error.
    """

    _MODEL_PATH = "models/vocadine_nlu"

    def __init__(self):
        self.nlp = None
        try:
            import spacy
            from pathlib import Path
            model_path = Path(__file__).parent / self._MODEL_PATH
            if model_path.exists():
                self.nlp = spacy.load(str(model_path))
                print(f"[NLU] spaCy model loaded from {model_path}")
            else:
                print(f"[NLU] spaCy model not found at {model_path} — rule-based fallback only.")
                print(f"      Run 'python train_nlu.py' to build the model.")
        except ImportError:
            print("[NLU] spaCy not installed — rule-based fallback only.")
        except Exception as e:
            print(f"[NLU] Could not load spaCy model: {e} — rule-based fallback only.")

    def extract_all_spacy(self, text: str) -> dict:
        """
        Run spaCy NER over text and return {slot_name: value} for all
        recognised entities. Returns empty dict if model not available.
        """
        if self.nlp is None:
            return {}
        doc = self.nlp(text)
        result = {}
        for ent in doc.ents:
            slot = _SPACY_LABEL_TO_SLOT.get(ent.label_)
            if slot and slot not in result:
                value = _normalise_spacy_value(slot, ent.text)
                if value:
                    result[slot] = value
        return result

    def extract(self, slot_name: str, text: str) -> str | None:
        """
        Single-slot extraction used as final fallback in _ask_slot().
        Tries spaCy first, then rule-based city whitelist for location.
        """
        t = text.lower().strip()

        # spaCy pass
        spacy_hits = self.extract_all_spacy(t)
        if slot_name in spacy_hits:
            return spacy_hits[slot_name]

        # Rule-based fallback for location
        if slot_name == "location":
            for key, canonical in GERMAN_CITIES.items():
                if re.search(r'\b' + re.escape(key) + r'\b', t):
                    return canonical
        return None

class RecommendationEngine:
    def rank(self, businesses: list[dict], slots: dict) -> list[dict]:
        if not businesses: return []
        
        def build_features(biz: dict) -> str:
            name = biz.get("name", "")
            types = " ".join(biz.get("types", []))
            summary = biz.get("editorialSummary", {}).get("text", "")
            reviews = " ".join(
                r.get("text", {}).get("text", "")
                for r in biz.get("reviews", [])[:3]
            )
            # Inject structured attributes as text tokens so TF-IDF can match them
            attrs = []
            if biz.get("outdoorSeating"): attrs.append("outdoor seating terrace")
            if biz.get("goodForGroups"): attrs.append("good for groups large party")
            return f"{name} {types} {summary} {reviews} {' '.join(attrs)}".lower()

        def budget_bonus(biz: dict, budget_slot: str) -> float:
            """+0.1 if priceRange matches the user's budget slot."""
            price_range = biz.get("priceRange", {})
            end_price = float(price_range.get("endPrice", {}).get("units", 0) or 0)
            if end_price == 0:
                return 0.0
            if budget_slot == "cheap" and end_price <= 15:       return 0.1
            if budget_slot == "moderate" and 15 < end_price <= 35: return 0.1
            if budget_slot in ("fine dining", "expensive") and end_price > 35: return 0.1
            return 0.0

        def attribute_bonus(biz: dict) -> float:
            """Small bonuses for structured attribute matches with user slots."""
            bonus = 0.0
            special = (slots.get("special_features") or "").lower()
            if "outdoor" in special and biz.get("outdoorSeating"):
                bonus += 0.1
            group = slots.get("group_size")
            if group and str(group).isdigit() and int(group) >= 4 and biz.get("goodForGroups"):
                bonus += 0.1
            return bonus

        user_pref = f"{slots.get('cuisine')} {slots.get('diet')} {slots.get('occasion')} {slots.get('past_experience', '')}".lower()
        biz_features = [build_features(b) for b in businesses]

        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf = vectorizer.fit_transform(biz_features + [user_pref])
            scores = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()
        except: scores = [0.0] * len(businesses)

        ranked = []
        for i, biz in enumerate(businesses):
            rating = biz.get("rating", 0)
            combined = (
                (scores[i] * 0.4)
                + ((rating / 5.0) * 0.6)
                + budget_bonus(biz, slots.get("budget", ""))
                + attribute_bonus(biz)
            )
            ranked.append((combined, biz))

        ranked.sort(key=lambda x: x[0], reverse=True)
        return [b for _, b in ranked[:3]]

# ─────────────────────────────────────────────
# IMPATIENCE DETECTOR
# ─────────────────────────────────────────────
class ImpatienceDetector:
    """Two-signal impatience detection: VADER sentiment + keyword rules.
    VADER catches frustrated phrasing even without explicit stop-words.
    Keywords catch explicit requests to stop."""

    _KEYWORDS = re.compile(
        r'\b(stop|enough|too long|hurry|come on|forget it|just go|'
        r'tired of this|annoyed|frustrated|speed up|move on|skip|'
        r'just find|search now|stop asking|taking too long|just search|'
        r'i already told|i just told|i just said|i just explained|'
        r'already said|not explaining|told you|said that already)\b'
    )

    def __init__(self):
        self.vader_available = False
        try:
            from nltk.sentiment.vader import SentimentIntensityAnalyzer
            import nltk
            try:
                self._sia = SentimentIntensityAnalyzer()
            except LookupError:
                nltk.download('vader_lexicon', quiet=True)
                self._sia = SentimentIntensityAnalyzer()
            self.vader_available = True
            print("[ImpatienceDetector] VADER loaded.")
        except ImportError:
            print("[ImpatienceDetector] NLTK not installed — keyword-only mode.")

    def score(self, transcript: str) -> float:
        """Returns VADER compound score (-1.0 … +1.0). Falls back to 0.0."""
        if self.vader_available:
            return self._sia.polarity_scores(transcript)['compound']
        return 0.0

    def is_impatient(self, transcript: str, slot_filled: bool) -> bool:
        """Returns True when user signals impatience.
        Combines VADER negative sentiment with keyword or empty-slot signal."""
        t = transcript.lower().strip()
        keyword_hit = bool(self._KEYWORDS.search(t))
        compound = self.score(t)
        # Strong frustration even without keyword
        vader_strong = compound < -0.5
        # Mild frustration + no useful answer extracted
        vader_mild_no_info = compound < -0.2 and not slot_filled
        return keyword_hit or vader_strong or vader_mild_no_info

# ─────────────────────────────────────────────
# DIALOG MANAGER
# ─────────────────────────────────────────────
class DialogStateManager:
    def __init__(self, tts, stt, api, nlu):
        self.tts, self.stt, self.api, self.nlu = tts, stt, api, nlu
        self.impatience = ImpatienceDetector()
        self.slots = {s: None for s in SLOTS}

    def _extract_multiple_slots(self, transcript: str) -> list[str]:
        """Extract multiple slot values from a single utterance.
        Returns a list of human-readable confirmation strings for TTS feedback."""
        confirmed = []

        # spaCy pass — fill LOCATION / CUISINE / DIET / BUDGET / GROUP_SIZE if model available
        spacy_hits = self.nlu.extract_all_spacy(transcript)
        for slot, value in spacy_hits.items():
            if slot in self.slots and not self.slots.get(slot):
                self.slots[slot] = value
                label_map = {
                    "location":   f"{value} as your location",
                    "cuisine":    f"{value} cuisine",
                    "diet":       f"{value} as dietary preference",
                    "budget":     f"{value} budget",
                    "group_size": f"a group of {value}",
                }
                hint = label_map.get(slot, f"{value}")
                confirmed.append(hint)

        # Location — fallback: word-boundary whitelist if spaCy missed it
        if not self.slots.get("location"):
            for key, canonical in GERMAN_CITIES.items():
                if re.search(r'\b' + re.escape(key) + r'\b', transcript):
                    self.slots["location"] = canonical
                    confirmed.append(f"{canonical} as your location")
                    break

        # Cuisine — fallback keyword list
        cuisines = ["italian", "turkish", "asian", "german food", "traditional german",
                    "french", "indian", "japanese", "chinese", "greek", "mexican",
                    "thai", "american", "burger", "burgers", "pizza", "sushi",
                    "kebab", "doner", "dooner", "doona", "döner", "vietnamese", "spanish"]
        if not self.slots.get("cuisine"):
            for cuisine in cuisines:
                if cuisine in transcript:
                    self.slots["cuisine"] = cuisine.title()
                    confirmed.append(f"{cuisine.title()} cuisine")
                    break

        # Diet — fallback keyword list
        diets = ["vegan", "vegetarian", "gluten-free", "halal", "kosher"]
        if not self.slots.get("diet"):
            for diet in diets:
                if diet in transcript:
                    self.slots["diet"] = diet
                    confirmed.append(f"{diet} as dietary preference")
                    break
            if not self.slots.get("diet"):
                if re.search(r'\b(none|no restrictions?|eat everything|eat anything|all good|everything is fine|no dietary|eat meat|i eat meat|meat eater|no special diet|no diet)\b', transcript):
                    self.slots["diet"] = "none"
                elif re.search(r"^no\b", transcript):
                    self.slots["diet"] = "none"

        # Budget — fallback keyword map
        budget_map = [
            ("fine dining", "fine dining"), ("expensive", "fine dining"), ("fancy", "fine dining"),
            ("upscale", "fine dining"), ("high end", "fine dining"),
            ("moderate", "moderate"), ("mid range", "moderate"), ("average", "moderate"),
            ("average price", "moderate"), ("normal price", "moderate"), ("regular", "moderate"),
            ("not too expensive", "moderate"), ("nothing too expensive", "moderate"),
            ("nothing fancy", "moderate"), ("somewhere in between", "moderate"),
            ("cheap", "cheap"), ("tight budget", "cheap"), ("low budget", "cheap"),
            ("affordable", "cheap"), ("inexpensive", "cheap"), ("on a budget", "cheap"),
        ]
        if not self.slots.get("budget"):
            for keyword, label in budget_map:
                if keyword in transcript:
                    self.slots["budget"] = label
                    confirmed.append(f"{label} budget")
                    break

        # Occasion
        occasion_map = [
            ("romantic", "date"), ("date", "date"), ("anniversary", "date"),
            ("business", "business meeting"), ("work dinner", "business meeting"),
            ("family", "family"), ("kids", "family"), ("children", "family"),
            ("casual", "casual"), ("just eating", "casual"), ("just dinner", "casual"),
            ("just lunch", "casual"), ("just want to eat", "casual"), ("have dinner", "casual"),
            ("have lunch", "casual"), ("grab a bite", "casual"),
        ]
        if not self.slots.get("occasion"):
            for keyword, label in occasion_map:
                if keyword in transcript:
                    self.slots["occasion"] = label
                    confirmed.append(f"{label} as occasion")
                    break

        # Datetime
        if not self.slots.get("datetime"):
            datetime_map = [
                ("right now", "right now"), ("now", "right now"),
                ("tonight", "tonight"), ("this evening", "tonight"),
                ("today", "today"), ("this afternoon", "this afternoon"),
                ("tomorrow", "tomorrow"), ("tomorrow evening", "tomorrow evening"),
                ("for lunch", "lunch"), ("at lunch", "lunch"),
                ("for dinner", "dinner"), ("at dinner", "dinner"),
                ("this weekend", "this weekend"), ("saturday", "saturday"), ("sunday", "sunday"),
            ]
            for keyword, label in datetime_map:
                if keyword in transcript:
                    self.slots["datetime"] = label
                    confirmed.append(f"{label}")
                    break
            # Fallback: store raw text if time expression not matched
            if not self.slots.get("datetime") and re.search(
                r'\b(at|around|by|before|after)\s+\d', transcript
            ):
                match = re.search(r'\b((?:at|around|by|before|after)\s+[\w\s:]+(?:am|pm)?)', transcript)
                if match:
                    self.slots["datetime"] = match.group(1).strip()
                    confirmed.append(match.group(1).strip())

        # Distance
        distance_map = [
            ("close by", "walking"), ("nearby", "walking"), ("near me", "walking"),
            ("walking distance", "walking"), ("not too far", "walking"),
            ("anywhere", "anywhere"), ("anywhere in the city", "anywhere"),
        ]
        if not self.slots.get("distance"):
            for keyword, label in distance_map:
                if keyword in transcript:
                    self.slots["distance"] = label
                    confirmed.append(f"{label} distance")
                    break

        # Group size — "around X", "just the two of us", "me and my X", digits, word numbers
        if not self.slots.get("group_size"):
            # "just the two of us" / "the two of us"
            if re.search(r'\b(just the |the )?two of us\b', transcript):
                self.slots["group_size"] = "2"
                confirmed.append("a group of 2")
            # "me and my family/friends/team/colleagues" — implies more than 2
            elif re.search(r'\b(me and my|with my) (family|friends|team|colleagues|group|crew)\b', transcript):
                self.slots["group_size"] = "4"
                confirmed.append("a group of 4")
            # "me and my / with my wife/girlfriend/partner/friend" — implies 2
            elif re.search(r'\b(me and my|with my) (wife|husband|girlfriend|boyfriend|partner|friend|colleague|date)\b', transcript):
                self.slots["group_size"] = "2"
                confirmed.append("a group of 2")
            else:
                # "around X" or plain digit
                match = re.search(r'\b(?:around\s+)?(\d+)\b', transcript)
                if match:
                    self.slots["group_size"] = match.group(1)
                    confirmed.append(f"a group of {match.group(1)}")
                else:
                    word_nums = {"one": "1", "two": "2", "three": "3", "four": "4",
                                 "five": "5", "six": "6", "seven": "7", "eight": "8",
                                 "nine": "9", "ten": "10"}
                    for word, num in word_nums.items():
                        if re.search(r'\b' + word + r'\b', transcript):
                            self.slots["group_size"] = num
                            confirmed.append(f"a group of {num}")
                            break

        # "Surprise me" / "egal" — fill all remaining empty slots with "any"
        if re.search(r'\b(surprise me|no preference|egal)\b', transcript):
            for slot in SLOTS:
                if self.slots[slot] is None:
                    self.slots[slot] = "any"
            confirmed.append("__surprise__")

        # "Stop asking / just search" — user wants to skip remaining questions
        if re.search(r'\b(stop|enough|just go|search now|find me|stop asking|just search|that\'s enough|too long)\b', transcript):
            for slot in SLOTS:
                if self.slots[slot] is None:
                    self.slots[slot] = "any"
            confirmed.append("__stop__")

        return confirmed

    def _infer_diet_from_past_experience(self):
        """
        Infer diet slot from past_experience free-text if diet is still unknown.
        - Meat keyword + negation ("don't like meat") → diet = vegetarian
          KNOWN EDGE CASE: negation detection is shallow (no deep parsing).
          "They served meat and I don't like meat" may not always parse correctly
          if the negation is separated from the keyword by a long clause.
        - Meat keyword without negation → diet = none (no restrictions)
        - No meat keyword → no inference, diet question will be asked normally.
        """
        if self.slots.get("diet") is not None:
            return
        past = self.slots.get("past_experience", "") or ""
        past = past.lower()

        MEAT_KEYWORDS = [
            "meat", "chicken", "beef", "pork", "steak", "meatball",
            "burger", "sausage", "fish", "seafood", "bacon", "lamb", "duck"
        ]
        NEGATION_PATTERNS = [
            r"don'?t (like|eat|want|enjoy)",
            r"do not (like|eat|want|enjoy)",
            r"hate",
            r"can'?t eat",
            r"avoid",
            r"not a (fan|big fan)",
            r"i'?m not into",
        ]

        meat_found = any(kw in past for kw in MEAT_KEYWORDS)
        negation_found = any(re.search(p, past) for p in NEGATION_PATTERNS)

        if meat_found and negation_found:
            # User dislikes meat → likely vegetarian, but we can't be certain → ask
            # This is a known limitation: edge case documented in Error Analysis
            pass  # do not infer, let the diet question run normally
        elif meat_found:
            self.slots["diet"] = "none"

    def _detect_ambiguity(self, transcript: str) -> tuple | None:
        """Detect if transcript contains multiple competing values for a single slot.
        Returns (slot_name, [option_a, option_b]) or None."""
        cuisines = ["italian", "turkish", "asian", "german food", "traditional german",
                    "french", "indian", "japanese", "chinese", "greek", "mexican",
                    "thai", "american", "burger", "pizza", "sushi", "kebab",
                    "vietnamese", "spanish"]
        found = [c for c in cuisines if c in transcript]
        if len(found) >= 2:
            return ("cuisine", [c.title() for c in found[:2]])
        return None

    def _resolve_ambiguity(self, slot: str, options: list[str]):
        """Ask the user to pick between two ambiguous options for a slot."""
        self.tts.speak(f"I noticed you mentioned both {options[0]} and {options[1]}. Which would you prefer?")
        clarification = self.stt.listen()
        if clarification:
            self.slots[slot] = None  # reset so extraction can fill it cleanly
            self._extract_multiple_slots(clarification)
        if self.slots[slot] is None:
            self.slots[slot] = options[0]  # fallback to first mentioned

    def _ask_slot(self, slot: str):
        """Ask for a single slot, run implicit extraction, validate if high-impact."""
        self.tts.speak(QUESTIONS[slot])
        transcript = self.stt.listen()

        if transcript:
            confirmed = self._extract_multiple_slots(transcript)
            slot_filled = self.slots[slot] is not None or bool(confirmed)
            if "__stop__" in confirmed or self.impatience.is_impatient(transcript, slot_filled):
                print(f"[IMPATIENCE] compound={self.impatience.score(transcript):.2f}")
                for s in SLOTS:
                    if self.slots[s] is None:
                        self.slots[s] = "any"
                self.tts.speak("I'm sorry for taking so long! Let me find you something right away.")
                return
            if "__surprise__" in confirmed:
                self.tts.speak("Ok, I'll surprise you!")
            elif confirmed:
                self.tts.speak("Got it — " + " and ".join(confirmed) + ".")
            # Ambiguity check on follow-up answers too
            ambiguity = self._detect_ambiguity(transcript)
            if ambiguity:
                amb_slot, options = ambiguity
                self._resolve_ambiguity(amb_slot, options)
            if self.slots[slot] is None:
                self.slots[slot] = self.nlu.extract(slot, transcript)
            # Free-form slots: store raw transcript, confirm receipt
            if slot == "past_experience" and self.slots[slot] is None and transcript:
                self.slots[slot] = transcript
                if not confirmed:
                    self.tts.speak("Got it, I'll keep that in mind.")
            # Indifference fallback: "don't care / doesn't matter / not important" → any
            if self.slots[slot] is None:
                if re.search(r"\b(don'?t care|doesn'?t matter|not important|no preference|up to you|whatever|anything)\b", transcript):
                    self.slots[slot] = "any"
            # Location retry: if still empty after extraction, user named an unknown city
            if slot == "location" and self.slots["location"] is None:
                self.tts.speak("I'm sorry, I didn't catch the city. Could you spell it out or try again?")
                retry = self.stt.listen()
                if retry:
                    self.slots["location"] = self.nlu.extract("location", retry)
                if self.slots["location"] is None:
                    self.slots["location"] = "any"
            if slot in HIGH_IMPACT_SLOTS and self.slots[slot] not in (None, "any"):
                if self.api.probe(self.slots) == 0:
                    self.tts.speak(f"I'm sorry, I couldn't find any results for {self.slots[slot]}. Let's try another choice.")
                    self.slots[slot] = None
        else:
            self.tts.speak("No worries, I'll keep that open.")
            self.slots[slot] = "any"

    def _ask_bundled(self, slots: list[str]):
        """Ask multiple missing slots in a single question and extract all at once."""
        fragments = [SLOT_FRAGMENTS[s] for s in slots if s in SLOT_FRAGMENTS]
        if not fragments:
            return
        if len(fragments) == 1:
            question = QUESTIONS[slots[0]]
        else:
            question = "Just a couple more things — " + ", ".join(fragments[:-1]) + ", and " + fragments[-1] + "?"
        self.tts.speak(question)
        transcript = self.stt.listen()
        if not transcript:
            for s in slots:
                if self.slots[s] is None:
                    self.slots[s] = "any"
            return
        confirmed = self._extract_multiple_slots(transcript)
        slot_filled = any(self.slots[s] is not None for s in slots)
        if "__stop__" in confirmed or self.impatience.is_impatient(transcript, slot_filled):
            print(f"[IMPATIENCE] compound={self.impatience.score(transcript):.2f}")
            for s in SLOTS:
                if self.slots[s] is None:
                    self.slots[s] = "any"
            self.tts.speak("I'm sorry for taking so long! Let me find you something right away.")
            return
        if "__surprise__" in confirmed:
            self.tts.speak("Ok, I'll surprise you!")
        elif confirmed:
            readable = [c for c in confirmed if c not in ("__surprise__", "__stop__")]
            if readable:
                self.tts.speak("Got it — " + " and ".join(readable) + ".")

    def run_interview(self):
        self.tts.speak("Welcome to the VocaDine Germany restaurant guide.")

        # Open question — user can volunteer anything upfront
        self.tts.speak("Tell me what you are looking for: City, cuisine, any preferences.")
        transcript = self.stt.listen()
        if transcript:
            confirmed = self._extract_multiple_slots(transcript)
            if "__surprise__" in confirmed:
                self.tts.speak("Ok, I'll surprise you!")
            elif confirmed:
                readable = [c for c in confirmed if c != "__surprise__"]
                self.tts.speak("Great — I've noted " + " and ".join(readable) + ".")
            ambiguity = self._detect_ambiguity(transcript)
            if ambiguity:
                self._resolve_ambiguity(*ambiguity)

        if all(self.slots[s] is not None for s in SLOTS):
            return self.slots

        # Solo critical slots
        for slot in ["location", "cuisine"]:
            if self.slots[slot] is None:
                self._ask_slot(slot)
            if all(self.slots[s] is not None for s in SLOTS):
                return self.slots

        # past_experience — open-ended, asked alone after location/cuisine
        if self.slots["past_experience"] is None:
            self._ask_slot("past_experience")

        # Infer diet from past_experience before asking (may skip the question entirely)
        self._infer_diet_from_past_experience()

        # Paired slots: diet + budget together
        missing_diet_budget = [s for s in ["diet", "budget"] if self.slots[s] is None]
        if missing_diet_budget:
            self._ask_bundled(missing_diet_budget)
        if all(self.slots[s] is not None for s in SLOTS):
            return self.slots

        # Paired slots: group_size + occasion together
        missing_group_occasion = [s for s in ["group_size", "occasion"] if self.slots[s] is None]
        if missing_group_occasion:
            self._ask_bundled(missing_group_occasion)
        if all(self.slots[s] is not None for s in SLOTS):
            return self.slots

        # Paired slots: datetime + distance together ("when and where")
        missing_when_where = [s for s in ["datetime", "distance"] if self.slots[s] is None]
        if missing_when_where:
            self._ask_bundled(missing_when_where)
        if all(self.slots[s] is not None for s in SLOTS):
            return self.slots

        # special_features alone
        if self.slots["special_features"] is None:
            self._ask_slot("special_features")

        # Auto-skip remaining slots
        for slot in SLOTS:
            if self.slots[slot] is None:
                self.slots[slot] = "any"

        return self.slots

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    tts = TTSEngine()
    stt = STTEngine()
    api = GooglePlacesClient(GOOGLE_API_KEY)
    nlu = NLU()
    recommender = RecommendationEngine()
    dm = DialogStateManager(tts, stt, api, nlu)

    # 1. Interview
    final_slots = dm.run_interview()
    
    # 2. Fetch & Rank
    city = final_slots.get("location")
    city_display = city if city and city != "any" else "Germany"
    tts.speak(f"Thank you! I am now searching for the best matches in {city_display}.")
    results = api.full_fetch(final_slots)
    top3 = recommender.rank(results, final_slots)

    # 3. Output
    if not top3:
        tts.speak("I am very sorry, I could not find any restaurants that match your specific criteria.")
    else:
        tts.speak(f"I found {len(top3)} great options for you.")
        for i, biz in enumerate(top3, 1):
            msg = f"Option {i}: {biz['name']} with a rating of {biz.get('rating')} stars. Address: {biz.get('formatted_address')}"
            tts.speak(msg)

    tts.speak("Enjoy your stay in Germany and have a great meal. Goodbye!")

if __name__ == "__main__":
    main()