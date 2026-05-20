# Design Document — VocaDine
**Much, Korbinian | IU14127772 | DLMAIWNLPVA02**

---

## 1. System Overview

VocaDine is a voice-based restaurant recommendation assistant for English-speaking tourists in Germany. The user interacts exclusively via voice. The system collects preferences through a conversational dialog, queries live restaurant data, ranks results, and reads the top 3 recommendations aloud.

All logic is contained in a single Python script (`main.py`) with one supporting module (`german_cities.py`). No framework runtime is required beyond standard pip dependencies.

---

## 2. Architecture Overview

The system follows a sequential pipeline architecture:

```
Microphone
    ↓ audio
STTEngine  (Google Web Speech API)
    ↓ transcript
NLU  (spaCy NER → rule fallback → GERMAN_CITIES whitelist)
    ↓ slot values
DialogStateManager  (10 slots, implicit filling, validation probe)
    ↓ confirmed slots
GooglePlacesClient  (Places API New — full fetch + locationBias)
    ↓ venue list
RecommendationEngine  (TF-IDF cosine + rating + bonuses)
    ↓ top 3
TTSEngine  (edge-tts, en-US-JennyNeural)
    ↓ spoken output
User
```

---

## 3. Component Descriptions

### 3.1 STTEngine (`main.py`)

Captures microphone input and converts speech to text using the Google Web Speech API (`speech_recognition` library, `en-US` language).

| Parameter | Value | Rationale |
|---|---|---|
| `pause_threshold` | 1.5s | Reduced from default 2.5s to minimise perceived lag |
| `phrase_time_limit` | 15s | Prevents indefinite recording |
| `timeout` | 7s | Returns `None` on silence; dialog re-prompts |

**Known limitation:** The Web Speech API does not expose confidence scores. Low-confidence results cannot be detected and re-prompted automatically.

---

### 3.2 GERMAN_CITIES Whitelist (`german_cities.py`)

A dictionary mapping 2058+ German city names to lists of phonetic alias strings — likely en-US STT transcriptions of those city names. Applied at two points in the NLU layer.

- Matching uses `re.search(r'\b{alias}\b', text, re.IGNORECASE)` to prevent substring false positives
- Aliases were created from observed STT failures and extended with LLM-assisted generation

---

### 3.3 NLU (`main.py`)

Two-pass slot extraction:

**Pass 1 — spaCy NER model** (`extract_all_spacy()`):
- Blank spaCy English model trained on 600 annotated utterances
- Labels: LOCATION, CUISINE, DIET, BUDGET, GROUP_SIZE
- Macro-F1 = 0.881 on 90 held-out test utterances
- Model loaded once at startup from `models/vocadine_nlu/`

**Pass 2 — Rule-based fallback** (`_extract_multiple_slots()`):
- Keyword maps for cuisine (20+ types), budget (20+ phrases), occasion (10+), datetime, distance
- Regex patterns for group size (word numbers, relationship phrases, digits)
- Negation handling for diet slot
- Covers slots outside the 5 trained NER labels (occasion, datetime, distance, special_features)

Additional NLU features:
- `_detect_ambiguity()`: triggers clarification when ≥2 cuisines appear in one utterance
- `_infer_diet_from_past_experience()`: infers diet=none from meat keywords without negation
- `ImpatienceDetector`: VADER sentiment (compound < −0.5) or stop keywords → skip remaining slots

---

### 3.4 DialogStateManager (`main.py`)

Manages the 10-slot conversation state using `run_interview()`.

| Slot | Type | Filled by |
|---|---|---|
| location | critical | NER / whitelist |
| cuisine | critical | NER / rules |
| diet | critical | NER / rules / inference |
| budget | critical | NER / rules |
| past_experience | open | Free text |
| datetime | optional | Rules |
| group_size | optional | NER / rules |
| occasion | optional | Rules |
| distance | optional | Rules |
| special_features | optional | Rules |

Questions are asked in semantically related pairs (diet+budget, group_size+occasion, datetime+distance) to reduce turn count. Slots filled by earlier utterances are skipped automatically.

---

### 3.5 GooglePlacesClient (`main.py`)

Two API call types:

**Probe** (`probe()`): Lightweight text search to validate a single slot value before accepting it. Returns result count only. 0 results → slot rolled back, user re-prompted.

**Full fetch** (`full_fetch()`): POST to `https://places.googleapis.com/v1/places:searchText`. Query string: `{cuisine} {diet} restaurant in {location} Germany {special_features}`. FieldMask requests: `displayName`, `formattedAddress`, `rating`, `types`, `editorialSummary`, `reviews`, `outdoorSeating`, `goodForGroups`, `priceRange`.

**Geographic bias**: `_geocode_city()` resolves city name to lat/lng via Google Geocoding API. Result cached per session. `locationBias` circle (3km radius) added to full fetch body. Falls back to text-only query if geocoding fails.

**Venue filtering**: `_is_food_venue()` applies an allowlist of food-specific Place types (`restaurant`, `food`, `meal_takeaway`, `meal_delivery`, `cafe`, `bakery`, `*_restaurant`). Non-food venues are excluded.

---

### 3.6 RecommendationEngine (`main.py`)

`build_features(venue)` constructs a feature string per venue:
```
name + types + editorialSummary + reviews[:3] + attribute tokens
```
Attribute tokens: "outdoor seating terrace" if `outdoorSeating=True`, "good for groups large party" if `goodForGroups=True`.

User preference string: `cuisine + diet + occasion + past_experience`

`rank()` runs `TfidfVectorizer.fit_transform()` on all feature strings and the user string at query time (on-demand — no saved model). Cosine similarity computed between user vector and each venue vector.

Scoring formula:
```
score = (cosine × 0.4) + (rating/5.0 × 0.6) + budget_bonus + attribute_bonus
```
- `budget_bonus`: +0.1 if `priceRange.endPrice` matches budget slot
- `attribute_bonus`: +0.1 for outdoor seating match, +0.1 for goodForGroups when group ≥ 4

Top 3 returned.

---

### 3.7 TTSEngine (`main.py`)

Uses `edge-tts` (Microsoft Azure Neural voices, no API key required). Voice: `en-US-JennyNeural`. Output written to a temporary file and played via `pygame.mixer`. Async generation with synchronous playback.

Selected over `pyttsx3` due to: COM Exception in Spyder/IPython environment; unreliable short utterance handling; no clean context release between test runs.

---

## 4. Data Flow Summary

| Data | From | To | Stored |
|---|---|---|---|
| Audio (PCM) | Microphone | Google Cloud (STT) | No |
| Transcript | Google Cloud | NLU layer | Session memory |
| Slot values | NLU | DialogStateManager | Session memory |
| Text query + location | DialogStateManager | Google Cloud (Places API) | No |
| Venue JSON | Google Places API | RecommendationEngine | Session memory |
| TTS audio | edge-tts (Azure) | Speaker | Temp file, deleted after playback |

No data is written to disk persistently. All session state is lost on program exit.

---

## 5. Technology Stack

| Component | Library / Service | Version |
|---|---|---|
| STT | `speech_recognition` + Google Web Speech API | 3.10+ |
| NLU (trained) | `spaCy` blank en model | 3.x |
| NLU (sentiment) | `vaderSentiment` | 3.3.2 |
| Ranking | `scikit-learn` TfidfVectorizer | 1.x |
| Places API | Google Places API (New) | v1 |
| Geocoding | Google Geocoding API | v1 |
| TTS | `edge-tts` | 6.x |
| Audio playback | `pygame.mixer` | 2.x |
| Language | Python | 3.12 |

---

## 6. Module Structure

```
main.py                  ← All core logic (STT, NLU, Dialog, API, Ranking, TTS)
german_cities.py         ← GERMAN_CITIES whitelist dict
train_nlu.py             ← spaCy NER training script
eval_nlu.py              ← NER evaluation script
data/
  training_data.py       ← 600 annotated utterances
  annotation_guidelines.md
models/
  vocadine_nlu/          ← Trained spaCy model (best checkpoint)
```
