# VocaDine — Presentation Concept v2 (10 Slides)
**Course:** DLMAIWNLPVA02 · NLP and Voice Assistants · IU International University
**Version:** v2 — addresses all Anne Schwerk feedback (27.04.2026)

---

## Changes vs. v1

| Anne's Point | v1 | v2 |
|---|---|---|
| Feature Engineering oberflächlich | Name + Types only, 40/60 unbegründet | Slide 6 vertieft: Reviews + Attributes, Gewichtung begründet, Generic-Types-Problem diskutiert |
| F1=1.000 naiv | 20 kuratierte Utterances, rule-based | Slide 7: 600 Utterances, spaCy NER, Macro-F1=0.881 auf 90 Utterance Holdout, ehrlich gerahmt |
| TF-IDF "Training"-Argument schwach | fit_transform = Training behauptet | Slide 6: Einschränkung ehrlich, spaCy NER als echter ML-Nachweis etabliert |
| Latenz-Diskrepanz 1.8s vs. 8s | Ungeklärt | Slide 7: lokale Latenz vs. End-to-End explizit getrennt |
| Privacy oberflächlich | "No persistent storage" | Slide 8: Audio + Standortdaten gehen an Google Cloud — klar benannt |
| edge-tts Wechsel unbegründet | Nicht erwähnt | Slide 2: pyttsx3-Probleme explizit genannt |
| Alexa als Strohmann | Volle Tabelle ohne Einschränkung | Slide 3: Alexa-Stärken eingeräumt, Vergleich auf Use Case begrenzt |
| "0 Typing Required" trivial | Als Key Figure gelistet | Ersetzt durch "600 annotated utterances" |
| Grice-Zitat dekorativ | Als Begründung für Top-3 | Slide 6: Designentscheidung direkt begründet, Grice gestrichen |

---

## Slide 1 — Title & Use Case
**Category:** Problem Definition (10%)

**Title:** VocaDine Germany
**Subtitle:** Voice Restaurant Assistant for English-Speaking Tourists

**Scenario:**
> Sarah, 28, arrives in Haigerloch, Germany. She speaks no German. She opens VocaDine and says: *"I'm looking for Italian food for two people near the city center"* — the assistant asks two follow-up questions, calls the Google Places API, and reads out the top 3 restaurants.

**Key figures (revised — no trivial claims):**
- 10 Conversation Slots (past bookings, dietary restrictions, cuisine, time/day, guests + 5 optional)
- 2058+ German Cities with phonetic STT correction
- 600 Annotated Training Utterances for NER model
- Macro-F1 = 0.881 on 90 held-out test utterances

**Relevance:**
Voice assistants are increasingly adopted as a primary interface for local discovery in tourism contexts (Ukpabi et al., 2019). VocaDine addresses a specific gap: English-speaking users navigating small German cities where generic assistants fail on local geography.

---

## Slide 2 — Architecture & Technology Decisions
**Category:** Design Document + Methodology (20%)

**Pipeline:**
```
Microphone
  → [audio: PCM 16kHz]
  → STT: Google Web Speech API (en-US)
  → [raw transcript]
  → NLU: spaCy NER (primary) + City Whitelist + Keyword Fallback
  → [slot dict]
  → DialogStateManager (10 slots, implicit filling, impatience detection)
  → [confirmed slots]
  → Validation Probe (Google Places API)
  → full_fetch (up to 50 venues — name, types, rating, reviews, attributes)
  → RecommendationEngine (TF-IDF cosine + rating)
  → [top 3 ranked]
  → TTS: edge-tts · en-US-JennyNeural
```

**Technology decisions (with reasoning):**

| Component | Choice | Why |
|---|---|---|
| STT | Google Web Speech API | Free tier, reliable en-US accuracy, minimal setup for prototype |
| NLU | spaCy NER + rule fallback | Trained model covers unseen phrasings; rule layer handles closed-domain edge cases |
| TTS | edge-tts (Microsoft Neural) | **pyttsx3 was discarded** — environment incompatibilities in Spyder/IPython made it unreliable across test setups. edge-tts delivers neural voice quality without requiring a paid API key |
| Ranking | TF-IDF + Google Rating | Deterministic, explainable, no extra API cost. Limitations acknowledged — see Slide 6 |
| API | Google Places API New | Live data, rich fields (reviews, editorialSummary, structured attributes), sufficient free quota for prototype |

---

## Slide 3 — VocaDine vs. Alexa: Scoped Comparison
**Category:** Creativity (20%)

> **Note:** Alexa is significantly stronger in ecosystem breadth, hardware integrations, and third-party skill coverage. This comparison is scoped to one specific use case: an English-speaking tourist finding a restaurant in a small German city.

| Feature | Alexa (general) | VocaDine (tourist use case) |
|---|---|---|
| German city STT | Fails on small/uncommon cities | Whitelist: 2058+ cities + phonetic aliases |
| 0-results handling | Typically surfaces empty/generic list | Validation probe rolls back slot, re-prompts |
| Dialog flexibility | Skill-dependent, often turn-by-turn | Implicit filling: up to 5 slots from one utterance |
| Ranking signal | Popularity / sponsored | TF-IDF preference match + Google Rating |
| Impatience detection | Not available in standard flow | VADER sentiment + keyword patterns |
| Ambiguity resolution | First-match or error | `_detect_ambiguity()` triggers clarification |

**What Alexa does better (honest):** Smart home integration, music, shopping, calendar, massive third-party skill ecosystem, hardware (Echo devices), multilingual out of the box. VocaDine is purpose-built for one narrow problem Alexa does not solve well.

---

## Slide 4 — Implicit Slot Filling & Dialog Management
**Category:** Implementation Steps

**The core dialog problem:** Asking 10 questions sequentially feels like a form, not a conversation. VocaDine resolves up to 5 slots from a single utterance and skips questions already answered.

**Example:**
> *"I want Italian food in Berlin for two people tonight, nothing too fancy"*
> → `location=Berlin` · `cuisine=Italian` · `group_size=2` · `datetime=tonight` · `budget=moderate`
> → TTS: *"Got it — Berlin, Italian cuisine, 2 people, tonight, moderate budget."*
> → Next question: *"Any dietary restrictions?"* (only unfilled critical slot remaining)

**Extraction cascade (per utterance):**
1. `extract_all_spacy(text)` — trained NER model, returns all 5 entity types in one pass
2. City whitelist fallback — word-boundary regex for location if NER missed it
3. Keyword maps — budget, occasion, datetime, distance (rule-based, reliable for closed lists)

**Special dialog mechanisms:**
- **Validation probe:** After each high-impact slot (location, cuisine, diet) → quick Places API call. 0 results → slot rolled back, user re-prompted
- **Impatience detection:** VADER compound < -0.5 OR keyword patterns ("stop asking", "just find") → all remaining slots set to "any", immediate search
- **Ambiguity detection:** ≥2 cuisines in one utterance → clarification question
- **Diet inference:** meat keyword in `past_experience` without negation → diet="none" inferred, question skipped

---

## Slide 5 — NLU: spaCy NER Training
**Category:** Collect Training Data + Train NLP Models (mandatory)

**Why a trained model?**
Rule-based keyword matching achieves perfect scores on utterances it was designed for — but fails silently on unseen phrasings ("I fancy sushi", "plant-based options", "we're counting pennies"). A trained NER model generalises across the full vocabulary of the slot type.

**Dataset:**
- 600 manually annotated utterances in `data/training_data.py`
- 5 entity labels: LOCATION · CUISINE · DIET · BUDGET · GROUP_SIZE
- Deterministic split via `random.seed(42)`: 420 train / 90 val / 90 test

| Section | Count | Examples |
|---|---|---|
| Single-label | 290 | "I'm in Munich", "something vegan" |
| Multi-label combos | 270 | "cheap Thai in Hamburg for four" |
| Adversarial / edge | 42 | Negations, corrections, colloquial phrasings |

**Training setup (`train_nlu.py`):**
- Model: `spacy.blank("en")` — no pre-trained vectors, NER only
- 40 epochs, dropout=0.35, compounding batch size 4→32
- Best checkpoint saved at epoch 23 (val Macro-F1 = 0.9685)

**Annotation guidelines:** `data/annotation_guidelines.md` — span boundaries, edge cases per label, inter-annotator agreement target (κ ≥ 0.85), ASR noise handling

---

## Slide 6 — TF-IDF Recommendation Engine
**Category:** Recommendation Mechanism — scikit-learn

**Scoring formula:**
```
score = (cosine_similarity × 0.4) + (google_rating / 5.0 × 0.6)
      + budget_bonus (+0.1 if priceRange matches budget slot)
      + attribute_bonus (+0.1 per matched structured attribute: outdoor, groups)
```

**Feature engineering — restaurant side:**
`name + types + editorialSummary + top-3 review texts + attribute tokens`

Reviews and editorial summaries are fetched live from Places API and included in the TF-IDF corpus. This gives the vectoriser domain-rich text — not just short type tags. Structured attributes (outdoorSeating, goodForGroups) are injected as text tokens so TF-IDF can match them against user preferences.

**Feature engineering — user side:**
`cuisine + diet + occasion + past_experience free text`

**Known limitations (honest):**
- When the Places API returns only generic types (e.g., `["restaurant", "food", "point_of_interest"]`), TF-IDF reduces to near-random ranking — reviews and editorial summary become the primary signal in that case
- TF-IDF cannot capture semantic similarity: "sushi" and "Japanese" are unrelated tokens unless both appear in the same document
- The 40/60 weighting (cosine vs. rating) is a **design choice, not empirical optimisation**: it prioritises Google's crowd-sourced quality signal over keyword overlap, on the assumption that rating correlates more reliably with overall experience than a sparse TF-IDF match on short descriptions

**On the "training" claim:**
`fit_transform()` called at runtime on live restaurant data constitutes lightweight on-demand vectoriser fitting — the IDF weights are computed from the actual result set for this query. This is not equivalent to offline model training with a large corpus. The genuine ML training component is the **spaCy NER model** (Slide 5).

---

## Slide 7 — Evaluation
**Category:** Mandatory: Precision / Recall / F1

### NER Evaluation (spaCy model — 90 held-out utterances)

| Label | Precision | Recall | F1 |
|---|---|---|---|
| LOCATION | 0.963 | 1.000 | 0.981 |
| DIET | 0.944 | 1.000 | 0.971 |
| CUISINE | 0.878 | 0.977 | 0.925 |
| BUDGET | 0.783 | 0.857 | 0.818 |
| GROUP_SIZE | 0.640 | 0.800 | 0.711 |
| **Macro** | **0.842** | **0.927** | **0.881** |

**Honest framing:**
- Test set: 90 utterances, held out before training, never used for model selection
- Model trained on 600 utterances — small dataset, no pre-trained vectors
- GROUP_SIZE (F1=0.711): implicit group expressions ("me and my wife") are not annotatable as NER spans — rule-based layer covers these cases. This is a known architectural boundary, not a model failure.
- BUDGET (F1=0.818): multi-word spans ("not too expensive") remain challenging for span detection

### System Metrics (end-to-end)

| Metric | Value | Scope |
|---|---|---|
| Task Completion Rate | 18 / 20 = **90%** | Full conversation to top-3 output |
| Local processing latency | **~1.8s** | STT result → NLU → ranking → TTS start |
| End-to-end latency (incl. API) | **~6–9s** | Microphone open → user hears first result |
| WER on short words | ~20% | "no", "two" — known STT limit |

**Latency note:** The "8 seconds" scenario in Slide 1 refers to end-to-end time including two Google Places API roundtrips (validation probe + full fetch). The 1.8s figure is local processing only. Both are real measurements — they measure different things.

---

## Slide 8 — STT & Privacy
**Category:** Methodology + honest data handling

### STT — SpeechRecognition / Google Web Speech API

**Phonetic alias system (core differentiator):**

| Spoken | STT output | Alias fix |
|---|---|---|
| "Tübingen" | "tubing in" | tubing in → Tübingen |
| "Haigerloch" | "Hi girl" | hi girl → Haigerloch |
| "Horb am Neckar" | "hope America" | hope america → Horb am Neckar |
| "Döner" | "doona" | doona → Döner |
| "Bayreuth" | "Beirut" | beirut → Bayreuth |

Word-boundary regex (`\b...\b`) prevents substring false positives ("burg" inside "hamburg").

### Privacy — honest assessment

| Data | Where it goes | Mitigation |
|---|---|---|
| **Audio** | Google Cloud (Web Speech API) | Microphone only active during `recognizer.listen()` — no always-on. Google processes and discards per their API terms. |
| **Location + preferences** | Google Cloud (Places API) | City name + cuisine/diet slot sent as query string. No persistent user profile stored server-side by VocaDine. |
| **Session data** | Local memory only | Slots not written to disk. Session ends when script exits. |
| **API key** | `.env` file, not in repo | `.gitignore` excludes `.env` |

**Critical note:** "No always-on microphone" and "no persistent storage" are the minimum bar for any prototype — not differentiating privacy features. For a production deployment handling location and dietary data of tourists, GDPR Article 13 disclosure would be required before first use.

---

## Slide 9 — Error Analysis
**Category:** Error Analysis (Methodology)

| # | Category | Example | Root Cause | Status |
|---|---|---|---|---|
| 1 | STT phonetic | "Tübingen" → "tubing in" | en-US unfamiliar with small city | ✅ Phonetic alias |
| 2 | STT phonetic | "Horb am Neckar" → "hope America" | Compound German toponym | ✅ Alias added |
| 3 | STT phonetic | "Döner" → "doona" | German food term unknown to en-US | ✅ Cuisine alias |
| 4 | Substring FP | "germany" → cuisine=German | Missing word boundary | ✅ `\b`-regex |
| 5 | Substring FP | "hamburg" matched city "Burg" | Dict ordering, no boundary | ✅ Word-boundary fix |
| 6 | Negation missed | "no restrictions" → diet=None | Only positive keywords | ✅ Negation pattern |
| 7 | Impatience ignored | "stop asking" → continued | No sentiment | ✅ VADER + ImpatienceDetector |
| 8 | Ambiguity silent | "Italian or Greek?" → Italian | First-match-wins | ✅ `_detect_ambiguity()` |
| 9 | Group size wrong | "me and my family" → 2 | Pattern too generic | ✅ family=4, partner=2 |
| 10 | Budget keyword missing | "average price" → unrecognised | Gap in keyword map | ✅ Keywords extended |
| 11 | Venue type wrong | Shisha bar in results | No type filtering | ❌ Phase 3 |
| 12 | Geographic imprecision | Berlin-Zehlendorf → Moabit | City only, no radius | ❌ Phase 3 |
| 13 | Diet inference: negation | "they served meat and I don't like meat" | Clause-separated negation beyond shallow parser | ⚠️ Known limit — fallback: diet question asked |

**Honest framing:** The rule-based NLU achieves near-perfect scores on utterances it was designed for. The errors surfaced here came from live test runs and edge cases — not from a systematic adversarial evaluation. Errors 11–13 remain open by design.

---

## Slide 10 — Before/After & Outlook
**Category:** Creativity + Summary

### Before / After

| Dimension | Phase 1 | Phase 2 |
|---|---|---|
| NLU | Rule-based keyword only | spaCy NER (Macro-F1=0.881) + rule fallback |
| Training data | None | 600 annotated utterances, 420/90/90 split |
| Slot filling | Sequential, 1 slot/utterance | Implicit, up to 5 slots/utterance |
| Ambiguity | Silent first-match | Clarification follow-up |
| Impatience | Ignored | VADER sentiment detection |
| STT errors documented | ~5 known | 13 documented, 10 fixed |
| TTS | pyttsx3 (discarded: env issues) | edge-tts · Microsoft Neural |
| Task Completion | Not measured | 90% (18/20) |
| NER Evaluation | Not available | Macro-F1=0.881 on 90 held-out utterances |

### Phase 3 Roadmap

- **Type filtering** — exclude non-restaurant results (shisha bars, clubs) from Places API results
- **Radius search** — geographic restriction (configurable km radius around city centre)
- **Multilingual** — German, French, Spanish speaker profiles
- **Offline fallback** — local model when no internet available

### What remains limited (honest)

- TF-IDF on short type strings is not deep semantic understanding — works well when reviews/summaries are available, degrades on sparse data
- GROUP_SIZE and BUDGET NER still benefit from rule-layer augmentation
- End-to-end latency (~7s) acceptable for prototype, not production-ready
- Privacy disclosure would need formal GDPR basis for real deployment

---

## References

**[1]** Hutto, C. J., & Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. *Proceedings of ICWSM*. AAAI Press.
→ *Slide 4, 9: VADER ImpatienceDetector*

**[2]** Nahar, L., Sultana, Z., Iqbal, N., & Chowdhury, A. (2019). Sentiment analysis and emotion extraction. *ICASERT 2019*. IEEE.
→ *Slide 4: context for sentiment in dialog systems*

**[3]** Rafailidis, D., & Manolopoulos, Y. (2019). Can virtual assistants produce recommendations? *WIMS 2019*.
→ *Slide 6: TF-IDF ranking vs. popularity-only*

**[4]** Ukpabi, D. C., Aslam, B., & Karjaluoto, H. (2019). Chatbot adoption in tourism services. In *Robots, Artificial Intelligence, and Service Automation in Travel, Tourism and Hospitality*. Emerald.
→ *Slide 1: voice assistants in tourism context*

**[5]** Abdullah, T., & Ahmet, A. (2022). Deep learning in sentiment analysis: Recent architectures. *ACM Computing Surveys, 55*(8).
→ *Slide 4: justification for VADER in real-time context over heavy DL models*

> Grice [1975] removed — the Top-3 design decision is self-evident and does not require a philosophical citation.
