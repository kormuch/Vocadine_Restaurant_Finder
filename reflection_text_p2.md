# Reflection Text — Phase 2
# VocaDine Germany · DLMAIWNLPVA02
# Korbinian Much · April 2026
# (150–200 words · for PebblePad Part A · paste directly into text field)

---

Phase 2 centred on two parallel workstreams: building a working voice pipeline and replacing the rule-based NLU with a genuinely trained model.

The core technical risk was the NLU evaluation problem identified in the Phase 1 feedback: a rule-based system tested on utterances it was designed for produces perfect metrics that prove nothing. To address this, I manually annotated 600 domain utterances across five entity labels, trained a blank spaCy NER model over 40 epochs, and evaluated it on a held-out test set of 90 utterances — yielding Macro-F1 = 0.881. This replaced the misleading F1 = 1.000 figure with an honest generalisability measure.

A second risk was dependency stability: pyttsx3 failed consistently in the Spyder/IPython environment. Switching to edge-tts resolved this with the added benefit of neural voice quality at no API cost.

The main resource constraint was annotation time. Building 600 labelled examples manually took longer than expected, but the resulting model demonstrates measurable generalisation — recognising unseen phrasings the rule layer would have missed.

Open issues — venue type filtering and geographic radius search — are deferred to Phase 3 by design, not oversight.
