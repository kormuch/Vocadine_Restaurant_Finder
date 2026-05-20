# Final Product — VocaDine
**Much, Korbinian | IU14127772 | DLMAIWNLPVA02 | Phase 3**

---

## Product

VocaDine is a voice-based restaurant finder for English-speaking tourists in Germany. The user interacts exclusively via voice. The system collects preferences through a conversational dialog, queries live restaurant data via the Google Places API, ranks results using a hybrid TF-IDF and rating-based scoring formula, and reads the top 3 recommendations aloud via neural text-to-speech.

---

## GitHub Repository

https://github.com/kormuch/Vocadine_Restaurant_Finder

The repository contains all source code, training data, trained NER model, evaluation results, and documentation.

---

## Key Files

| File | Description |
|---|---|
| `main.py` | Full voice assistant — run this to start VocaDine |
| `german_cities.py` | Phonetic alias whitelist for 2058+ German cities |
| `train_nlu.py` | spaCy NER training script |
| `eval_nlu.py` | NER evaluation on held-out test set |
| `data/training_data.py` | 600 annotated utterances |
| `data/annotation_guidelines.md` | Annotation rules and label definitions |
| `models/vocadine_nlu/` | Trained spaCy NER model (best checkpoint, epoch 23) |

---

## Performance

| Metric | Value |
|---|---|
| NER Macro-F1 (90 held-out utterances) | 0.881 |
| Task completion rate | 90% (18/20 sessions) |
| Local processing latency (STT → TTS start) | ~1.8s |
| End-to-end latency (mic open → result heard) | ~6–9s |

---

## Setup

See `04-Finished voice assistant/README_user.md` for installation and run instructions.
