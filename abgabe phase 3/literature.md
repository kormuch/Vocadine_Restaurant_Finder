# VocaDine — Literature & Design Decision References

All citations used or considered for VocaDine. Each entry states the design decision it supports and the exact claim it justifies. Only cite what earns its place.

---

## Core citations (used in Phase 2, carried forward)

**[1]** Grice, H. P. (1975). Logic and conversation. In P. Cole & J. Morgan (Eds.), *Syntax and Semantics, Vol. 3: Speech Acts* (pp. 41–58). Academic Press.
→ **Design decision:** Top-3 output limit
→ **Claim:** Maxim of Quantity — be as informative as required, not more. Reading 50 restaurants aloud causes analysis paralysis. Top-3 is the principled bound.
→ **Verdict:** Marginal but defensible. Only cite if the framing is precise — not as a philosophical decoration.

**[2]** Hutto, C., & Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. *Proceedings of the International AAAI Conference on Web and Social Media, 8*(1), 216–225. https://doi.org/10.1609/icwsm.v8i1.14550
→ **Design decision:** ImpatienceDetector implementation
→ **Claim:** VADER is real-time, requires no external model, and handles informal/colloquial language — appropriate for a live dialog context where latency matters.
→ **Verdict:** Strong. Direct implementation reference.

**[3]** Ravi, L., & Vairavasundaram, S. (2016). A collaborative location based travel recommendation system through enhanced rating prediction for the group of users. *Computational Intelligence and Neuroscience, 2016*, 1–28. https://doi.org/10.1155/2016/1291358
→ **Design decision:** TF-IDF + rating hybrid ranking; 40/60 weighting
→ **Claim:** Rating-based prediction improves recommendation quality in location-based travel contexts. Directly supports weighting aggregate rating higher than content similarity in sparse-feature environments.
→ **Verdict:** Strong. Peer-reviewed, directly on-topic for location + rating hybrid recommendation.

**[4]** Ukpabi, D. C., Aslam, B., & Karjaluoto, H. (2019). Chatbot adoption in tourism services. In *Robots, AI, and Service Automation in Travel, Tourism and Hospitality*. Emerald.
→ **Design decision:** Use case relevance (tourist context)
→ **Claim:** Voice and conversational interfaces are relevant and adopted in tourism — situates VocaDine in a real application domain.
→ **Verdict:** Weak as a standalone citation. Only useful if the Making Of needs to justify the tourism use case framing. Can be dropped if space is tight.

**[5]** Abdullah, T., & Ahmet, A. (2022). Deep learning in sentiment analysis: Recent architectures. *ACM Computing Surveys, 55*(8), 1–37.
→ **Design decision:** Choice of VADER over deep learning sentiment models
→ **Claim:** Deep learning sentiment models require significant compute and offline training; VADER is appropriate when real-time inference and no additional API dependency are constraints.
→ **Verdict:** Weak. The argument doesn't need a survey paper — it can stand on its own. Only keep if cited precisely.

---

## New citations (Phase 3 — identified during research)

**[6]** Kumar, R., Ghosh, S., & Ramakrishnan, G. (2024). Beyond common words: Enhancing ASR cross-lingual proper noun recognition using large language models. *Findings of the Association for Computational Linguistics: EMNLP 2024*, 6821–6828. https://doi.org/10.18653/v1/2024.findings-emnlp.399
→ **Design decision:** Phonetic alias whitelist as prototype-appropriate solution
→ **Claim:** Current research solves cross-lingual proper noun ASR failure with LLM-based phonetic dictionaries. VocaDine uses a manually curated whitelist — simpler, deterministic, appropriate for a closed-domain prototype with a known city set.
→ **Verdict:** Strong framing citation — situates the whitelist in active research, honestly acknowledges the production alternative.
→ **URL:** https://aclanthology.org/2024.findings-emnlp.399/

**[10]** Weld, H., Huang, J., Lee, S., Zhang, T., Wang, K., & Long, G. (2022). A survey of joint intent detection and slot filling models in natural language understanding. *ACM Computing Surveys, 55*(8), 1–38. https://doi.org/10.1145/3547140
→ **Design decision:** NER-based slot filling; multi-slot extraction from single utterance
→ **Claim:** Slot filling (extracting semantic slot values from user utterances) is the standard NLU component in task-oriented dialog systems. Multi-slot extraction from single utterances is an established design goal, not an unusual approach.
→ **Verdict:** Good survey reference. Situates spaCy NER and implicit slot filling in standard practice.
→ **URL:** https://arxiv.org/abs/2207.13211

**[11]** Xu, P., & Sarikaya, R. (2013). Convolutional neural network based triangular CRF for joint intent detection and slot filling. *IEEE ASRU*.
→ (See also: Survey — ACM Computing Surveys, 2022, doi:10.1145/3547138)
→ **Design decision:** spaCy NER as slot filling model; rule fallback as second pass
→ **Claim:** Joint intent + slot modeling outperforms sequential pipelines. VocaDine's spaCy-first-then-rule-fallback is a pragmatic approximation — simpler than joint BERT-based models, appropriate for a closed 5-label domain.
→ **Verdict:** Use the ACM survey (doi:10.1145/3547138) rather than this paper — broader and more citable.
→ **URL (survey):** https://dl.acm.org/doi/10.1145/3547138

**[12]** Hechler, S., et al. (2024). "Stupid robot, I want to speak to a human!" User frustration detection in task-oriented dialog systems. *arXiv preprint arXiv:2411.17437*. (Also: COLING 2025 Industry Track)
→ **Design decision:** ImpatienceDetector — VADER + keyword hybrid
→ **Claim:** Frustration detection in task-oriented dialog is an active research problem. LLM-based detection shows 16% F1 improvement over sentiment-based baselines. VocaDine uses VADER + keyword patterns — a lightweight baseline appropriate for real-time prototype constraints.
→ **Verdict:** Excellent. Recent, directly on-topic, lets you honestly frame the limitation: "production-grade frustration detection would use LLM-based classification (Hechler et al. 2024); VADER + keywords is appropriate for prototype scope."
→ **URL:** https://arxiv.org/abs/2411.17437

---

## Citation → Making Of mapping

| Making Of point                                             | Cite                                               |
| ----------------------------------------------------------- | -------------------------------------------------- |
| 40/60 weighting — not arbitrary, justified by rating signal | [3] Ravi & Vairavasundaram 2016                    |
| Phonetic whitelist — solves documented ASR failure          | [6] Kumar et al. 2024                              |
| spaCy NER as slot filling model                             | [10] Weld et al. 2022                              |
| ImpatienceDetector — VADER + keywords, honest about limit   | [2] Hutto & Gilbert 2014, [12] Hechler et al. 2024 |
| Top-3 output limit                                          | [1] Grice 1975                                     |
| Tourism use case relevance                                  | [4] Ukpabi et al. 2019 (optional)                  |
| VADER over deep learning                                    | [5] Abdullah & Ahmet 2022 (optional)               |

---

## Dropped / weak citations

| Citation                  | Why dropped                                                                                |
| ------------------------- | ------------------------------------------------------------------------------------------ |
| [4] Ukpabi et al. 2019    | Only justifies use case framing — not a design decision. Drop if space is tight.           |
| [5] Abdullah & Ahmet 2022 | The VADER-over-DL argument stands without a survey paper. Drop unless reviewer expects it. |
| Grice [1]                 | Keep only if the "Maxim of Quantity → Top-3" framing is stated precisely in the Making Of. |
