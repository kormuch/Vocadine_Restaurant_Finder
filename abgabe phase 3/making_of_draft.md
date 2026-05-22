# Making Of — VocaDine
**Much, Korbinian | IU14127772 | DLMAIWNLPVA02**

---

## 1. Context and USP

VocaDine is a voice-based restaurant finder for English-speaking tourists in Germany, requiring no typing or local knowledge. It addresses a specific cross-lingual failure: en-US speech recognition engines cannot interpret German city names spoken by tourists — a breakdown generic assistants fail to recover from. While production systems might leverage non-deterministic Large Language Models (LLMs) for proper noun mutations (Kumar et al., 2024), VocaDine deliberately rejects LLMs. For a focused product scope, a deterministic phonetic alias whitelist maximizes task speed and execution reliability, eliminating generative hallucinations and dependency on additional inference infrastructure.

---

## 2. Design Philosophy

- **Simplicity:** Technology choices prioritize maintainability and code clarity over unnecessary sophistication.
- **Speed:** Minimal time-to-value; every dialog decision exists to accelerate the path from launching to recommendation.
- **Pragmatism:** Complexity is rejected without user data. A more advanced ranking algorithm would offer false precision.
- **Security:** Closed-domain slot filling structurally thwarts prompt injection threats (Greshake et al., 2023); inputs matching no slot pattern are dropped.

---

## 3. Technology Decisions, Privacy and Limitations

**TTS:** Testing on Windows revealed flaws in pyttsx3: COM exceptions crashed startup and failed to release context, while short utterances ("yes"/"no") were clipped. Replacing it with edge-tts solved these via Azure Neural voices without environment-specific COM dependencies.

**NLU (spaCy & TF-IDF):** A blank spaCy pipeline was selected (Montani et al., 2023) and trained on 600 annotated utterances across five labels (LOCATION, CUISINE, DIET, BUDGET, GROUP_SIZE) using a 420/90/90 split, 40 epochs, and dropout=0.35. Peak validation F1 reached 0.97 (epoch 23), yielding a held-out test Macro-F1 of 0.881. To absorb unannotated edge cases, a hybrid architecture routes neural extraction failures to a rule-based fallback (Weld et al., 2022). LLMs represent architectural overshooting here; a fast, finite slot-state machine is safer, faster, and immune to prompt exploits. Lexical mapping relies on TF-IDF vectorization (Salton & Buckley, 1988); general sentence embeddings trained on broad corpora are not expected to reliably distinguish context-specific cuisine strings, whereas TF-IDF ensures explicit, interpretable token mapping.

**Privacy & Limits:** Audio and query data leave the device — explicitly acknowledged by design. In a production deployment, GDPR Article 13 would require active user notification before first use; no such interface mechanism exists in this functional prototype. Over-quota API limits default safely to "no results found".

---

## 4. Recommendation Engine

**The 40/60 Weighting:** `score = (cosine × 0.4) + (rating/5.0 × 0.6) + bonus`

The 60% weight on Google ratings is an intentional engineering judgment: (1) The tourist assumption: users lack local context; prioritizing aggregate rating acts in their interest using data they do not possess. (2) Non-exclusion: lower-rated exact cuisine matches are reordered, not eliminated. (3) Feature sparsity: when the API returns generic types (["restaurant", "food"]), cosine scores collapse to near-zero; rating provides the stable signal. When editorialSummary or reviews are retrieved, the cosine term operates on richer feature strings and contributes more meaningfully to the score through increased input quality rather than adjusted weights.

**Dialog Design:** Questions are grouped in semantically related pairs (e.g., diet & budget) to minimize conversational turns. Implicit slot filling captures up to 8 slots per utterance (five via the spaCy NER model and three additional slots (occasion, datetime, distance) via the rule-based pass), reducing a 10-slot interview to 2–3 turns in cooperative scenarios. Output is limited to three results, providing sufficient choice without exceeding what a voice interface can usefully convey — consistent with Grice's Maxim of Quantity (1975). Real-time frustration detection uses VADER sentiment analysis (Hutto & Gilbert, 2014); a compound score threshold of −0.5 was chosen empirically for this dialog context, as VADER's default polarity boundaries are calibrated for social media text rather than spoken interaction. Impatience or explicit abort keywords dynamically intercept the user, abort the questionnaire, and instantly trigger the search. End-to-end latency is 6–9s (two external API roundtrips); local STT-to-TTS processing takes ~1.8s.

---

## 5. Phonetic Alias System

The whitelist maps 2058+ German cities to likely en-US STT corruptions, built from empirical pipeline failures and LLM-assisted generation. To guarantee runtime robustness, LLM candidates were manually cross-verified against a validation list of known speech mutations. Word-boundary regex prevents false positives, restricting aliases strictly to documented cross-lingual edge cases (Kumar et al., 2024).

---

## References

Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T., & Fritz, M. (2023). Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection. *Proceedings of the 12th Workshop on Artificial Intelligence Safety (WAISE)*. https://doi.org/10.48550/arXiv.2302.12173

Grice, H. P. (1975). Logic and conversation. In P. Cole & J. Morgan (Eds.), *Syntax and Semantics* (Vol. 3, pp. 41–58). Academic Press.

Hutto, C., & Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. *Proceedings of the International AAAI Conference on Web and Social Media, 8*(1), 216–225. https://doi.org/10.1609/icwsm.v8i1.14550

Kumar, R., Ghosh, S., & Ramakrishnan, G. (2024). Beyond common words: Enhancing ASR cross-lingual proper noun recognition using large language models. *Findings of the Association for Computational Linguistics: EMNLP 2024*, 6821–6828. https://doi.org/10.18653/v1/2024.findings-emnlp.399

Montani, I., Honnibal, M., Boyd, A., Van Landeghem, S., & Peters, H. (2023). *explosion/spaCy: v3.7.2* (v3.7.2) [Software]. Zenodo. https://doi.org/10.5281/zenodo.10009823

Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval. *Information Processing & Management, 24*(5), 513–523. https://doi.org/10.1016/0306-4573(88)90021-0

Weld, H., Huang, X., Long, S., Poon, J., & Han, S. C. (2022). A survey of joint intent detection and slot filling models in natural language understanding. *ACM Computing Surveys, 55*(8), 1–38. https://doi.org/10.1145/3547138
