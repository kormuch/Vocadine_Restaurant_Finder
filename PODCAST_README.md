# VocaDine — Architektur & Technologie Briefing

## Was ist VocaDine?

Ein sprachgesteuerter Restaurantempfehlungs-Assistent fuer englischsprachige Touristen in Deutschland. Der User spricht per Mikrofon, das System stellt gezielte Fragen, sucht passende Restaurants via Google Places und liest die Empfehlungen vor.

---

## Pipeline-Architektur (End-to-End)

```
Mikrofon → Google Web Speech API (STT) → NLU-Pipeline → Dialog State Manager
    → Google Places API → TF-IDF Ranking Engine → edge-tts (TTS) → Lautsprecher
```

**Latenz**: 6–9 Sekunden End-to-End (dominiert durch API-Calls)

---

## Kernkomponenten im Detail

### 1. Speech-to-Text (STT)

- **Bibliothek**: `speech_recognition` 3.10.4
- **Backend**: Google Web Speech API (en-US)
- **Konfiguration**: `pause_threshold=1.5s`, `phrase_time_limit=15s`, `timeout=7s`
- **Kein API-Key noetig** (kostenlose Google-Variante)
- **Limitation**: Keine Confidence-Scores verfuegbar — niedrige Qualitaet kann nicht automatisch erkannt werden

### 2. NLU-Pipeline (Zweistufig)

#### Stufe 1: Neuronales NER (spaCy)

- **Modell**: Blank English spaCy, trainiert auf 600 annotierten Utterances
- **5 Entity-Labels**: LOCATION, CUISINE, DIET, BUDGET, GROUP_SIZE
- **Datensplit**: 420 Train / 90 Validation / 90 Test (70/15/15, seed=42)
- **Performance** (Held-Out Test): **Macro-F1 = 0.881**
  - LOCATION: F1 = 0.981
  - CUISINE: F1 = 0.925
  - DIET: F1 = 0.971
  - BUDGET: F1 = 0.818
  - GROUP_SIZE: F1 = 0.711 (schwaecher wegen impliziter Ausdruecke)
- **Training**: 40 Epochen, bester Checkpoint bei Epoche 23 (Validation-F1 = 0.97)

#### Stufe 2: Regelbasierter Fallback

- Deckt 5 weitere Slots ab: occasion, datetime, distance, special_features, past_experience
- Keyword-Maps: 20+ Cuisine-Typen, 20+ Budget-Phrasen, 10+ Occasions, Regex fuer Gruppengroesse
- **Phonetische Stadt-Whitelist**: 2058+ deutsche Staedte mit Aliassen (z.B. "tubing" → Tuebingen, "munich" → Muenchen, "cologne" → Koeln)
- **Negations-Erkennung**: "don't like meat" → vegetarisch-Inferenz
- **Ambiguitaets-Erkennung**: ≥2 Cuisines in einem Satz → Klaerungsfrage

### 3. Dialog State Manager (10 Slots)

| Slot | Typ | Strategie |
|------|-----|-----------|
| location | kritisch | Einzelfrage + Validierungsprobe |
| cuisine | kritisch | Einzelfrage + Validierungsprobe |
| past_experience | offen | Freitext nach location/cuisine |
| diet + budget | kritisch | Gepaart gefragt |
| group_size + occasion | optional | Gepaart gefragt |
| datetime + distance | optional | Gepaart gefragt |
| special_features | optional | Einzelfrage (letzte) |

**Dialogstrategie**:
- Offene Eingangsfrage: User kann sofort mehrere Slots gleichzeitig fuellen (2–3 Turns moeglich)
- **Validierungsprobe**: Bei location/cuisine wird die Google Places API vorab angefragt — liefert sie 0 Ergebnisse, wird der Slot zurueckgesetzt und nachgefragt
- **Impatience Detection**: VADER-Sentiment < -0.5 ODER Stop-Keywords ("just search", "stop") → verbleibende Slots werden mit "any" gefuellt, Suche startet sofort

### 4. Recommendation Engine (TF-IDF + Rating)

- **Score-Formel**: `(cosine_similarity * 0.4) + (google_rating/5.0 * 0.6) + Bonusse`
- **TF-IDF**: Berechnet on-demand auf Basis der API-Rueckgaben (Venue-Typen, Beschreibungen)
- **Rationale fuer 40/60 Gewichtung**: Touristen haben kein Lokalwissen — aggregierte Google-Ratings kompensieren fehlendes Insiderwissen
- **Keine vortrainierten Embeddings** (Word2Vec, BERT) — TF-IDF ist transparenter und deterministisch fuer das geschlossene Domaenen-Vokabular

### 5. Text-to-Speech (TTS)

- **Bibliothek**: `edge-tts` 6.1.9 (Microsoft Azure Neural Voices)
- **Stimme**: `en-US-JennyNeural`
- **Ablauf**: Async TTS-Generierung → Temp-MP3 → synchrone Wiedergabe via `pygame.mixer`
- **Warum nicht pyttsx3?** COM-Exceptions unter Windows, clipping bei kurzen Utterances, unreliable Context-Release

---

## Design-Philosophie

### Deterministisch statt LLM-basiert

VocaDine verzichtet bewusst auf Large Language Models (GPT, etc.) fuer:
- **Geschwindigkeit**: Kein LLM-API-Call noetig fuer Intent/Entity-Erkennung
- **Determinismus**: Gleiche Eingabe = gleiches Ergebnis, keine Halluzinationen
- **Sicherheit**: Closed-Domain Slot Filling ist immun gegen Prompt Injection
- **Kosten**: Keine Token-Kosten, keine Rate Limits fuer NLU

### Privacy-First (Zero Persistent Storage)

- Kein Nutzerprofil, keine History, kein Session-Speicher nach Beendigung
- Audio geht an Google Cloud (STT) — wird nicht lokal gespeichert
- Temp-MP3 fuer TTS wird nach Abspielen geloescht
- Vermeidet DSGVO Art. 13 Compliance-Aufwand (bewusste Prototyp-Entscheidung)

### Pragmatische Fehlertoleranz

- Phonetische Aliasse statt Custom-ASR-Modell
- Rule-Based Fallback fuer alles, was NER nicht abdeckt
- Probe-Validation: Testen ob ein Slot ueberhaupt Ergebnisse liefert, bevor er akzeptiert wird
- Graceful Degradation: API-Fehler → "keine Ergebnisse" statt Crash

---

## Tech-Stack Uebersicht

| Komponente | Technologie | Version |
|------------|-------------|---------|
| Sprache | Python | 3.12 |
| STT | speech_recognition + Google Web Speech | 3.10.4 |
| NLU | spaCy (NER) + NLTK (VADER) | ≥3.7 / ≥3.8 |
| Ranking | scikit-learn (TF-IDF + Cosine) | 1.4.0 |
| TTS | edge-tts (Azure Neural Voices) | ≥6.1.9 |
| Audio | pygame + pyaudio | ≥2.5 / 0.2.14 |
| APIs | Google Places v1, Geocoding v1 | — |
| Config | python-dotenv | 1.0.0 |

**Keine Frameworks** (kein Flask, Django, FastAPI) — alles in einer einzigen `main.py`.

---

## Trainingsdaten

- **600 Utterances** (manuell erstellt, spaCy-Format mit Character-Offset Annotationen)
- **Zusammensetzung**: 290 Single-Label + 270 Multi-Label + 40 Adversarial
- **Realistische Tourist-Sprache**: Informelle Formulierungen, simulierte ASR-Fehler ("doona" fuer Doener, "veejin" fuer vegan)
- **Single Annotator** (kein Inter-Annotator Agreement gemessen — dokumentierte Limitation)

---

## Bekannte Limitationen (ehrlich dokumentiert)

1. **Keine STT Confidence Scores** — schlechte Transkription wird nicht automatisch erkannt
2. **GROUP_SIZE schwach** (F1=0.711) — implizite Ausdruecke werden vom Rule-System aufgefangen
3. **Flache Negations-Erkennung** — kein tiefes syntaktisches Parsing
4. **Single Annotator** — Inter-Annotator Agreement κ≥0.85 definiert aber nie formal gemessen
5. **Kein echtes ASR-Trainingsmaterial** — Utterances simulieren Sprachfehler manuell
6. **Feature Sparsity im Ranking** — bei generischen Venue-Typen kollabiert der TF-IDF-Score
7. **Keine DSGVO-Infrastruktur** — Prototyp-Entscheidung, fuer Produktion muesste Art. 13 implementiert werden
8. **Kein Recovery bei Null-Ergebnissen** am Pipeline-Ende

---

## Warum diese Architektur funktioniert (Argumentationshilfe)

**"Warum kein ChatGPT/LLM?"**
→ Closed-Domain Slot Filling braucht kein Sprachmodell. 10 definierte Slots, endliches Vokabular. Determinismus > Kreativitaet. Keine Halluzinationen, keine Prompt Injection, keine Token-Kosten.

**"Warum spaCy statt BERT/Transformer?"**
→ 600 Utterances sind zu wenig fuer Fine-Tuning eines Transformers. SpaCy's CNN-basiertes NER ist fuer kleine Domaenen effizient und schnell (Millisekunden statt Sekunden).

**"Warum TF-IDF statt Sentence Embeddings?"**
→ Domaenen-spezifische Begriffe (Cuisine-Typen, Diaeten) werden von allgemeinen Embeddings schlecht abgebildet. TF-IDF ist transparent, deterministisch und matched exakt auf den zurueckgegebenen Venue-Daten.

**"Macro-F1 von 0.881 — ist das gut genug?"**
→ Fuer einen Prototyp mit 600 Trainingsbeispielen und einem closed-domain Szenario: ja. Die schwachen Labels (GROUP_SIZE, BUDGET) werden vom Rule-System aufgefangen. Das Gesamtsystem ist robuster als der NER-Score allein suggeriert.

**"Vibecoding — wo ist die Eigenleistung?"**
→ Architekturentscheidungen (deterministisch vs. LLM, TF-IDF vs. Embeddings, Probe-Validation, Impatience Detection, phonetische Whitelist) sind konzeptionelle Designentscheidungen. Die Implementierung ist das Werkzeug, das Design ist die Ingenieurleistung. Jede Entscheidung ist begruendet und dokumentiert. Das Making-Of dokumentiert den iterativen Prozess transparent.

---

## Dateistruktur

```
Code/
  main.py                  ← Gesamte Runtime-Logik (STT, NLU, Dialog, API, Ranking, TTS)
  train_nlu.py             ← spaCy NER Training (40 Epochen, Checkpoint-Selection)
  eval_nlu.py              ← NLU-Evaluation (20 Testfaelle, Rule-Based Validation)
  german_cities.py         ← 2058+ Staedte + phonetische Aliasse
  german_cities_list.py    ← Offizielle deutsche Staedteliste
  requirements.txt         ← 9 pip-Pakete
  data/training_data.py    ← 600 annotierte Utterances
  data/annotation_guidelines.md ← Annotationsregeln
  models/vocadine_nlu/     ← Bester spaCy-Checkpoint (Epoche 23)
  sessions/                ← Timestamped Session-Logs

Dokumente/
  design_document.md       ← Architektur, Komponenten, Datenfluss
  making_of.md             ← Designphilosophie, Entscheidungen, Referenzen
  requirements.md          ← 30 funktionale/nicht-funktionale Anforderungen
  dataset_description.md   ← Trainings-Daten-Dokumentation
```

---

## Akademische Referenzen (im Projekt zitiert)

- Kumar et al. (2020) — Conversational AI / Dialogue Systems
- Honnibal & Montani (2017) — spaCy Industrial NLP
- Weld et al. (2022) — Survey of NER Methods
- Hutto & Gilbert (2014) — VADER Sentiment Analysis
- Rasa Open Source — Dialog Management Pattern (als Designreferenz, nicht als Dependency)
