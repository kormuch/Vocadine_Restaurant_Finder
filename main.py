"""
VocaDine Germany — Portfolio Prototype
Usecase: English-speaking tourist in Germany.
Architecture: STT (English) → Dialog Management → Google Places API → ML Ranking → TTS (English)
"""

import os
import re
import time
import requests
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ─────────────────────────────────────────────
# CONFIGURATION & ENV LOADING
# ─────────────────────────────────────────────
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_KEY")

if not GOOGLE_API_KEY:
    print("❌ ERROR: GOOGLE_PLACES_KEY not found in .env file!")
    exit()

# City whitelist for STT correction (Helping the tourist with German names)
GERMAN_CITIES = {
    "berlin": "Berlin", "hamburg": "Hamburg", "munich": "Munich", "münchen": "Munich",
    "cologne": "Cologne", "köln": "Cologne", "frankfurt": "Frankfurt", "mainz": "Mainz",
    "stuttgart": "Stuttgart", "düsseldorf": "Düsseldorf", "leipzig": "Leipzig", "bonn": "Bonn"
}

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

HIGH_IMPACT_SLOTS = {"location", "cuisine", "diet"}

# ─────────────────────────────────────────────
# TTS ENGINE (English Voice)
# ─────────────────────────────────────────────
class TTSEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 170)
        voices = self.engine.getProperty('voices')
        # Ensure an English voice is selected
        for voice in voices:
            if "english" in voice.name.lower() or "en_US" in voice.id or "en_GB" in voice.id:
                self.engine.setProperty('voice', voice.id)
                break

    def speak(self, text: str):
        print(f"\n[VocaDine] {text}")
        self.engine.say(text)
        self.engine.runAndWait()

# ─────────────────────────────────────────────
# STT ENGINE (English Listening)
# ─────────────────────────────────────────────
class STTEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self, language: str = "en-US") -> str | None:
        with sr.Microphone() as source:
            print(f"[LISTENING] Please speak... ({language})")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio, language=language)
                print(f"[USER] {text}")
                return text.lower().strip()
            except:
                return None

# ─────────────────────────────────────────────
# GOOGLE PLACES CLIENT
# ─────────────────────────────────────────────
class GooglePlacesClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

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
        if not slots.get("location"): return -1
        params = {"query": self._build_query(slots), "key": self.api_key, "language": "en"}
        try:
            resp = requests.get(self.url, params=params, timeout=5)
            data = resp.json()
            if data.get("status") == "ZERO_RESULTS": return 0
            return len(data.get("results", []))
        except: return -1

    def full_fetch(self, slots: dict) -> list[dict]:
            # Wir nutzen die Text Search (New) URL
            new_url = "https://places.googleapis.com/v1/places:searchText"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.priceLevel,places.types"
            }
            body = {
                "textQuery": self._build_query(slots),
                "languageCode": "en"
            }
            try:
                resp = requests.post(new_url, headers=headers, json=body, timeout=10)
                data = resp.json()
                # Die "New" API gibt die Ergebnisse im Feld 'places' zurück
                results = data.get("places", [])
                # Wir mappen die Namen kurz um, damit der Rest vom Skript (biz['name']) funktioniert
                mapped_results = []
                for p in results:
                    p['name'] = p.get('displayName', {}).get('text', 'Unknown')
                    p['formatted_address'] = p.get('formattedAddress', '')
                    mapped_results.append(p)
                return mapped_results
            except Exception as e:
                print(f"[GOOGLE FETCH ERROR] {e}")
                return []

# ─────────────────────────────────────────────
# NLU & ML RANKING
# ─────────────────────────────────────────────
class NLU:
    def extract(self, slot_name: str, text: str) -> str | None:
        text = text.lower().strip()
        if slot_name == "location":
            for key, canonical in GERMAN_CITIES.items():
                if key in text: return canonical
        return text

class RecommendationEngine:
    def rank(self, businesses: list[dict], slots: dict) -> list[dict]:
        if not businesses: return []
        
        def build_features(biz: dict) -> str:
            types = " ".join(biz.get("types", []))
            name = biz.get("name", "")
            return f"{name} {types}".lower()

        user_pref = f"{slots.get('cuisine')} {slots.get('diet')} {slots.get('occasion')}".lower()
        biz_features = [build_features(b) for b in businesses]
        
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf = vectorizer.fit_transform(biz_features + [user_pref])
            scores = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()
        except: scores = [0.0] * len(businesses)

        ranked = []
        for i, biz in enumerate(businesses):
            rating = biz.get("rating", 0)
            combined = (scores[i] * 0.4) + ((rating / 5.0) * 0.6) # Slight bias towards ratings for tourists
            ranked.append((combined, biz))

        ranked.sort(key=lambda x: x[0], reverse=True)
        return [b for _, b in ranked[:3]]

# ─────────────────────────────────────────────
# DIALOG MANAGER
# ─────────────────────────────────────────────
class DialogStateManager:
    def __init__(self, tts, stt, api, nlu):
        self.tts, self.stt, self.api, self.nlu = tts, stt, api, nlu
        self.slots = {s: None for s in SLOTS}

    def _extract_multiple_slots(self, transcript: str) -> list[str]:
        """Extract multiple slot values from a single utterance.
        Returns a list of human-readable confirmation strings for TTS feedback."""
        confirmed = []

        # Location
        if not self.slots.get("location"):
            for key, canonical in GERMAN_CITIES.items():
                if key in transcript:
                    self.slots["location"] = canonical
                    confirmed.append(f"{canonical} as your location")
                    break

        # Cuisine
        cuisines = ["italian", "turkish", "asian", "german", "french", "indian",
                    "japanese", "chinese", "greek", "mexican", "thai", "american"]
        if not self.slots.get("cuisine"):
            for cuisine in cuisines:
                if cuisine in transcript:
                    self.slots["cuisine"] = cuisine.title()
                    confirmed.append(f"{cuisine.title()} cuisine")
                    break

        # Diet
        diets = ["vegan", "vegetarian", "gluten-free", "halal", "kosher"]
        if not self.slots.get("diet"):
            for diet in diets:
                if diet in transcript:
                    self.slots["diet"] = diet
                    confirmed.append(f"{diet} as dietary preference")
                    break
            if not self.slots.get("diet") and "none" in transcript:
                self.slots["diet"] = "none"

        # Budget
        budget_map = [("fine dining", "fine dining"), ("expensive", "fine dining"),
                      ("moderate", "moderate"), ("cheap", "cheap"), ("budget", "cheap")]
        if not self.slots.get("budget"):
            for keyword, label in budget_map:
                if keyword in transcript:
                    self.slots["budget"] = label
                    confirmed.append(f"{label} budget")
                    break

        # Group size — digits first, then word numbers
        if not self.slots.get("group_size"):
            match = re.search(r'\b(\d+)\b', transcript)
            if match:
                self.slots["group_size"] = match.group(1)
                confirmed.append(f"a group of {match.group(1)}")
            else:
                word_nums = {"one": "1", "two": "2", "three": "3", "four": "4",
                             "five": "5", "six": "6", "seven": "7", "eight": "8"}
                for word, num in word_nums.items():
                    if word in transcript:
                        self.slots["group_size"] = num
                        confirmed.append(f"a group of {num}")
                        break

        return confirmed

    def run_interview(self):
        self.tts.speak("Welcome to VocaDine Germany. I am your local assistant for finding the best places to eat.")
        self.tts.speak("I will ask you a few quick questions to tailor my recommendation.")

        for slot in SLOTS:
            if self.slots[slot] is not None:
                continue  # Already filled via implicit extraction — skip question

            self.tts.speak(QUESTIONS[slot])
            transcript = self.stt.listen()

            if transcript:
                # Implicit slot filling: one answer may fill multiple slots at once
                confirmed = self._extract_multiple_slots(transcript)

                if confirmed:
                    feedback = "I've noted " + " and ".join(confirmed) + "."
                    self.tts.speak(feedback)

                # If current slot still empty after multi-extraction, use single-slot NLU
                if self.slots[slot] is None:
                    value = self.nlu.extract(slot, transcript)
                    self.slots[slot] = value

                # Validate high-impact slots against the API (probe)
                if slot in HIGH_IMPACT_SLOTS and self.slots[slot] not in (None, "any"):
                    if self.api.probe(self.slots) == 0:
                        self.tts.speak(f"I'm sorry, I couldn't find any results for {self.slots[slot]}. Let's try another choice.")
                        self.slots[slot] = None
            else:
                self.tts.speak("I didn't catch that, I'll just skip this for now.")
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
    tts.speak("Thank you! I am now searching for the best matches in Germany.")
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