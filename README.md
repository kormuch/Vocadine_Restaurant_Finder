# VocaDine — Restaurant Voice Assistant for Tourists in Germany

**Course**: DLMAIWNLPVA02 — NLP and Voice Assistants
**Phase**: 2 (Working Prototype)
**Stack**: Python 3.12 · SpeechRecognition · pyttsx3 · Google Places API · scikit-learn

---

## Use Case

English-speaking tourist in a small German city (e.g. Haigerloch) searches for a restaurant via voice — without typing, without knowing German city names, without getting dead-end "0 results" responses.

---

## Key Differentiators vs. Alexa

| Feature | Alexa | VocaDine |
|---|---|---|
| German city STT | Fails on small cities | Whitelist of 1000+ cities + phonetic aliases |
| 0-results handling | Shows empty list | Validation probe rolls back the slot |
| Dialog flexibility | Rigid sequence | Implicit slot filling (fewer questions) |
| Ranking | Popularity only | TF-IDF similarity + Google rating (40/60) |

---

## Architecture

```
Microphone → STT (Google Web Speech, en-US)
           → NLU (keyword matching + GERMAN_CITIES dict)
           → DialogStateManager (10 slots, implicit filling)
           → Validation Probe (Google Places API)
           → full_fetch (Places API New)
           → RecommendationEngine (TF-IDF + cosine similarity)
           → TTS (pyttsx3, offline)
```

**Data flow**: `audio → text → slot_value → API_query → ranked results → speech`

---

## Installation

```bash
git clone https://github.com/kormuch/Vocadine_Restaurant_Finder.git
cd Vocadine_Restaurant_Finder
pip install -r requirements.txt
cp .env.example .env
# Add your Google Places API key to .env
```

### Requirements

- Python 3.12
- Working microphone
- Google Places API key (Text Search enabled)
- Windows: `pyaudio` via `pip install pyaudio` (or use the pre-built wheel)

---

## Run

```bash
python main.py
```

---

## Features

### 1. German City Whitelist (1000+ cities)
Prevents STT failures on German city names. Includes phonetic aliases:
- "Hi girl" → Haigerloch
- "higher lock" → Haigerloch
- "munich" → München

### 2. Implicit Slot Filling
A single utterance can fill multiple slots simultaneously:
> "I want Italian food in Berlin for two people"
> → `location=Berlin`, `cuisine=Italian`, `group_size=2`
> → TTS confirms: "I've noted Berlin as your location and Italian cuisine and a group of 2."
> → Result: fewer than 10 questions asked

### 3. Validation Probe
Before accepting a high-impact slot (location, cuisine, diet), the system probes the Google Places API. If 0 results would be returned, the slot is rolled back and the user is asked again.

### 4. TF-IDF Recommendation Engine
User preference string (`cuisine + diet + occasion`) is vectorized against restaurant feature strings (`name + types` from Places API).

```
score = (cosine_similarity * 0.4) + (google_rating / 5.0 * 0.6)
```

Top 3 results are read aloud via TTS.

---

## 10 Conversation Slots

| Slot | Question |
|---|---|
| location | Which German city are you visiting? |
| past_experience | A restaurant you enjoyed — what did you like? |
| datetime | When would you like to eat? |
| cuisine | What kind of food are you looking for? |
| diet | Any dietary restrictions? |
| budget | Cheap, moderate, or fine dining? |
| group_size | For how many people? |
| occasion | Casual, date, or business? |
| distance | Walking distance or anywhere in the city? |
| special_features | Outdoor seating, English menus, etc.? |

---

## Performance Metrics (Phase 2 Tests)

| Metric | Result |
|---|---|
| Task completion rate | 18/20 test runs (90%) |
| WER monosyllabic words | 2/10 before → 0/10 after synonym mapping |
| Google Places probe latency | avg. 1.2s |
| Slots filled per utterance (implicit) | up to 3 simultaneously |

---

## Known Limitations & Error Analysis

| # | Problem | Solution |
|---|---|---|
| 1 | Short words misrecognized ("no" → "know") | Synonym mapping |
| 2 | German city mispronunciation ("Haigerloch" → "Hi girl") | Phonetic alias whitelist |
| 3 | Irrelevant venue types (shisha bar) | Type filtering (Phase 3) |
| 4 | Geographic imprecision (wrong district) | Radius search (Phase 3) |
| 5 | Recording latency 2.5s | Reduced pause threshold → 1.8s |
| 6 | Ambiguous questions | Rephrased to location-specific phrasing |
| 7 | Audio sent to Google Cloud | No persistent storage, DSGVO-compliant |
| 8 | Analysis paralysis (50 results) | Top 3 only (Grice's Maxim) |

---

## Project Structure

```
vocadine/
├── main.py                # Core application (dialog, STT, TTS, ranking)
├── german_cities.py       # City whitelist + phonetic aliases
├── german_cities_list.py  # Full list of 1000+ German cities
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore
```

---

## Environment Variables

```
GOOGLE_PLACES_KEY=your_api_key_here
```
