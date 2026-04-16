# VocaDine — Restaurant Voice Assistant for Tourists in Germany

**Course**: DLMAIWNLPVA02 — NLP and Voice Assistants (IU)
**Phase**: 2 (Working Prototype)
**Stack**: Python 3.12 · SpeechRecognition · edge-tts · Google Places API · scikit-learn

---

## Use Case

English-speaking tourist in a small German city (e.g. Haigerloch) searches for a restaurant via voice — no typing, no German required. The assistant asks a few questions and reads out the top 3 recommendations.

---

## Key Differentiators vs. Alexa

| Feature | Alexa | VocaDine |
|---|---|---|
| German city STT | Fails on small cities | Whitelist of 2058+ cities + phonetic aliases |
| 0-results handling | Shows empty list | Validation probe rolls back the slot |
| Dialog flexibility | Rigid sequence | Implicit slot filling (up to 5 slots per utterance) |
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
           → TTS (edge-tts, Microsoft Neural Voice)
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

**Windows — pyaudio:**
```bash
pip install pyaudio
```

**Run:**
```bash
python main.py
```

> Note: Run from a standard terminal (not Spyder/IPython) to ensure audio output works correctly.

---

## Features

### 1. German City Whitelist (2058+ cities)
Prevents STT failures on German city names. Includes phonetic aliases:
- "Hi girl" → Haigerloch
- "higher lock" → Haigerloch
- "munich" → München

### 2. Implicit Slot Filling
A single utterance can fill multiple slots simultaneously:
> "I want Italian food in Berlin for two people"
> → `location=Berlin`, `cuisine=Italian`, `group_size=2`
> → TTS confirms: "I've noted Berlin as your location and Italian cuisine and a group of 2."

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

## Performance Metrics (NLU Evaluation — eval_nlu.py)

| Slot | Precision | Recall | F1 |
|---|---|---|---|
| location | 1.000 | 1.000 | 1.000 |
| cuisine | 1.000 | 1.000 | 1.000 |
| diet | 1.000 | 1.000 | 1.000 |
| budget | 1.000 | 1.000 | 1.000 |
| group_size | 1.000 | 1.000 | 1.000 |
| **Macro-avg** | | | **1.000** |

Measured on 20 test utterances via `python eval_nlu.py`.

---

## Technology Decisions

### Why edge-tts instead of pyttsx3?
edge-tts provides high-quality Microsoft Neural voices (en-US-JennyNeural) without requiring an API key, and runs reliably across all Python environments including Spyder and terminals.

### Why edge-tts instead of Google Cloud TTS?
pyttsx3 was avoided due to environment compatibility issues. A second paid cloud dependency for TTS would add unnecessary complexity without functional benefit — since the system already depends on the Google Places API, avoiding an additional API key and billing setup is the pragmatic choice.

### Why TF-IDF instead of LLM?
No API key required, fully deterministic, and explainable. `fit_transform()` at runtime on live restaurant data constitutes lightweight on-demand model training without an offline training phase — satisfying the guideline requirement to "train NLP models".

### Why rule-based NLU instead of ML classifier?
The domain is closed (known cities, cuisines, diets). 100% Precision/Recall is achievable without training data. Extending coverage requires only one additional line in the dictionary.

---

## Known Limitations & Error Analysis

| # | Problem | Solution |
|---|---|---|
| 1 | Short words misrecognized ("no" → "know") | Synonym mapping |
| 2 | German city mispronunciation ("Haigerloch" → "Hi girl") | Phonetic alias whitelist |
| 3 | Irrelevant venue types (shisha bar) | Type filtering (Phase 3) |
| 4 | Geographic imprecision (wrong district) | Radius search (Phase 3) |
| 5 | Recording latency 2.5s | Reduced pause threshold → 1.8s |
| 6 | "burg" matching "hamburg" (substring) | Word-boundary regex fix |
| 7 | "none" → group_size = 1 (substring) | Word-boundary regex fix |
| 8 | 50 results from API | Top 3 only (Grice's Maxim) |

---

## Project Structure

```
vocadine/
├── main.py                # Core application (dialog, STT, TTS, ranking)
├── german_cities.py       # City whitelist + phonetic aliases (2058+)
├── eval_nlu.py            # NLU evaluation — F1/Precision/Recall
├── requirements.txt
├── .env.example
├── README.md
├── DOCS.md                # Full technical documentation (German)
└── .gitignore
```

---

## Submission Structure — Phase 2

| Part | Content | Where |
|---|---|---|
| A | Reflection text (150–200 words) | Directly in PebblePad |
| B | 10-slide PDF | Upload in PebblePad |
| C | GitHub link | https://github.com/kormuch/Vocadine_Restaurant_Finder |

### Slide Plan

| Slide | Content | Guideline |
|---|---|---|
| 1 | Title + Use Case (Haigerloch scenario) | Problem definition (10%) |
| 2 | Architecture diagram with data types on arrows | Design document |
| 3 | Differentiation vs. Alexa | Creativity (20%) |
| 4 | Implicit Slot Filling + code snippet | Implementation steps |
| 5 | STT + NLU method + phonetic aliases | Methodology (20%) |
| 6 | Google Places API + code snippet + JSON | Optional feature (Option 2) |
| 7 | TF-IDF formula + visualization | "Describe recommendation mechanism" |
| 8 | **F1 / Precision / Recall table** | **Mandatory per guidelines** |
| 9 | Error analysis (8 categories) | "Perform error analysis" |
| 10 | Before/After + Phase 3 outlook | Creativity + Methodology |

---

## Open Tasks

- [ ] Manual 20 test runs with microphone
- [ ] Merge PR: `feature/phase2-implicit-slot-filling` → `main`
- [ ] Create 10-slide PDF (slides 7 + 8 critical)
- [ ] Write reflection text (150–200 words) for PebblePad
- [ ] Submit in PebblePad

---

## Environment Variables

```
GOOGLE_PLACES_KEY=your_api_key_here
```
