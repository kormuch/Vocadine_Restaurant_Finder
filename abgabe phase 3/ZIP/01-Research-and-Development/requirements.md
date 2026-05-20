# Functional & Non-Functional Requirements — VocaDine
**Much, Korbinian | IU14127772 | DLMAIWNLPVA02**

---

**Notation:** FR = Functional Requirement (what the system must do). NFR = Non-Functional Requirement (how the system must do it — quality constraints such as performance, privacy, and maintainability). Each requirement is identified by a unique ID for traceability.

---

## Functional Requirements

| ID | Requirement | Implementation |
|---|---|---|
| FR-01 | The system shall accept voice input from the user via microphone | `STTEngine.listen()` — Google Web Speech API, en-US |
| FR-02 | The system shall extract restaurant preferences from natural language utterances | `NLU._extract_multiple_slots()` — spaCy NER + rule-based fallback |
| FR-03 | The system shall collect a minimum of 10 preference slots across the conversation | `DialogStateManager.run_interview()` — location, cuisine, diet, budget, group_size, occasion, datetime, distance, past_experience, special_features |
| FR-04 | The system shall fill multiple slots from a single utterance where possible | Implicit slot filling — up to 5 slots per utterance |
| FR-05 | The system shall ask only for slots not already filled | Dialog skips questions for slots extracted earlier in the conversation |
| FR-06 | The system shall validate high-impact slots before accepting them | `GooglePlacesClient.probe()` — 0 results triggers slot rollback and re-prompt |
| FR-07 | The system shall detect user frustration and skip remaining questions | `ImpatienceDetector` — VADER compound < −0.5 or explicit stop keywords |
| FR-08 | The system shall resolve ambiguous cuisine input | `_detect_ambiguity()` — ≥2 cuisines triggers clarification question |
| FR-09 | The system shall infer dietary preference from past experience | `_infer_diet_from_past_experience()` — meat keyword without negation → diet=none |
| FR-10 | The system shall query live restaurant data from an external API | `GooglePlacesClient.full_fetch()` — Google Places API (New), textQuery |
| FR-11 | The system shall filter results to food venues only | `_is_food_venue()` — allowlist of food-specific Place types |
| FR-12 | The system shall apply geographic bias to results | `_geocode_city()` + `locationBias` 3km radius — Google Geocoding API |
| FR-13 | The system shall rank results by relevance and quality | `RecommendationEngine.rank()` — TF-IDF cosine (0.4) + aggregate rating (0.6) + bonuses |
| FR-14 | The system shall output the top 3 recommendations as spoken audio | `TTSEngine.speak()` — edge-tts, en-US-JennyNeural |
| FR-15 | The system shall handle German city names spoken with an English accent | `GERMAN_CITIES` whitelist — 2058+ cities with phonetic aliases, word-boundary regex |
| FR-16 | The system shall handle zero-result scenarios gracefully | Validation probe → slot rollback; end-of-pipeline empty result → spoken "no results" message |

---

## Non-Functional Requirements

| ID | Requirement | Implementation / Measurement |
|---|---|---|
| NFR-01 | **Performance** — Local processing latency (STT result → TTS start) shall be under 3 seconds | Measured ~1.8s local; end-to-end including API calls ~6–9s |
| NFR-02 | **Usability** — The system shall require no typing at any point | Voice-only input throughout; no keyboard interaction required |
| NFR-03 | **Usability** — The system shall minimise conversation turns | Implicit slot filling reduces 10-slot interview to 2–3 turns when user provides rich initial input |
| NFR-04 | **Reliability** — The system shall fall back gracefully when STT fails | `STTEngine.listen()` returns `None` on failure; dialog re-prompts |
| NFR-05 | **Reliability** — The system shall fall back gracefully when the Places API is unavailable or rate-limited | `full_fetch()` catches exceptions and returns empty list; system responds with "no results found" |
| NFR-06 | **Reliability** — The system shall fall back gracefully when geocoding fails | `_geocode_city()` returns `None` on failure; `full_fetch()` proceeds without `locationBias` |
| NFR-07 | **Privacy** — The system shall not store any user data persistently | All slot values held in session memory only; lost on program exit |
| NFR-08 | **Privacy** — The microphone shall be active only during active listening | `listen()` opens and closes microphone per call; no background monitoring |
| NFR-09 | **Security** — The system shall not be susceptible to prompt injection | Closed-domain slot filling: arbitrary input is processed through slot extractors only; no free-text passthrough to APIs |
| NFR-10 | **Maintainability** — The system shall be runnable with a single script | `main.py` — no build step, no framework runtime required beyond pip dependencies |
| NFR-11 | **Maintainability** — All technology choices shall use publicly available libraries with active maintenance | spaCy, edge-tts, scikit-learn, SpeechRecognition, vaderSentiment — all actively maintained open-source packages |
| NFR-12 | **Portability** — The system shall run on Windows without environment-specific configuration | Tested on Windows 11 / Spyder; edge-tts requires no COM/SAPI dependency |

---

## Out of Scope

| Item | Reason |
|---|---|
| Multilingual STT | Requires a different STT model; out of prototype scope |
| Persistent user profiles | Privacy risk; no production requirement |
| Always-on voice monitoring | Sarah opens the app when needed; background monitoring not required |
| LLM-based ranking | No API key; adds opacity; TF-IDF is honest about what it does |
| GDPR compliance infrastructure | Required for production deployment; outside prototype scope |
