# Making Of — VocaDine
**Much, Korbinian | IU14127772 | DLMAIWNLPVA02**

---

## Context and USP

VocaDine is a voice-based restaurant finder designed for English-speaking tourists in Germany, requiring no typing and no local knowledge. Its specific problem: an English-speaking tourist names a German city to an en-US speech recognition engine, which the engine does not understand — a failure generic voice assistants do not recover from (Takeda et al., 2014; Datta et al., 2024).

---

## Design Philosophy

- **Simplicity by design.** Every technology choice prioritizes maintainability and clarity over sophistication.
- **Speed by design.** The user wants a fast recommendation; every dialog decision exists to minimize time between opening the app and hearing a result.
- **Prototype scope is real scope.** Complexity is added only when evidence supports it — without real user data, a more sophisticated ranking algorithm would be false precision.
- **Security by design.** Closed-domain slot filling structurally prevents prompt injection: input that matches no slot pattern returns no values and is ignored.

---

## Technology Decisions

### TTS: pyttsx3 → edge-tts

Development started with pyttsx3, a known quantity from a prior project. Two problems emerged during testing in Spyder/IPython on Windows: (1) COM Exception — pyttsx3's dependency on Windows SAPI via COM caused crashes on startup and failed to release context cleanly between test runs; (2) short utterance failure — responses like "yes" or "no" were frequently dropped or garbled. edge-tts was selected as the replacement: no COM dependency, reliable on short outputs, no environment-specific setup, and higher output quality via Azure Neural voices. The switch followed from observed testing failures, not a planned architectural decision.

### NLU: spaCy NER and TF-IDF

These two components serve different roles and should not be described as equivalent.

**spaCy NER is the trained model.** A blank spaCy English model was trained on 600 manually annotated utterances across five labels: LOCATION, CUISINE, DIET, BUDGET, GROUP_SIZE. Training used a 420/90/90 train/val/test split (seed=42), 40 epochs, dropout=0.35. The best checkpoint was selected by peak validation F1 (0.97 at epoch 23 — the checkpoint-selection signal, optimistic by design). Evaluation on the fully held-out test set yields Macro-F1 = 0.881. Training scope was deliberately limited under an 80/20 prioritisation: robust coverage of edge cases — regional language variation, domain-specific restaurant vocabulary — would require expert annotation at significantly larger scale. Edge cases fall through to the rule-based fallback.

**TF-IDF is on-demand vectorization.** `TfidfVectorizer.fit_transform()` runs at query time across the current result set. There is no saved TF-IDF model; the vocabulary changes with every query.

### Recommendation Engine: the 40/60 weighting

`score = (cosine × 0.4) + (rating/5.0 × 0.6) + bonuses`

The 60% weight on Google's aggregate rating is a design judgment, not an empirically calibrated parameter. Three reasons: first, the tourist assumption — the user does not know the local restaurant landscape; weighting rating higher means the system acts on information the user lacks, in their interest (Rafailidis & Manolopoulos, 2019). Second, the top-3 design — a cuisine match is not eliminated, only reordered; a lower-rated exact match still appears, just not at position one. Third, feature sparsity — when the Places API returns only generic type data such as `["restaurant", "food"]`, TF-IDF cosine produces near-zero scores across all venues; aggregate rating is the more stable signal in this case (Khadka, 2023; Li et al., 2021). When `editorialSummary` and `reviews` are available in `build_features()`, cosine becomes a stronger contributor. The weighting was not tuned empirically — tuning requires user session data that does not exist at prototype stage.

### Dialog Design

Questions are asked in semantically related pairs — diet and budget together, group size and occasion together, time and distance together — reducing turn count without reducing information gathered. Implicit slot filling allows the user to volunteer multiple slots in one utterance, reducing a 10-slot interview to 2–3 turns in practice. The top-3 output limit follows Grice's Maxim of Quantity (1975). When VADER sentiment scoring detects frustration (compound < −0.5) or explicit stop keywords are used, remaining slots are set to "any" and the system proceeds to search immediately (Hutto & Gilbert, 2014). End-to-end latency is 6–9 seconds including two Places API calls; local processing from STT result to TTS start is approximately 1.8 seconds.

### Phonetic Alias System

The whitelist maps 2058+ German cities to their phonetically likely en-US STT transcriptions, created from observed STT failures and extended with LLM-assisted generation. Word-boundary regex prevents substring false positives — documented cases such as "germany" triggering cuisine=German and "hamburg" triggering city=Burg were resolved this way. A production system would use IPA-based phonetic generation; the curated whitelist is the prototype-appropriate solution (Datta et al., 2024).

---

## Limitations and Privacy

Audio is sent to Google Cloud via the Web Speech API; location and preferences are transmitted to the Google Places API. No data is stored persistently. Google's infrastructure was chosen for reliability and real-world deployability — the consequence, user audio leaving the device, is acknowledged. For production deployment, GDPR Article 13 obligations would apply. Google Places API free-tier rate limits apply; if exceeded, the system returns "no results found" — production use would require exponential backoff. Identified future improvements: session memory for repeating prior recommendations, IPA-based alias generation, and low-confidence STT re-prompting (currently blocked by Web Speech API not exposing confidence scores).

---

## References

Datta, A., et al. (2024). Beyond common words: Enhancing ASR cross-lingual proper noun recognition using large language models. *Findings of EMNLP 2024*. ACL Anthology.

Grice, H. P. (1975). Logic and conversation. In P. Cole & J. Morgan (Eds.), *Syntax and Semantics, Vol. 3* (pp. 41–58). Academic Press.

Hutto, C. J., & Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. *Proceedings of the 8th International Conference on Weblogs and Social Media (ICWSM)*. AAAI Press.

Khadka, P. (2023). Content-based recommendation engine for video streaming platform. *arXiv:2308.08406*.

Li, Y., et al. (2021). Hybrid algorithm based on content and collaborative filtering in recommendation system optimization. *Scientific Programming*. Wiley.

Rafailidis, D., & Manolopoulos, Y. (2019). Can virtual assistants produce recommendations? *Proceedings of WIMS*.

Takeda, H., et al. (2014). Improving recognition of proper nouns in end-to-end ASR by phonetic transcription. *Speech Communication, 62*, 1–12. Elsevier.

Weld, H., et al. (2022). A survey of intent classification and slot-filling datasets for task-oriented dialog. *arXiv:2207.13211*.
