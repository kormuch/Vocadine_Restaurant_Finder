# Dataset Description — VocaDine NER Training Data
**Much, Korbinian | IU14127772 | DLMAIWNLPVA02**

---

## 1. Purpose

This dataset was created to train a named entity recognition (NER) model for VocaDine — a voice-based restaurant finder for English-speaking tourists in Germany. The model extracts user preferences from natural language utterances produced by automatic speech recognition (ASR). All utterances reflect the conversational register of spoken language: informal phrasing, incomplete sentences, and ASR noise patterns.

---

## 2. Dataset Summary

| Property | Value |
|---|---|
| Total utterances | 600 |
| Entity labels | 5 (LOCATION, CUISINE, DIET, BUDGET, GROUP_SIZE) |
| Language | English |
| Domain | Restaurant preference elicitation |
| Format | spaCy training format (`Example` objects via `make_example()`) |
| Source file | `data/training_data.py` |
| Annotation guidelines | `data/annotation_guidelines.md` |

---

## 3. Composition

| Category | Count | Description |
|---|---|---|
| Single-label utterances | 290 | Each utterance contains exactly one entity span |
| Multi-label utterances | 270 | 2–4 entity spans per utterance |
| Adversarial / edge cases | 40 | Negations, ASR noise, ambiguous phrasing, empty annotations |
| **Total** | **600** | |

Multi-label utterances reflect realistic user input: "Italian food for two in Munich, nothing too fancy" contains CUISINE, GROUP_SIZE, LOCATION, and BUDGET in a single sentence. These are critical for training implicit slot filling behaviour.

---

## 4. Entity Labels

| Label | Definition | Example span |
|---|---|---|
| LOCATION | German city the user is in or travelling to | "Berlin", "Munich", "Tübingen" |
| CUISINE | Food type or culinary tradition requested | "Italian", "sushi", "traditional German" |
| DIET | Dietary restriction or lifestyle preference | "vegan", "gluten-free", "halal" |
| BUDGET | Price range preference | "cheap", "fine dining", "tight budget" |
| GROUP_SIZE | Number of people dining | "four", "two of us", "six" |

Slots outside these 5 labels (occasion, datetime, distance, special_features) are not handled by the NER model — they are covered by the rule-based fallback layer.

---

## 5. Data Split

| Split | Size | Proportion | Purpose |
|---|---|---|---|
| Train | 420 | 70% | Model weight updates |
| Validation | 90 | 15% | Per-epoch F1 for checkpoint selection |
| Test | 90 | 15% | Final held-out evaluation (run once) |

Split is deterministic: `random.seed(42)` in `split_data()` (`data/training_data.py`). The test set was never used during training or checkpoint selection — it was evaluated once after the best model was selected by validation F1.

---

## 6. Annotation Process

Utterances were written and annotated manually by the project author. The annotation process followed the guidelines in `data/annotation_guidelines.md`, which defines:

- Span boundary rules (minimal meaningful span, no surrounding articles)
- Per-label definitions with positive and negative examples
- Edge case handling (ASR noise, overlapping spans, negations)
- Quality checks: `make_example()` warnings indicate span mismatches

Utterances were designed to reflect realistic tourist speech patterns, including:
- Informal phrasing ("something cheap", "not too fancy")
- ASR-like noise ("doona" for Döner, "veejin" for vegan)
- Relationship-based group size ("me and my wife", "me and three friends")
- Compound budget expressions ("nothing too expensive", "we're counting pennies")

---

## 7. Scope and Limitations

The dataset covers the common case well. Known limitations:

- **Edge case coverage is limited by annotation cost.** Robust coverage of regional language variation, professional restaurant vocabulary, and complex multi-clause utterances would require domain expert annotation at significantly larger scale. These cases fall through to the rule-based fallback layer.
- **GROUP_SIZE is the weakest label** (F1 = 0.711). Implicit expressions ("me and my wife", "just the two of us") are not annotatable as NER spans and are handled by rule-based patterns instead.
- **No real ASR output used.** All utterances were written to simulate ASR output. Adversarial examples approximate noise but do not cover the full distribution of real transcription errors.
- **Single annotator.** Inter-annotator agreement (target κ ≥ 0.85) was defined in the guidelines but not formally measured due to prototype scope.

---

## 8. Evaluation Results (held-out test set, 90 utterances)

| Label | Precision | Recall | F1 | TP | FP | FN |
|---|---|---|---|---|---|---|
| LOCATION | 0.963 | 1.000 | 0.981 | 26 | 1 | 0 |
| CUISINE | 0.878 | 0.977 | 0.925 | 43 | 6 | 1 |
| DIET | 0.944 | 1.000 | 0.971 | 17 | 1 | 0 |
| BUDGET | 0.783 | 0.857 | 0.818 | 18 | 5 | 3 |
| GROUP_SIZE | 0.640 | 0.800 | 0.711 | 16 | 9 | 4 |
| **Macro** | **0.842** | **0.927** | **0.881** | | | |

Validation F1 peaked at 0.97 at epoch 23 — this is the checkpoint-selection signal and is optimistic by design. The test F1 of 0.881 on the fully held-out set is the honest performance metric.
