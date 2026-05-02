# Was meint der Kurs mit „Train NLP Models"?
Analyse auf Basis von Skript DLMAIWNLPVA01 + Assignment Portfolio DLMAIWNLPVA02

---

## 1. Die exakte Anforderung (Assignment Portfolio, Zeile 28)

> "Implementation Steps: **Setup frameworks, collect training data, train NLP models**, and perform error analysis."

Das sind vier explizite Schritte — kein „oder", kein „z.B.". Alle vier sollen in den Slides dokumentiert sein.

Zusätzlich aus der **Mandatory Documentation Checklist** (Phase 3):
- `[ ] Data annotation guidelines (labeling process)` → explizit verlangt
- `[ ] Dataset description (voice samples, transcripts)` → explizit verlangt

---

## 2. Was das Skript unter „Training" versteht

### Kapitel 1.4 — Training, Validation, and Test Set (Skript, S. 30)

> "During training, a portion of the training set is **iteratively used as input to the model**, and based on a comparison between the model output and the **labels** in the training set, the **model parameters are iteratively adjusted** with the goal of minimizing the deviation."

→ Das ist klassisches supervised ML: gelabelte Daten → Modell lernt → Parameter werden angepasst.

> "Often the division is **80% training, 10% validation, 10% test**."
> "The samples in the test set are **unseen**, i.e., have not been used during training."

→ Klarer Anspruch: Trainingsdaten ≠ Testdaten. Ein System, das auf denselben Utterances evaluiert wird, die es implizit kennt (weil regel-basiert auf sie ausgerichtet), erfüllt das nicht.

---

## 3. Das Referenzmodell im Skript — Rasa (Skript, S. 88–89)

Das Skript beschreibt ausführlich, wie Chatbot-NLU laut Kurs aussehen soll:

> "Chatbots can also be built using **statistical methods**, in which **machine learning techniques are employed to train the chatbot with example conversations** to produce the desired behavior. An example of this approach is **Rasa**."

**Zwei konkrete Trainingsschritte, die Rasa macht:**

### Schritt 1: Intent Classification
```
## intent:greet
- hello
- good morning
- hey

## intent:mood_negative
- bad
- not so good
- i am feeling unhappy
```
> "The input feature of our models is the text input of the user, and the **output feature is one of the labels**. [...] we have mapped the problem to a **text classification task**."

→ Gelabelte Utterances → trainierter ML-Classifier.

### Schritt 2: Dialog Management
> "The dialog management model is **trained on sample conversations called 'stories'** that show the bot what actions are most likely to follow a certain intent."
> "The dialog management module uses a sequence of intents as input and is **trained to predict the next action**."

---

## 4. Was das Skript als Slot Filling einordnet

> "Chatbots can also **extract specific information from the user's input**, such as location, dates, or names, for example, in hotel or train booking dialog systems. This is a **named entity recognition task**, which is called **slot filling** in the context of chatbots."

→ Slot Filling = NER-Aufgabe. Der Kurs erwartet, dass das als NER behandelt wird — also mit gelabelten Daten, nicht nur mit Regex + Dict-Lookup.

---

## 5. Die empfohlenen Tools (Methodology/Ideas — 20% der Note)

Aus dem Assignment Portfolio:
> "Appropriateness of tools (e.g., **Mycroft, Snips, TensorFlow, PyTorch**)."

Mycroft und Snips sind vollständige Voice-Assistant-Frameworks mit eingebautem ML-Training für Intent Classification und NER. Das ist der explizite Referenzrahmen für „Methodology/Ideas".

---

## 6. Was VocaDine aktuell macht — und wo die Lücke liegt

| Was der Kurs erwartet | Was VocaDine macht | Lücke |
|---|---|---|
| ML-basierter Intent Classifier (trainiert auf gelabelten Utterances) | Regel-basiertes NLU (Dict-Lookup + Regex) | Kein Training |
| Labeled training dataset (80/10/10 Split) | 20 Utterances für Evaluation, kein echter Split | Training = Test |
| Slot Filling als NER-Aufgabe | Regex-Pattern auf bekannten Keywords | Kein ML |
| `fit_transform()` auf Restaurantdaten | `fit_transform()` auf 3–5-Wort-Strings (name + types) | Kein semantisches Training |
| Unseen test set | Testset wurde manuell auf regelbasiertes System zugeschnitten | Kein echter Generalisierungstest |

---

## 7. Die zwei Wege laut Professoren-Feedback

### Weg A — Ehrliche Einschränkung kommunizieren (minimal, aber redlich)
In den Slides explizit schreiben:
- "NLU is rule-based by design — closed-domain slot filling does not require ML training"
- "TF-IDF fit_transform at runtime is technically model fitting, but lightweight — richer approaches (embeddings, fine-tuned classifiers) were out of scope for this prototype"
- F1=1.000 als "on curated, rule-consistent test set" rahmen, nicht als Generalisierungsbeleg

### Weg B — NLP-Komponente wirklich stärken (tatsächliches Training)

**Option B1: sklearn Intent Classifier (einfachste echte Lösung)**
- Die 20 Utterances aus `eval_nlu.py` + 30–40 neue annotieren
- TF-IDF + LogisticRegression oder Naive Bayes als Intent/Slot-Classifier trainieren
- 70/15/15 Split → echter Train/Val/Test-Zyklus
- Ergebnis: „Wir trainieren einen ML-Classifier auf annotierten Utterances" — das ist glaubwürdig

**Option B2: Review-Texte als Feature (für den Recommendation-Teil)**
- Google Places API liefert `reviews[].text` → als Restaurant Feature String statt nur `name + types`
- Dann ist TF-IDF auf echtem Fließtext → semantisch sinnvoll, nicht nur Keyword-Overlap
- Ändert nur den Feature String in `RecommendationEngine`, kein großer Aufwand

**Option B3: spaCy NER für Slot Filling**
- `en_core_web_sm` laden (pre-trained, kein API Key nötig)
- NER-Output als Ergänzung zu Regex (Location, Person, Date, etc.)
- Im Slide: „We use spaCy's pre-trained NER as a foundation and extend it with domain-specific rules"
- Das ist methodisch stärker, auch wenn es kein eigenes Training ist

---

## 8. Empfehlung für VocaDine Phase 2

**Kurzfristig (Slides ohne Code-Änderung):**
- Weg A umsetzen: Einschränkungen transparent kommunizieren
- TF-IDF als "lightweight runtime fitting on live data" positionieren, Limitation ehrlich benennen
- F1=1.000 als "on rule-consistent curated test set — not a generalization benchmark" rahmen

**Mittelfristig (wenn noch Code-Änderung möglich):**
- Option B2 (Reviews als Feature) ist mit ~10 Zeilen Code machbar und stärkt den Recommendation-Teil erheblich
- Dann ist der TF-IDF tatsächlich auf bedeutungsvollem Text und die Begründung hält

---

## 9. Relevante Zitate aus dem Skript (für Slides / Reflexion)

| Zitat | Ort | Nutzbar für |
|---|---|---|
| "machine learning techniques are employed to train the chatbot with example conversations" | S. 88 | Begründung warum rule-based ein Kompromiss ist |
| "This is a named entity recognition task, which is called slot filling" | S. 89 | Theoretische Einordnung von NLU/Slot Filling |
| "the model parameters are iteratively adjusted with the goal of minimizing the deviation" | S. 30 | Definition Training → zeigt, warum fit_transform das nicht ist |
| "80% training, 10% validation, 10% test — samples in the test set are unseen" | S. 30 | Begründung für Limitationen der aktuellen Evaluation |
