# VocaDine — Restaurant Voice Assistant for Tourists in Germany

## Project Context

**Course:** DLMAIWNLPVA02 — NLP and Voice Assistants, IU Internationale Hochschule
**Student ID:** IU14127772
**Status:** Phase 2 submitted (Apr 2026), feedback received, Phase 3 open
**Local path:** `C:/Users/kormu/projekte/Artificial Intelligence/IU modules/NLP and Voice 2/`
**GitHub:** https://github.com/kormuch/Vocadine_Restaurant_Finder
**Assessor:** Anne Schwerk

**Next step:** Write 2-page "Making Of" PDF (Arial 11pt, 1.5-spaced) — the main deliverable for Phase 3.

---


**Course:** DLMAIWNLPVA02 — NLP and Voice Assistants (IU)
**Phase:** 2 complete · Phase 3 pending
**Stack:** Python 3.12 · SpeechRecognition · edge-tts · spaCy · scikit-learn · VADER · Google Places API
**Repo:** https://github.com/kormuch/Vocadine_Restaurant_Finder

---

## Use Case

Sarah, 28, arrives in Haigerloch, Germany. She speaks no German. She opens VocaDine, says: *"I'm looking for Italian food for two people near the city center"* — and 8 seconds later hears the top 3 restaurants read aloud.

**Core problem:** Google STT (en-US) fails on small German city names. "Haigerloch" becomes "Hi girl" → 0 results. VocaDine solves this via a 2058+ city whitelist with phonetic aliases.

---

## Key Differentiators vs. Alexa

| Feature | Alexa | VocaDine |
|---|---|---|
| German city STT | Fails on small cities | Whitelist 2058+ cities + phonetic aliases |
| 0-results handling | Shows empty list | Validation probe rolls back the slot |
| Dialog flexibility | Rigid turn-by-turn | Implicit slot filling (up to 5 slots/utterance) |
| Ranking | Popularity only | TF-IDF + Google rating (40/60) |
| Impatience detection | Not available | VADER sentiment + keyword patterns |
| Ambiguity handling | Not available | Detects "Italian or Greek?" → clarifies |
| API dependency | Alexa Skills Kit required | Direct Google Places API |

> Note: Alexa is stronger in ecosystem, hardware, and multilingual support. This comparison is scoped to the specific use case: English tourist, small German city.

---

## Architecture

```
Microphone
  → [audio: PCM 16kHz]
  → STT (Google Web Speech API, en-US, pause_threshold=1.8s)
  → [text: raw transcript]
  → City Whitelist correction (2058+ phonetic aliases)
  → NLU (_extract_multiple_slots)
       → spaCy NER (trained, 5 labels) — first pass
       → Rule-based fallback (regex/keyword maps) — remaining slots
       → VADER sentiment (ImpatienceDetector)
  → [slots: dict]
  → DialogStateManager (10 slots, implicit filling, validation probe)
  → [confirmed slot → full_fetch trigger]
  → Google Places API (New) — full_fetch
  → [JSON: up to 50 venues]
  → RecommendationEngine (TF-IDF cosine + rating + bonuses)
  → [top 3: ranked list]
  → TTS (edge-tts, en-US-JennyNeural)
```

### Class Overview

| Class | File | Role |
|---|---|---|
| `TTSEngine` | main.py | Text → Speech (edge-tts, Microsoft Neural Voice) |
| `STTEngine` | main.py | Microphone → Text (Google Web Speech) |
| `ImpatienceDetector` | main.py | VADER sentiment + keyword patterns |
| `GooglePlacesClient` | main.py | API queries (probe + full_fetch) |
| `NLU` | main.py | Slot extraction (spaCy NER + rule fallback) |
| `RecommendationEngine` | main.py | TF-IDF ranking, Top 3 |
| `DialogStateManager` | main.py | Interview flow, slot management |
| `GERMAN_CITIES` | german_cities.py | 2058+ cities + phonetic aliases |

---

## 10 Conversation Slots

The dialog manager handles 10 distinct information slots, each elicited in a separate turn if not volunteered — meeting the assignment's scale requirement of "10 questions and 10 answers."

| Slot | Question | Example |
|---|---|---|
| `location` | Which German city are you visiting? | "I'm in Berlin" |
| `past_experience` | A restaurant you enjoyed — what did you like? | "Italian place, great pasta" |
| `datetime` | When would you like to eat? | "Today at seven PM" |
| `cuisine` | What kind of food are you looking for? | "Italian" |
| `diet` | Any dietary restrictions? | "I'm vegan" / "none" |
| `budget` | Cheap, moderate, or fine dining? | "moderate" |
| `group_size` | For how many people? | "four" |
| `occasion` | Casual, date, or business? | "a date" |
| `distance` | Walking distance or anywhere? | "walking distance" |
| `special_features` | Outdoor seating, English menus? | "outdoor seating" |

Slots filled implicitly by earlier answers are skipped automatically.

---

## Features

### 1. German City Whitelist (2058+ cities)
Prevents STT failures on German city names via phonetic aliases:

| Spoken | STT Output | Fix |
|---|---|---|
| "Tübingen" | "tubing in" | tubing in → Tübingen |
| "Haigerloch" | "Hi girl" | hi girl → Haigerloch |
| "Horb am Neckar" | "hope America" | hope america → Horb am Neckar |
| "Döner" | "doona" | doona → Döner |
| "Bayreuth" | "Beirut" | beirut → Bayreuth |

Word-boundary regex (`\b...\b`) prevents substring false positives (e.g. "burg" matching inside "hamburg").

### 2. Implicit Slot Filling
A single utterance can fill up to 5 slots simultaneously:

> "I want Italian food in Berlin for two people tonight, nothing too fancy"
> → `location=Berlin`, `cuisine=Italian`, `group_size=2`, `occasion=casual`, `budget=moderate`

### 3. Validation Probe
Before accepting a high-impact slot (location, cuisine, diet), the system probes the Google Places API. 0 results → slot is rolled back and the user is re-asked.

### 4. TF-IDF Recommendation Engine

```
score = (cosine_similarity × 0.4) + (google_rating / 5.0 × 0.6)
      + budget_bonus (0.1 if priceRange.endPrice matches budget slot)
      + attribute_bonus (0.1 per matched structured attribute)
```

**Why 40/60 split?** On short type-only descriptions, TF-IDF cosine produces low-confidence scores. Google's aggregate rating averages hundreds of reviews — more stable signal. When reviews and editorialSummary are available, cosine becomes stronger. A 50/50 split was considered but rejected: a higher rating weight ensures useful results even when TF-IDF signal degrades.

**Budget mapping from `priceRange.endPrice` (€):**
- cheap → ≤ €15
- moderate → €16–35
- fine dining → > €35

`price_level` (legacy integer 1–4) was not used — deprecated in Places API (New), unreliably populated.

**Why Top 3?** Grice's Maxim of Quantity: be as informative as required, not more. Reading 50 restaurants aloud = analysis paralysis.

### 5. spaCy NER (trained, Phase 2)

Replaces the Phase 1 rule-only NLU. Trained on 600 manually annotated utterances, evaluated on a fully held-out test set.

- **Labels:** LOCATION, CUISINE, DIET, BUDGET, GROUP_SIZE
- **Split:** 420 train / 90 val / 90 test
- **Training:** 40 epochs, dropout=0.35, compounding batch 4→32
- **Best checkpoint:** epoch 23

| Label | F1 | P | R |
|---|---|---|---|
| LOCATION | 0.981 | 0.963 | 1.000 |
| DIET | 0.971 | 0.944 | 1.000 |
| CUISINE | 0.925 | 0.878 | 0.977 |
| BUDGET | 0.818 | 0.783 | 0.857 |
| GROUP_SIZE | 0.711 | 0.640 | 0.800 |
| **MACRO** | **0.881** | 0.842 | 0.927 |

> Val-F1 (≈ 0.97 at best epoch) is the checkpoint-selection signal — the model is saved when this peaks, making it optimistic by design. Test-F1 = 0.881 is on a fully held-out set the model never influenced. The gap is expected and methodologically sound.

### 6. Impatience Detection
VADER sentiment (compound < −0.5) + keyword patterns ("stop asking", "just find something") → all remaining slots set to `"any"`, system searches immediately.

### 7. Ambiguity Handling
`_detect_ambiguity()` checks if ≥2 cuisines appear in one utterance → clarification question asked.

### 8. Privacy / Data Flows

| Data | Destination | Notes |
|---|---|---|
| Audio | Google Cloud (Web Speech API) | Processed for STT, not stored for advertising (Google terms) |
| Location + preferences | Google Places API | Sent as textQuery string, e.g. "Italian vegan Berlin" |
| API key | .env file | Not in repository (.gitignore) |

- Microphone active only during `recognizer.listen()` — no always-on monitoring
- No persistent user profile stored server-side
- For production: GDPR Article 13 transparency obligations would apply before first use

---

## Performance Metrics

| Metric | Value | Scope |
|---|---|---|
| NER Macro-F1 | **0.881** | 90 held-out test utterances, spaCy NER |
| Task Completion | **90%** (18/20) | Full conversation → top-3 recommendation |
| Local latency | **~1.8s** | STT result → ranking → TTS start |
| End-to-end latency | **~6–9s** | Mic open → user hears result (incl. 2× Places API) |
| WER short words | ~20% | "no", "two" — known STT limitation, mitigated by word-boundary regex |

---

## Error Analysis

| # | Category | Example | Root Cause | Status |
|---|---|---|---|---|
| 1 | STT phonetic | "Tübingen" → "tubing in" | en-US doesn't know small city | ✅ Phonetic alias |
| 2 | STT phonetic | "Horb am Neckar" → "hope America" | Compound German toponym | ✅ Alias added |
| 3 | STT phonetic | "Döner" → "doona" | en-US doesn't know German food term | ✅ Cuisine alias |
| 4 | Substring FP | "germany" → cuisine=German | No word boundary | ✅ `\b`-regex |
| 5 | Substring FP | "hamburg" → location=Burg | Dict order issue | ✅ Word-boundary fix |
| 6 | Substring FP | "none" → group_size=1 | "one" inside "none" | ✅ Word-boundary fix |
| 7 | Negation | "no restrictions" → diet=None | Only positive keywords | ✅ Negation pattern |
| 8 | Indifference | "I don't care" → all slots forced | Trigger too broad | ✅ Slot-specific fallback |
| 9 | Ambiguity | "Italian or Greek?" → Italian | No ambiguity check | ✅ `_detect_ambiguity()` |
| 10 | Impatience | "stop asking" → system continued | No sentiment analysis | ✅ VADER + ImpatienceDetector |
| 11 | Group size | "me and my family" → 2 | Pattern mismatch | ✅ family=4, partner=2 |
| 12 | Unknown city | Unknown city → silent "any" | No retry logic | ✅ One retry with spelling prompt |
| 13 | Budget keywords | "average price" not matched | Not in budget_map | ✅ Keywords added |
| 14 | Occasion keywords | "grab a bite" not matched | Not in occasion_map | ✅ Keywords added |
| 15 | TTS fallback | "searching in any" | No display fallback | ✅ Fallback: "Germany" |
| 16 | Venue type | Shisha bar in results | No type filtering | ❌ **Phase 3** |
| 17 | Geographic precision | User in Berlin-Kreuzberg gets Charlottenburg results (6km away). NLU extracts "Berlin" but not the district; Places API query uses city name only, no radius or district filter | City name only; NLU has no sub-location slot; no `locationBias` radius in API call | ❌ **Phase 3**: extract district as sub-location slot + apply 3km radius via `locationBias` parameter |
| 18 | Diet inference (positive) | "loved the meatballs" → diet=none inferred | Correct inference | ✅ `_infer_diet_from_past_experience()` |
| 19 | Diet inference (negation) | "they served meat and I don't like meat" | Clause-separated negation | ⚠️ Known limit — diet question asked as fallback |
| 20 | STT short words | "No" → "Know", "Two" → "To" | en-US phonetic ambiguity | ✅ Word-boundary regex + synonym map |
| 21 | Dialog question framing | "Where are you now?" → user plans for next week | Wrong question intent | ✅ Changed to "In which city would you like to eat?" |
| 22 | German food terms | "Schnitzel" → "snit cell" | STT doesn't know German dish | ❌ **Phase 3** — extend alias map |
| 23 | Mumbled speech | System filled "any" without asking | No low-confidence detection | ❌ **Phase 3** — confidence threshold |

**2 open test failures:**
- User said "Schnitzel" (German) → STT returned "snit cell" → unmatched
- User mumbled → system filled slot with "any" without re-asking

---

## Technology Decisions

### Why edge-tts instead of pyttsx3?
pyttsx3 produced consistent COM object / audio driver errors in Spyder and IPython contexts on Windows. Not reliably reproducible but frequent enough to block testing. edge-tts uses Microsoft Azure Neural voices via lightweight async Python — no API key, no environment issues observed. Disadvantage: requires internet (acceptable for tourist-facing app).

### Why TF-IDF instead of LLM?
No API key, fully deterministic, explainable. `fit_transform()` at runtime on live restaurant data = on-demand vectorization. Limitation honestly stated: on very short type strings ("restaurant, food"), cosine similarity produces low-confidence scores — mitigated by the 40/60 rating weight and by using reviews + editorialSummary when available.

### Why spaCy blank model instead of pre-trained?
Domain is narrow (5 entity types, closed vocabulary). Pre-trained vectors add setup overhead and GPU dependency without significant benefit for this closed domain. Blank model trained from scratch demonstrates the training pipeline clearly for course purposes.

### Why Google Web Speech API for STT?
Free tier sufficient for prototype, reliable en-US accuracy, minimal setup. pause_threshold reduced 2.5s → 1.8s to reduce perceived latency. Known limitation: small German city names fail consistently — mitigated by phonetic alias system.

---

## Project Structure

```
NLP and Voice 2/
├── main.py                       — Core application (dialog, STT, TTS, API, NLU, ranking)
├── train_nlu.py                  — spaCy NER training (40 epochs, 420/90/90 split)
├── eval_nlu.py                   — NLU evaluation on held-out test set
├── german_cities.py              — City whitelist + phonetic aliases (2058+ cities)
├── german_cities_list.py         — Raw list of all German cities
├── api_key_test.py               — Google Places API connectivity test
├── training_log.json             — Per-epoch val-F1 and loss (40 epochs)
├── test_results.json             — Final test-set F1/P/R per label (held-out 90)
├── requirements.txt
├── .env                          — API key (not in repo)
├── .env.example
├── data/
│   ├── training_data.py          — 600 annotated utterances, split_data(seed=42)
│   └── annotation_guidelines.md — Labeling rules, span boundaries, edge cases
├── models/
│   └── vocadine_nlu/             — Trained spaCy NER model (best checkpoint epoch 23)
├── abgabe phase 2/
│   ├── presentation/
│   │   ├── vocadine_p2.html      — 10-slide Blueprint presentation
│   │   └── architecture_diagram.html — Standalone system architecture diagram
│   ├── code/                     — Submission copies of main.py, train_nlu.py, eval_nlu.py
│   └── docs/                     — phase2_submission_matrix.md, training_log.json, test_results.json
└── guidlines pdfs/
    ├── Assignments Portfolio_DLMAIWNLPVA02 (1).txt
    ├── Guidelines Portfolio_new.txt
    ├── feedback1.txt             — Tutor feedback Phase 1
    └── feedback2_anne_schwerk.txt — Tutor feedback Phase 2
```

---

## Installation

```bash
git clone https://github.com/kormuch/Vocadine_Restaurant_Finder.git
cd Vocadine_Restaurant_Finder
pip install -r requirements.txt
cp .env.example .env
# Add your Google Places API key to .env:
# GOOGLE_PLACES_KEY=AIzaSy...
```

**Windows — pyaudio:**
```bash
pip install pyaudio
# If that fails:
pip install pipwin && pipwin install pyaudio
```

**Run:**
```bash
python main.py
```

**Train NER model:**
```bash
python train_nlu.py
# Output: models/vocadine_nlu/, training_log.json, test_results.json
```

**NLU Evaluation (no microphone needed):**
```bash
python eval_nlu.py
```

> Run from a standard terminal (not Spyder/IPython) to ensure audio output works correctly.

---

## Environment Variables

```
GOOGLE_PLACES_KEY=your_api_key_here
```

---

## Phase 2 — Submission Status

| Part | Content | Status |
|---|---|---|
| A | Reflection text (150–200 words) | ✅ reflection_text_p2.txt |
| B | 10-slide PDF | ⚠️ Export from vocadine_p2.html → Ctrl+P → PDF |
| C | GitHub link | ✅ https://github.com/kormuch/Vocadine_Restaurant_Finder |

Filename: `Much-Korbinian_[MatrNr]_Voice Assistants_P2_S.pdf`

### Phase 2 — Completed ✅

- [x] spaCy NER trained on 600 utterances, Macro-F1 = 0.881 on held-out test set
- [x] `train_nlu.py` — 40 epochs, best checkpoint saved, training_log.json written
- [x] `eval_nlu.py` — evaluation on 90 test utterances, test_results.json written
- [x] `data/annotation_guidelines.md` — full labeling rules for Phase 3 checklist
- [x] `_extract_multiple_slots` updated — spaCy first pass, rule fallback for remaining slots
- [x] 10-slide Blueprint presentation (vocadine_p2.html)
  - [x] Slide 1: KPIs + Alexa comparison (scoped, honest)
  - [x] Slide 2: Pipeline SVG + tech decisions + NLU cascade code
  - [x] Slide 3: Full 5-layer architecture SVG (INPUT/NLU/DIALOG/API+RANK/OUTPUT)
  - [x] Slide 4: Dialog management (implicit filling, validation, impatience, ambiguity)
  - [x] Slide 5: NLU training (dataset, training setup, code)
  - [x] Slide 6: Recommendation engine (formula, priceRange, honest limitations)
  - [x] Slide 7: Evaluation (F1 bars, system metrics, val-F1 vs test-F1 note)
  - [x] Slide 8: STT & Privacy (phonetic alias table, data flow table, GDPR note)
  - [x] Slide 9: Error analysis (13 fixed, 3 open)
  - [x] Slide 10: Before/After + Phase 3 roadmap
  - [x] Hyperlinks: SpeechRecognition, spaCy, edge-tts, scikit-learn, Google Places API
- [x] `architecture_diagram.html` — standalone A3-printable architecture diagram
- [x] `technical_design_notes.txt` — supplementary justifications for examiner
- [x] `reflection_text_p2.txt` — 173-word plain text for PebblePad Part A
- [x] `phase2_submission_matrix.md` — requirements vs. results matrix
- [x] All Anne Schwerk Phase 2 feedback addressed (see matrix)
- [x] Val-F1 vs. test-F1 gap explained on Slide 7
- [x] "10 questions and 10 answers" explicitly addressed in README + Slide 4

### Phase 2 — Still Open ⚠️

- [ ] Export vocadine_p2.html as PDF (Chrome → Ctrl+P → Background graphics ON)
- [ ] Submit in PebblePad: Part A (paste reflection_text_p2.txt), Part B (PDF), Part C (GitHub)

---

## Phase 3

→ Issue matrix, Anne's feedback analysis, code audit, and full Phase 3 checklist:
**`abgabe phase 3/todo.md`**

---

## Anne Schwerk — Phase 2 Feedback Summary

Date: May 2026

Cross-referenced against the actual submitted PDF.

| # | Anne's Issue | Present in PDF? | Open for Phase 3 |
|---|---|---|---|
| 1 | 40/60 weighting unjustified — empirical or arbitrary? | Partial: "design decision: rating correlates more reliably" | ✅ Yes — needs direct answer: "not empirically calibrated, because..." |
| 2 | pyttsx3 switch never explained | Yes, Slide 2 table: "Spyder/IPython env incompatibilities" | ⚠️ Present but too brief — expand in Making Of |
| 3 | TF-IDF "training" claim intellectually weak | Yes, Slide 6: "lightweight on-demand vectoriser fitting — not equivalent to offline model training" | ⚠️ Qualification present, but Slide 5 header still reads "TRAIN NLP MODELS" |
| 4 | F1=1.000 still as headline | Not in PDF — Slides 1 and 7 show 0.881 as headline | ✅ Already fixed — Anne likely referenced a draft version |
| 5 | Latency discrepancy (1.8s vs. 8s) | Yes, Slide 7: local 1.8s and E2E 6–9s explicitly noted. Slide 1 says ~7s (not 8s) | ✅ Already fixed |
| 6 | Privacy discussion superficial | Yes, Slide 8: "minimum bar for a prototype — not differentiating privacy features. GDPR Art. 13..." | ✅ Already fixed |
| 7 | Literature decorative | Grice citation not visible in PDF — possibly removed | ⚠️ Making Of: anchor every citation to a concrete design decision |

### What still needs to be addressed in Phase 3

**Issue 1 — Answer the 40/60 question directly:**
> Current: "design decision: rating correlates more reliably"
> Required: explicit statement whether the split is empirically motivated or not.
> Making Of wording: "The 40/60 weighting is not empirically calibrated. It is a design judgment: Google's aggregate rating (thousands of reviews) provides a more stable quality signal than cosine similarity on short type strings. A 50/50 split was considered and rejected because TF-IDF confidence degrades on sparse features."

**Issue 2 — Expand pyttsx3 decision in Making Of:**
> Slide 2 covers it in one line. Making Of: one paragraph on the switch — what broke (COM Exception in Spyder/IPython), what edge-tts provides (Azure Neural voice, no API key, no environment issues), what was given up (internet dependency).

**Issue 3 — Clarify "Train NLP Models" framing:**
> The real trained model is spaCy NER (600 utterances, 40 epochs, Macro-F1 = 0.881). TF-IDF fit_transform() at runtime is on-demand vectorization, not model training. Both statements are in the PDF but the Slide 5 header "TRAIN NLP MODELS" (a course requirement label) may cause confusion. Making Of must separate the two explicitly.

**Additional slide notes from Anne:**
- Slide 1: Remove "0 Typing Required" — trivial for any voice assistant
- Slide 3: Frame Alexa comparison more explicitly as scoped (already in PDF, reinforce)
- Slide 10 Phase 3 roadmap: correct priorities — Type Filtering and Radius Search

---

## Literature

→ Full citations, design decision mappings, and Making Of reference guide:
**`abgabe phase 3/literature.md`**
