# VocaDine Phase 3 — Master Todo & Issue Tracker

**Last updated:** 2026-05-13
**Status:** Phase 2 submitted and graded. Phase 3 in progress.

## Code changelog

| Version | Date | Changes |
|---|---|---|
| v0.2 | Apr 2026 | Phase 2 submission — spaCy NER, implicit slot filling, VADER, TF-IDF ranking. Archived as `main_v0.2_archive.py`. |
| v0.3 | 2026-05-13 | [#16] Venue type filter (`_is_food_venue`, `_FOOD_TYPES`). [#17] Radius search via `_geocode_city()` + `locationBias` 3km. German comments translated. See design decisions below. |

---

---

## v0.3 Design Decisions

### #16 — Venue type filter: allowlist over blocklist

**Decision:** Keep a venue if its `types` contains at least one of `_FOOD_TYPES` (`restaurant`, `food`, `meal_takeaway`, `meal_delivery`, `cafe`, `bakery`) or any type ending in `_restaurant`.

**Why allowlist, not blocklist:** A blocklist of excluded types (shisha bar, night club, etc.) is incomplete by definition — new venue types get added to the Places API taxonomy over time. An allowlist of food-specific types is closed and stable. A restaurant will always have `restaurant` or `food` in its types; a shisha bar will not.

**Why this is the right scope:** Sarah wants to eat. Any venue that doesn't have a food type in the API response is not relevant to her, regardless of what it is. The filter is a principled scope boundary, not a one-off exclusion.

**Known limitation:** Venues with no `types` returned (API omission) pass the filter silently — `set([]) & _FOOD_TYPES` is empty → filtered out. This is the safer failure mode (exclude unknown) vs. including a non-food venue.

---

### #17 — Radius search: `locationBias` over `locationRestriction`

**Decision:** Use `locationBias` (soft preference) with 3km radius, not `locationRestriction` (hard cutoff).

**Why bias, not restriction:** `locationRestriction` would return zero results if no food venues exist within 3km — likely in small German towns like Haigerloch where Sarah's use case originates. `locationBias` ranks nearby results higher but falls back to the wider city if the local set is sparse. For Sarah, a result 4km away is better than no result.

**Why 3km:** Walking distance in a city is typically 1–2km. 3km covers a reasonable taxi/tram radius without expanding to a different district. A 10km radius in Berlin would still return Charlottenburg results for a Zehlendorf user.

**Why geocode separately:** The Places API (New) `locationBias` requires lat/lng, not a city name. The Geocoding API resolves city name → coordinates. The geocode result is cached per session — one additional API call per session, not per query.

**Fallback:** If geocoding fails (network error, unknown city, rate limit), `full_fetch()` proceeds without `locationBias` — identical to v0.2 behavior. Sarah gets a result, just without geographic precision.

---

## Part 1 — Anne Schwerk Issue Matrix

All issues raised in Phase 1 and Phase 2 feedback. Each entry: what Anne said, where it currently stands in the code/docs, honest verdict.

---

### Phase 1 Issues

| # | Anne's Issue | Current State | Verdict |
|---|---|---|---|
| P1-1 | Limited novelty — what distinguishes VocaDine from Google Assistant / Alexa? | README has scoped Alexa comparison table with 7 specific differentiators. Phonetic alias system is the clearest unique angle. | ✅ Sufficient — but the Making Of must name the *scoped claim* explicitly: "stronger than Alexa at this specific failure case, weaker in ecosystem" |
| P1-2 | Dialogue too deterministic — should adapt based on responses, not follow rigid sequence | Code: `run_interview()` uses paired bundling, implicit slot filling extracts up to 5 slots/utterance, past_experience infers diet, impatience skips remaining slots | ✅ Sufficient — the code genuinely does dynamic dialog. Must be clearly explained in Making Of, not just listed |
| P1-3 | Recommendation mechanism underspecified — how are restaurants represented, how are preferences encoded, how does ranking work? | Code: `build_features()` concatenates name + types + editorialSummary + reviews (up to 3) + structured attribute tokens. User pref string: cuisine + diet + occasion + past_experience. TF-IDF cosine + rating (40/60) + budget_bonus + attribute_bonus. README has full formula. | ⚠️ Code is solid but still underdocumented. The feature engineering (including editorialSummary, reviews, attribute injection) is not visible in Phase 2 slides. Making Of must describe what `build_features()` actually does. |
| P1-4 | Technology choices not justified — why pyttsx3, why classical ML over embeddings/LLMs? | README has "Technology Decisions" section. pyttsx3: COM Exception in Spyder/IPython. TF-IDF: no API key, deterministic, on-demand. Anne flagged in Phase 2 that pyttsx3 switch was not explained. | ⚠️ Lazy. The reasons exist but are treated as one-liners. Making Of needs a paragraph each: what failed, why the alternative was chosen, what was given up. |
| P1-5 | Practical constraints not addressed — API rate limits, STT errors, incomplete data | Error analysis (23 items) covers STT failures. Validation probe covers empty results. Rate limits: not mentioned anywhere. | ❌ Rate limits not addressed. One sentence in Making Of: Google Places free tier limits and what happens if they're hit (currently: exception caught, returns empty list → "no results" message). |
| P1-6 | Diagram clarity — abstract labels, unclear module boundaries, no data flow annotations | architecture_diagram.html is a standalone 5-layer SVG. Data flows are shown with arrows. | ✅ Adequate for Phase 3. No changes needed unless Making Of references it. |

---

### Phase 2 Issues

| # | Anne's Issue | Current State | Verdict |
|---|---|---|---|
| P2-1 | Recommendation mechanism: feature engineering still shallow. 40/60 weighting — empirical or arbitrary? What happens when types are generic ("restaurant")? | Code: `build_features()` uses name, types, editorialSummary, reviews[:3], structured attribute tokens. This is richer than Anne saw. The 40/60 question: README says "not empirically calibrated, design judgment" — this is the right answer but only in the README, not in slides or Making Of yet. | ⚠️ The code is better than documented. Need to expose what `build_features()` actually does. 40/60: answer exists in README, must be in Making Of verbatim. |
| P2-2 | pyttsx3 → edge-tts switch: never explained. TF-IDF justification is a convenience argument, not methodology. Does TF-IDF actually capture semantic differences on short type strings? | pyttsx3: README has one paragraph on COM Exception. edge-tts decision and quality difference: mentioned but thin. TF-IDF honest limitation: README says "on very short type strings, cosine produces low-confidence scores — mitigated by 0.6 rating weight." | ⚠️ Partially addressed. The TF-IDF limitation is honestly stated in README. Missing: any measurement or example of when cosine fails vs. when reviews/summary save the score. Making Of: one concrete example. |
| P2-3 | "Train NLP Models" claim is thin — fit_transform() at runtime is not model training in the course sense. | Code: spaCy NER is genuinely trained (600 utterances, 40 epochs, saved model). TF-IDF vectorizer is fit_transform at runtime in `rank()` (line 377). README distinguishes both. Slide 5 header "TRAIN NLP MODELS" is technically the slide covering spaCy training — but TF-IDF sits nearby. | ⚠️ The code distinction is real and correct. Making Of must make it explicit and clear. Do not let the two get conflated anywhere in Phase 3 docs. |
| P2-4 | Macro-F1 = 1.000 on 20 curated test cases is naive, not rigorous. Evaluation contradicts error analysis (how can it be perfect and have 11 error categories?). | Fixed in Phase 2 submission: spaCy NER evaluated on 90 held-out test utterances, Macro-F1 = 0.881. Val-F1 peak = 0.97 (checkpoint selection). README explicitly explains the gap. test_results.json exists. | ✅ Fixed. But Making Of must keep this framing: 0.881 on held-out test set, val-F1 = 0.97 is optimistic by design. Do not let 1.000 appear anywhere in Phase 3. |
| P2-5 | Latency discrepancy — 1.8s reported vs. "8 seconds later" on Slide 1. Which includes the API call? | README: "~1.8s local latency (STT result → ranking → TTS start)" and "~6–9s end-to-end (incl. 2× Places API)." Slide 1 was revised to ~7s. | ✅ Fixed in Phase 2. Making Of: report both figures with explicit scope. STT→TTS = 1.8s local; full pipeline = 6–9s. |
| P2-6 | Privacy discussion superficial — "no always-on microphone" is not a privacy feature. Audio leaves the device. Where does it go, under what conditions? | README lists: Audio → Google Cloud (Web Speech API), Location + preferences → Google Places API as textQuery. "No always-on monitoring." GDPR Art. 13 mentioned for production. | ⚠️ The facts are in the README but framed defensively. Making Of: acknowledge the data flows honestly, state what Google's terms say about processing, and note what would be needed for GDPR compliance. Do not present "no always-on" as a privacy achievement. |
| P2-7 | Literature decorative — Grice for top-3 is a design decision that doesn't need a citation to be valid. References aren't doing work. | README has 5 citations each with an explicit design connection. Grice: top-3 decision. Hutto & Gilbert: ImpatienceDetector. Rafailidis & Manolopoulos: TF-IDF vs. popularity ranking. | ⚠️ Rafailidis is the strongest citation (it directly supports the TF-IDF + rating hybrid). Grice is marginal — if cited, it must be because the "maxim of quantity" framing actively shaped the output design, not because it sounds good. Making Of: only cite what you can defend in one sentence. |

---

### Slide-level notes (still open)

| # | Issue | Status |
|---|---|---|
| S1 | "0 Typing Required" as a KPI — trivial for any voice assistant | ❌ Must be removed from any slides resubmitted in Phase 3 |
| S3 | Alexa comparison as strawman — should acknowledge Alexa's superior ecosystem | ⚠️ README already has a note scoping the comparison. Slides should add one line. |
| S5 | Slide header "TRAIN NLP MODELS" conflates spaCy NER and TF-IDF fit_transform | ⚠️ If slides are revised, split this: one section for spaCy NER (real training), one for TF-IDF (on-demand vectorization). |

---

## Part 2 — How the project actually works

This is the ground truth from reading the code. For every feature: what it does, where it lives, how it's justified (to Anne and to Sarah).

---

### System Overview

```
User speaks → STT (Google Web Speech, en-US) → raw transcript
→ City whitelist correction (german_cities.py)
→ NLU._extract_multiple_slots() [spaCy NER + rule fallback]
→ DialogStateManager.run_interview() [10 slots, implicit filling]
→ GooglePlacesClient.full_fetch() [Places API New]
→ RecommendationEngine.rank() [TF-IDF cosine + rating + bonuses]
→ TTSEngine.speak() [edge-tts, en-US-JennyNeural]
```

---

### Feature 1 — STT (STTEngine, main.py:122)

**What it does:** Captures audio via microphone. Uses Google Web Speech API with `en-US` language. `pause_threshold=1.5s`, `phrase_time_limit=15s`, `timeout=7s`.

**Justified to Sarah:** Sarah speaks English. Google Web Speech is free, reliable for en-US, no API key needed beyond the standard. Works on any laptop with a microphone.

**Justified to Anne:** Explicit choice over alternatives. Offline models (Whisper) would improve privacy but add setup complexity and latency. `pause_threshold` was tuned (down from 2.5s default) to reduce perceived lag. Known limitation: German city names fail in en-US — documented and solved by whitelist.

**Honest limitations:**
- Google processes audio in the cloud (privacy implication — see P2-6)
- Short words ("no", "two") misrecognised ~20% of the time — mitigated by word-boundary regex
- Confidence score not exposed by the Python API — prevents low-confidence re-prompt (Error #23, open)

---

### Feature 2 — German City Whitelist (german_cities.py, used in main.py:215, 474)

**What it does:** Dict of 2058+ German cities, each with zero or more phonetic alias keys. Word-boundary regex (`\b...\b`) prevents substring false positives. Applied in two places: `_normalise_spacy_value()` for spaCy-extracted locations, and as a fallback in `_extract_multiple_slots()`.

**Examples:**
- "hi girl" → Haigerloch
- "tubing in" → Tübingen
- "hope america" → Horb am Neckar
- "beirut" → Bayreuth

**Justified to Sarah:** Without this, Sarah says "Haigerloch" and gets zero results. The whitelist is the core differentiation from generic voice assistants.

**Justified to Anne:** Real problem, real solution, documented with concrete examples. The word-boundary regex (`\b` pattern) was added specifically to fix "germany" → cuisine=German and "hamburg" → location=Burg. Both bugs are in the error analysis.

**Honest limitations:** Aliases are manually created — they cover known failures, not exhaustive en-US phonetic space. Sublocation (district within a city) not supported — Error #17, open for Phase 3.

---

### Feature 3 — NLU: spaCy NER (NLU class, main.py:267)

**What it does:** A blank spaCy English model trained on 600 manually annotated utterances. Labels: LOCATION, CUISINE, DIET, BUDGET, GROUP_SIZE. Best checkpoint from 40 training epochs saved to `models/vocadine_nlu/`.

**Training:** `train_nlu.py`, 420 train / 90 val / 90 test (split_data(seed=42)). Compounding batch 4→32, dropout=0.35, 40 epochs. Best epoch saved when val-F1 peaks.

**Evaluation:**
- Macro-F1 = 0.881 on 90 held-out test utterances (never seen during training or checkpoint selection)
- Val-F1 peak = 0.97 at epoch 23 — this is the checkpoint signal, optimistic by design
- Per-label: LOCATION 0.981, DIET 0.971, CUISINE 0.925, BUDGET 0.818, GROUP_SIZE 0.711

**Architecture in code:** `extract_all_spacy()` runs the model, returns all recognised entity spans. `_normalise_spacy_value()` maps raw entity text to canonical slot values (e.g. "plant based" → "vegan"). Loaded once at `NLU.__init__()`, falls back to rule-only if model not found.

**Justified to Sarah:** Understands natural phrasing ("something light and plant-based for two") in a single pass, without forcing Sarah to use keyword commands.

**Justified to Anne:** This is the real NLP training component. Blank model demonstrates training pipeline clearly (no pretrained vectors needed for closed 5-label domain). The train/val/test split is principled. Val-F1 is used for checkpoint selection — which is standard practice, explicitly acknowledged as optimistic. Test-F1 on held-out set is the honest number.

**Honest limitations:** GROUP_SIZE F1 = 0.711 — weakest label, word-number patterns ("a couple", "just me") partially covered by rule fallback. Adversarial input (typos, thick accents, background noise) not tested.

---

### Feature 4 — NLU: Rule-based fallback (_extract_multiple_slots, main.py:453)

**What it does:** After spaCy's pass, fills any remaining unfilled slots using keyword maps and regex patterns. Covers: cuisine list (20+ types), diet keywords, budget map (20+ phrases), occasion map (10+ phrases), datetime map, distance map, group size patterns (word numbers, relationship phrases, digit extraction).

**Key implementation details:**
- All patterns use `\b` word boundaries where substring risk exists
- Negation handling: `re.search(r'\b(none|no restrictions?...)\b')` for diet=none
- "me and my family" → 4; "the two of us" → 2; "me and my partner" → 2 (explicit relationship patterns)
- "surprise me" / "no preference" → all remaining slots = "any"
- "stop asking / search now" → all remaining slots = "any" (shortcut to search)

**Justified to Anne:** spaCy handles the first pass. Rule fallback catches what the model misses for slots outside the 5 trained labels (occasion, datetime, distance, special_features) and provides robustness within trained labels. The dual-pass architecture is explicitly documented in the README.

**Honest limitations:** Negation in complex sentences is shallow — "they served meat and I don't like meat" may not parse correctly (documented in code comment at line 659 and Error #19).

---

### Feature 5 — Implicit slot filling & bundled questions (run_interview, main.py:769)

**What it does:** Single open question at the start allows user to volunteer multiple slots at once. `_extract_multiple_slots()` fills up to 5 slots from one utterance. Dialog then asks only for remaining unfilled slots. Slots are asked in logical pairs: diet+budget together, group_size+occasion together, datetime+distance together.

**Example:** "I want Italian for two tonight in Munich, nothing too fancy" → fills cuisine, group_size, datetime, location, budget in one turn. Dialog skips all five slot questions.

**Justified to Sarah:** Reduces the number of turns Sarah has to take. If she gives a rich initial answer, the dialog can complete in 2-3 turns instead of 10.

**Justified to Anne:** Directly addresses Phase 1 criticism about rigid deterministic dialog. The course requires "10 questions and 10 answers" — this is met because 10 slots exist and each has an associated question, but the system is smart enough to skip questions when information is already available. This design choice is explicitly explained in README and Slide 4.

---

### Feature 6 — Validation probe (GooglePlacesClient.probe, main.py:158)

**What it does:** Before accepting a high-impact slot value (location, cuisine, diet), makes a lightweight Places API call. If result count = 0, slot is rolled back and user is re-asked: "I couldn't find results for X, let's try another choice."

**Justified to Sarah:** Prevents the system from reaching the end of the interview and returning zero results for a combination that was never going to work (e.g. "vegan kosher fine dining in Haigerloch").

**Justified to Anne:** Explicit mechanism for handling API failure states — directly addresses P1-5 (practical constraints). Lightweight probe (text search, not full fetch) minimises latency and API quota usage.

**Honest limitations:** Only checks high-impact slots individually, not their combination. A combination of valid individual slots could still return 0 results from full_fetch.

---

### Feature 7 — Recommendation Engine (RecommendationEngine, main.py:332)

**What it does:**

1. `build_features(biz)`: Constructs a feature string per restaurant from:
   - `name` (from displayName.text)
   - `types` (API-returned category strings, e.g. "italian_restaurant food_and_drink")
   - `editorialSummary.text` (when available — richer semantic content)
   - `reviews[:3]` text (when available — customer language)
   - Structured attribute tokens: "outdoor seating terrace" if `outdoorSeating=True`, "good for groups large party" if `goodForGroups=True`

2. User preference string: `cuisine + diet + occasion + past_experience`

3. TF-IDF vectorizer fit_transform on all feature strings + user string together (on-demand, not a saved model)

4. Cosine similarity between user vector and each restaurant vector

5. Scoring formula:
   ```
   score = (cosine × 0.4) + (rating/5.0 × 0.6) + budget_bonus + attribute_bonus
   ```
   - `budget_bonus`: +0.1 if `priceRange.endPrice` matches user budget slot (cheap ≤ €15, moderate €16-35, fine dining > €35)
   - `attribute_bonus`: +0.1 for outdoor seating match, +0.1 for goodForGroups when group ≥ 4
   - `price_level` (deprecated int 1-4) deliberately not used — unreliably populated in Places API New

6. Top 3 returned (Grice Maxim of Quantity — bounded, justified)

**Justified to Sarah:** Returns the three most relevant restaurants based on her stated preferences, weighted toward real aggregate rating (more reliable than keyword match on short strings).

**Justified to Anne — on the 40/60 split:** Not empirically calibrated. Design judgment: on short type strings like "italian_restaurant food", TF-IDF cosine produces low-confidence scores due to sparse vocabulary. Google's aggregate rating averages hundreds of user reviews — it is a more stable signal in this feature-sparse environment. A 50/50 split was considered and rejected for this reason. When reviews and editorialSummary are available, cosine becomes a stronger contributor. The split is honest about its basis.

**Justified to Anne — on TF-IDF vs. embeddings:** fit_transform at runtime is not model training. It is on-demand vectorization. The distinction matters: TF-IDF is interpretable, requires no external model, and its limitations are explicit (poor on sparse features). The real trained model is spaCy NER. These two components serve different roles in the pipeline and must not be conflated.

**Honest limitations:** When `types` is only ["restaurant"], cosine similarity will be near-zero across all venues. The 0.6 rating weight partially compensates. This is a known degradation path, documented in README.

---

### Feature 8 — ImpatienceDetector (main.py:398)

**What it does:** Two-signal detection:
- VADER sentiment: compound score < -0.5 → strong frustration, immediate skip
- VADER mild: compound < -0.2 AND no slot filled → mild frustration with no useful info → skip
- Keyword patterns: explicit stop words ("stop asking", "just find", "I already told you")

When triggered: all remaining empty slots set to "any", system apologises and proceeds to search.

**Justified to Anne:** Demonstrates applied sentiment analysis (VADER, Hutto & Gilbert 2014) in a real dialog context. The two-signal approach (lexical + sentiment) is more robust than keyword-only. VADER is appropriate here: real-time, no additional API, handles informal language.

**Honest limitations:** VADER is calibrated for social media text, not dialog. Frustration expressed politely ("Could we perhaps move a bit faster?") will not trigger it. This is documented but not fixed — appropriate for prototype scope.

---

### Feature 9 — Ambiguity detection (_detect_ambiguity, main.py:664)

**What it does:** Checks if ≥ 2 cuisine keywords appear in one utterance → asks clarification. Example: "Italian or Greek, I'm not sure" → "I noticed you mentioned both Italian and Greek. Which would you prefer?"

**Justified to Sarah:** Prevents silent wrong choice (e.g. first match wins).

**Justified to Anne:** Small but genuine dialog intelligence. Shows the system is listening for conflict, not just filling slots greedily.

---

### Feature 10 — Diet inference from past_experience (_infer_diet_from_past_experience, main.py:625)

**What it does:** After past_experience is filled, checks for meat keywords. If meat mentioned without negation → diet = "none" (infers no restriction). If meat + negation → does not infer, asks normally (known edge case, code comment at line 659).

**Justified to Anne:** Shows NLU reasoning beyond keyword matching. The limitation (shallow negation in complex sentences) is honestly documented in both code comments and Error Analysis #19.

---

### Feature 11 — Google Places API (New) (GooglePlacesClient.full_fetch, main.py:168)

**What it does:** POST to `https://places.googleapis.com/v1/places:searchText` with FieldMask requesting: displayName, formattedAddress, rating, priceLevel, types, editorialSummary, reviews, outdoorSeating, goodForGroups, priceRange.

Query string built from: cuisine + diet (if not "none") + "restaurant" + "in {location} Germany" + special_features.

**Justified to Sarah:** Real-time data. No static database of restaurants needed.

**Justified to Anne:** Uses the new Places API (v1), not deprecated text search. `price_level` explicitly not used (deprecated, unreliably populated). `priceRange.endPrice` used instead. This is a deliberate, documented decision.

**Honest limitations:** API rate limits apply (free tier: 100 requests/day for text search). Currently: exception caught → returns empty list → system says "no results." Not surfaced to user as a distinct error. For production, exponential backoff and user messaging would be needed.

---

## Part 3 — Phase 3 deliverables checklist

### Making Of (2 pages, Arial 11pt, 1.5-spaced)
- [ ] 40/60 weighting: answer directly — not empirically calibrated, design judgment, why
- [ ] pyttsx3 → edge-tts: what broke (COM Exception in Spyder/IPython), what edge-tts provides (Azure Neural, no API key, no env issues), what was given up (internet dependency)
- [ ] spaCy NER vs. TF-IDF: clearly separated — spaCy is the real trained model, TF-IDF is on-demand vectorization. Both present, different roles.
- [ ] build_features() described: name + types + editorialSummary + reviews[:3] + attribute tokens — richer than Anne saw in Phase 2
- [ ] Privacy: audio goes to Google Cloud, preferences go to Places API, honest framing of what that means
- [ ] Literature: only cite what earns its place — Hutto & Gilbert for VADER, Rafailidis & Manolopoulos for TF-IDF+rating hybrid, Grice only if framing is precise
- [ ] Rate limits: one sentence acknowledgment
- [ ] Do not let F1=1.000 appear anywhere

### Mandatory ZIP docs
- [ ] Functional & non-functional requirements document (write from scratch)
- [ ] Design document (formal — derive from README architecture section)
- [ ] Dataset description (600 utterances: what they cover, how annotated, split rationale, seed=42)
- [ ] Data annotation guidelines ✅ already exists: `data/annotation_guidelines.md`
- [ ] Evaluation metrics table ✅ already exists: `test_results.json`
- [ ] GitHub link ✅

### ZIP folder structure
```
01-Research-and-Development/   ← research notes, annotation guidelines, dataset description
diagrams/                      ← architecture_diagram.html / exported PNG
voice assistant/               ← main.py, train_nlu.py, eval_nlu.py, german_cities.py, data/, models/
04-Finished voice assistant/   ← user documentation + run script (README subset, install instructions)
```

### Formal submission
- [ ] Re-upload Phase 1 result in PebblePad
- [ ] Re-upload Phase 2 result in PebblePad
- [ ] Upload Phase 3 Making Of PDF
- [ ] Upload Final Product PDF (with GitHub link)
- [ ] Affidavit via myCampus

### File naming
`Much-Korbinian_IU14127772_Voice Assistants_P3_S`

### Code (optional but strengthens grade)
| Priority | Feature | File | Problem | Status |
|---|---|---|---|---|
| High | Venue type filter | main.py | Shisha bars, nightclubs in results — filter `types` list (Error #16) | ✅ Done — `_is_food_venue()` + `_FOOD_TYPES` allowlist, applied in `full_fetch()` after mapping. Logs filtered count to session log. |
| High | Radius search 3km | main.py | Add `locationBias` with 3km radius to full_fetch body (Error #17) | ✅ Done — `_geocode_city()` caches lat/lng per session; `locationBias` circle added to `full_fetch()` body. Falls back to text-only if geocoding fails. |
| Medium | German food aliases | german_cities.py | "snit cell" → Schnitzel, extend cuisine alias map (Error #22) | ⬜ Open |
| Medium | Low-confidence re-prompt | main.py | STTEngine.listen() always returns None on failure — add confidence threshold or audio energy check (Error #23) | ⬜ Open |

---

## Part 4 — Honest summary

**What is genuinely strong in this project:**
- The phonetic alias system: real problem, documented failures, working solution
- spaCy NER pipeline: proper train/val/test split, honest metric reporting, working model
- Implicit slot filling: demonstrably more flexible than rigid Q&A
- Error analysis: 23 items, 19 fixed, 4 open — this is the intellectual model for the whole project
- The code is cleaner and more capable than the Phase 2 documentation showed

**What is still underdocumented relative to the code:**
- `build_features()` uses reviews and editorialSummary — Anne never saw this
- Rule-based fallback covers 10 slots across 60+ keywords — not fully visible in slides
- `_infer_diet_from_past_experience()` is a nice NLU move that got no attention

**What needs to be fixed in Making Of (not code):**
- 40/60 answer: direct, honest, one paragraph
- pyttsx3 decision: one paragraph with the actual reason
- Privacy: acknowledge what leaves the device
- Remove F1=1.000 from any Phase 3 material
