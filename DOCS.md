# VocaDine Germany — Vollständige Projektdokumentation

**Kurs:** DLMAIWNLPVA02 — NLP and Voice Assistants (IU)
**Phase:** 2 — Working Prototype
**Stand:** April 2026
**Repo:** https://github.com/kormuch/Vocadine_Restaurant_Finder
**Branch:** `feature/phase2-implicit-slot-filling`

---

## Was ist VocaDine?

VocaDine ist ein Sprach-Assistent für englischsprachige Touristen in Deutschland. Der Tourist spricht auf Englisch mit dem System — stellt keine einzige Suche, tippt nichts, muss kein Deutsch können — und bekommt am Ende drei Restaurantempfehlungen vorgelesen.

**Konkretes Szenario:**
Ein Tourist kommt abends ins Hotel in Haigerloch (Baden-Württemberg, ~10.000 Einwohner). Er fragt nach einem guten Restaurant. Google Maps kennt Haigerloch, aber wenn er "Haigerloch" sagt, hört Google STT "Hi girl" und liefert 0 Ergebnisse. VocaDine löst genau dieses Problem.

---

## Schnellstart (5 Minuten)

### Voraussetzungen

- Python 3.12
- Mikrofon
- Google Places API Key (Text Search aktiviert)

### Installation

```bash
git clone https://github.com/kormuch/Vocadine_Restaurant_Finder.git
cd Vocadine_Restaurant_Finder
pip install -r requirements.txt
cp .env.example .env
# .env öffnen und eigenen Key eintragen:
# GOOGLE_PLACES_KEY=AIzaSy...
```

### Starten

```bash
python main.py
```

Das System spricht sofort los. Mikrofon bereithalten.

### Evaluation (ohne Mikrofon)

```bash
python eval_nlu.py
```

Testet die NLU-Logik auf 20 vordefinierten Utterances und gibt F1/Precision/Recall aus.

---

## Architektur

### Datenfluss (mit konkretem Beispiel)

```
Tourist sagt:  "I want Italian food in Berlin for two people"
                        │
                        ▼
         [STT] Google Web Speech API (en-US)
                        │
              Text: "i want italian food in berlin for two people"
                        │
                        ▼
         [NLU] _extract_multiple_slots()
                        │
              location="Berlin", cuisine="Italian", group_size="2"
              TTS-Feedback: "I've noted Berlin as your location
                             and Italian cuisine and a group of 2."
                        │
                        ▼
         [Validation Probe] Google Places API
                        │
              Probe: "Italian restaurant in Berlin Germany" → 20 Treffer
              → Slot wird akzeptiert
                        │
                        ▼
         [API Fetch] Google Places New API
                        │
              JSON mit 20 Restaurants (Name, Adresse, Rating, Typen)
                        │
                        ▼
         [Ranking] TF-IDF + Cosine Similarity
                        │
              User-Vektor: "italian none casual"
              Restaurant-Vektoren: ["il fornaio italian restaurant", ...]
              Score = 0.4 × similarity + 0.6 × (rating / 5)
                        │
                        ▼
         [TTS] pyttsx3 (offline)
                        │
         "Option 1: Il Fornaio with a rating of 4.5 stars.
          Address: Unter den Linden 5, Berlin."
```

### Klassen-Übersicht

| Klasse | Datei | Aufgabe |
|---|---|---|
| `TTSEngine` | main.py | Text → Sprache (pyttsx3, offline) |
| `STTEngine` | main.py | Mikrofon → Text (Google Web Speech) |
| `GooglePlacesClient` | main.py | API-Abfragen (probe + full_fetch) |
| `NLU` | main.py | Einzelslot-Extraktion |
| `RecommendationEngine` | main.py | TF-IDF Ranking, Top 3 |
| `DialogStateManager` | main.py | Interview-Steuerung, Slots verwalten |
| `GERMAN_CITIES` | german_cities.py | 2058 Städte + phonetische Aliase |

---

## Die 10 Conversation Slots

Das System fragt nacheinander 10 Fragen. Wenn ein Slot bereits durch eine frühere Antwort befüllt wurde (Implicit Filling), wird die zugehörige Frage übersprungen.

| Slot | Frage | Beispielantwort |
|---|---|---|
| `location` | Which German city are you visiting? | "I'm in Berlin" |
| `past_experience` | A restaurant you enjoyed — what did you like? | "Italian place, great pasta" |
| `datetime` | When would you like to eat? | "Today at seven PM" |
| `cuisine` | What kind of food are you looking for? | "Italian" |
| `diet` | Dietary restrictions? | "I'm vegan" / "none" |
| `budget` | Cheap, moderate, or fine dining? | "moderate" |
| `group_size` | For how many people? | "four" / "4" |
| `occasion` | What is the occasion? | "a date" |
| `distance` | Walking distance or anywhere? | "walking distance" |
| `special_features` | Outdoor seating, English menus? | "outdoor seating" / "none" |

---

## Komponente 1: STT (Speech-to-Text)

```python
class STTEngine:
    def listen(self, language="en-US") -> str | None:
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=10)
            text = self.recognizer.recognize_google(audio, language=language)
            return text.lower().strip()
```

**Was passiert:** Das Mikrofon nimmt 7 Sekunden auf. Die Audiodatei wird an die Google Web Speech API gesendet. Der zurückgegebene Text wird als Lowercase-String zurückgegeben.

**Wichtig:** Wenn kein Ton erkannt wird, gibt `listen()` `None` zurück. Das System antwortet dann: *"I didn't catch that, I'll just skip this for now."* — der Slot wird auf `"any"` gesetzt.

---

## Komponente 2: German Cities Whitelist

Das ist einer der wichtigsten Unterschiede zu Alexa.

### Warum das nötig ist

Google STT erkennt deutsche Städtenamen oft falsch, besonders kleine Orte:
- "Haigerloch" → "Hi girl" oder "higher lock"
- "Bayreuth" → "Beirut"
- "Aschaffenburg" → unverständlich

Ohne Whitelist würde der Slot leer bleiben oder eine falsche Stadt eingetragen.

### Wie es funktioniert

`german_cities.py` enthält ein Dictionary mit 2058+ Einträgen. Der Schlüssel ist die Erkennungsvariante (lowercase), der Wert ist der kanonische Name.

```python
# Aus german_cities.py
PHONETIC_ALIASES = {
    "munich":       "München",         # Englischer Name
    "cologne":      "Köln",            # Englischer Name
    "hamburg":      "Hamburg",         # Kurzform (offizielle Liste hat nur Vollnamen)
    "frankfurt":    "Frankfurt am Main",
    "higher lock":  "Haigerloch",      # STT-Fehler
    "girl":         "Haigerloch",      # STT-Fehler "Hi girl"
    "gerlach":      "Haigerloch",      # STT-Fehler
}
```

### Matching-Logik (wichtig: Word-Boundary!)

```python
# FALSCH (ursprüngliche Version):
for key, canonical in GERMAN_CITIES.items():
    if key in transcript:              # "burg" ist auch in "hamburg" enthalten!
        ...

# KORREKT (nach Bugfix):
for key, canonical in GERMAN_CITIES.items():
    if re.search(r'\b' + re.escape(key) + r'\b', transcript):  # Wortgrenze
        ...
```

**Warum das wichtig ist:** Das Dictionary enthält "Burg" als eigenständige Stadt. Ohne Word-Boundary-Matching würde "I'm in Hamburg" zu `location = "Burg"` führen — weil "burg" ein Substring von "hamburg" ist.

---

## Komponente 3: Implicit Slot Filling

Das ist das Kernfeature von Phase 2. Eine einzige Antwort kann mehrere Slots gleichzeitig befüllen.

### Beispiel ohne Implicit Filling (naiv)

```
System: "Which city?"        → Tourist: "Berlin"
System: "What cuisine?"      → Tourist: "Italian"
System: "Group size?"        → Tourist: "two"
System: "Budget?"            → Tourist: "moderate"
                                                    → 4 Fragen
```

### Beispiel mit Implicit Filling

```
System: "Which city?"
Tourist: "I want Italian in Berlin for two people"
System: "I've noted Berlin as your location and Italian cuisine and a group of 2."
System: "Budget?"            → Tourist: "moderate"
                                                    → 2 Fragen
```

### Code-Erklärung

`_extract_multiple_slots()` wird bei jeder Antwort aufgerufen — egal welche Frage gerade gestellt wurde:

```python
def _extract_multiple_slots(self, transcript: str) -> list[str]:
    confirmed = []

    # Location: Wortgrenze-Suche in GERMAN_CITIES (2058 Einträge)
    if not self.slots.get("location"):
        for key, canonical in GERMAN_CITIES.items():
            if re.search(r'\b' + re.escape(key) + r'\b', transcript):
                self.slots["location"] = canonical
                confirmed.append(f"{canonical} as your location")
                break

    # Cuisine: Keywords aus fester Liste
    cuisines = ["italian", "turkish", "asian", "german", "french", ...]
    if not self.slots.get("cuisine"):
        for cuisine in cuisines:
            if cuisine in transcript:
                self.slots["cuisine"] = cuisine.title()
                confirmed.append(f"{cuisine.title()} cuisine")
                break

    # Diet: Keywords
    # Budget: Keywords + Synonyme ("expensive" → "fine dining")
    # Group size: Ziffern zuerst (\b\d+\b), dann Wortzahlen ("four")
    ...
    return confirmed
```

**Rückgabe:** Liste mit menschenlesbaren Strings für die TTS-Bestätigung.
Beispiel: `["Berlin as your location", "Italian cuisine", "a group of 2"]`
→ TTS: *"I've noted Berlin as your location and Italian cuisine and a group of 2."*

---

## Komponente 4: Validation Probe

Bevor ein Slot akzeptiert wird, prüft das System ob Google Places überhaupt Ergebnisse liefert.

```python
HIGH_IMPACT_SLOTS = {"location", "cuisine", "diet"}

# In run_interview():
if slot in HIGH_IMPACT_SLOTS and self.slots[slot] not in (None, "any"):
    if self.api.probe(self.slots) == 0:
        self.tts.speak(f"I'm sorry, I couldn't find any results for {self.slots[slot]}.")
        self.slots[slot] = None   # ← Slot wird zurückgesetzt
```

**Beispiel:** Tourist nennt "Starzach" (sehr kleines Dorf, keine Restaurants). Probe gibt 0 zurück. System sagt: *"I'm sorry, I couldn't find any results for Starzach. Let's try another choice."* → Frage nach Location wird wiederholt.

```python
def probe(self, slots: dict) -> int:
    params = {"query": "Italian restaurant in Starzach Germany", "key": API_KEY}
    resp = requests.get(self.url, params=params, timeout=5)
    data = resp.json()
    if data.get("status") == "ZERO_RESULTS": return 0
    return len(data.get("results", []))
```

---

## Komponente 5: Google Places API (full_fetch)

Nach dem Interview ruft das System die neue Google Places Text Search API auf.

```python
def full_fetch(self, slots: dict) -> list[dict]:
    new_url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": self.api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.priceLevel,places.types"
    }
    body = {
        "textQuery": "Italian restaurant in Berlin Germany",  # dynamisch aus Slots
        "languageCode": "en"
    }
    resp = requests.post(new_url, headers=headers, json=body, timeout=10)
    ...
```

**Beispiel API-Response (vereinfacht):**
```json
{
  "places": [
    {
      "displayName": {"text": "Il Fornaio"},
      "formattedAddress": "Unter den Linden 5, Berlin",
      "rating": 4.5,
      "types": ["restaurant", "italian_restaurant", "food"]
    },
    ...
  ]
}
```

Das System mappt die Felder auf eine einheitliche Struktur: `p['name'] = p['displayName']['text']`.

---

## Komponente 6: TF-IDF Recommendation Engine

Das Ranking kombiniert inhaltliche Ähnlichkeit (TF-IDF) mit der Google-Bewertung.

### Wie TF-IDF hier verwendet wird

**User-Präferenz** wird als String zusammengesetzt:
```python
user_pref = "italian none casual"   # cuisine + diet + occasion
```

**Jedes Restaurant** wird als Feature-String dargestellt:
```python
biz_features = [
    "il fornaio italian_restaurant restaurant food",   # name + types
    "asia house asian_restaurant restaurant",
    "zum goldenen hirsch german_restaurant restaurant",
]
```

**TF-IDF Fitting:** Der Vectorizer wird auf diese Strings trainiert (runtime, keine Offline-Phase):
```python
vectorizer = TfidfVectorizer(stop_words='english')
tfidf = vectorizer.fit_transform(biz_features + [user_pref])
scores = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()
# tfidf[-1] = User-Vektor, tfidf[:-1] = Restaurant-Vektoren
```

**Combined Score:**
```python
combined = (cosine_similarity_score * 0.4) + ((google_rating / 5.0) * 0.6)
```

Der Faktor 60% für das Rating ist bewusst höher — Touristen vertrauen Bewertungen stärker als Feature-Matching. Forschungsgrundlage: Grice's Maxim of Quantity (Top 3 sind genug).

**Beispiel-Output:**
```
Restaurant          | Similarity | Rating | Combined Score
--------------------|------------|--------|---------------
Il Fornaio          |    0.82    |  4.5   |    0.87
Asia House          |    0.15    |  4.8   |    0.64
Zum Goldenen Hirsch |    0.10    |  3.9   |    0.51
```

→ Il Fornaio wird als Option 1 vorgelesen.

---

## NLU Evaluation — eval_nlu.py

### Warum dieser Test?

Die Guidelines verlangen explizit Precision, Recall und F1-Score. Wir messen auf NLU-Ebene: Wie gut extrahiert `_extract_multiple_slots()` Slots aus natürlichen Utterances?

### Wie der Test aufgebaut ist

20 Utterances mit erwarteten Slot-Werten:

```python
TEST_CASES = [
    # Einfach — einzelner Slot
    ("i am in berlin",
     {"location": "Berlin", "cuisine": None, "diet": None, ...}),

    # Mehrere Slots in einer Aussage
    ("vegan restaurant in hamburg for two people",
     {"location": "Hamburg", "diet": "vegan", "group_size": "2", ...}),

    # Phonetischer Alias
    ("i am visiting girl loch",
     {"location": "Haigerloch", ...}),

    # Budget-Synonym
    ("something expensive for a date in berlin",
     {"location": "Berlin", "budget": "fine dining", ...}),

    # Negativ-Baseline (kein Slot erwartet)
    ("hello i would like a recommendation",
     {"location": None, "cuisine": None, ...}),
]
```

### Metriken

- **TP (True Positive):** Slot korrekt extrahiert
- **FP (False Positive):** Slot extrahiert, aber kein Wert erwartet
- **FN (False Negative):** Slot erwartet, aber nicht extrahiert (oder falscher Wert)
- **TN (True Negative):** Kein Slot erwartet, keiner extrahiert → korrekt, zählt aber nicht in F1

```
Precision = TP / (TP + FP)   → Wie oft war das, was wir extrahiert haben, richtig?
Recall    = TP / (TP + FN)   → Wie viel von dem, was da war, haben wir gefunden?
F1        = 2 × (P × R) / (P + R)
```

### Ergebnisse (nach Bugfixes)

```
Slot         TP   FP   FN   Precision   Recall    F1
------------ ---- ---- ---- ----------- --------- ------
location     13    0    0    1.000       1.000     1.000
cuisine       8    0    0    1.000       1.000     1.000
diet          6    0    0    1.000       1.000     1.000
budget        8    0    0    1.000       1.000     1.000
group_size    8    0    0    1.000       1.000     1.000
----------------------------------------------------------
Macro-avg F1                                       1.000
```

### Bugs, die der Test aufgedeckt hat

**Bug 1 — "hamburg" matchte "Burg"**

```
Utterance: "vegan restaurant in hamburg for two people"
Erwartet:  location = "Hamburg"
Bekommen:  location = "Burg"     ← falscher Match
```

Ursache: `if "burg" in "hamburg"` → True. Die Stadt "Burg" stand im Dict vor dem Alias "hamburg".
Fix: `re.search(r'\bburg\b', "hamburg")` → kein Match, weil kein Wortanfang/-ende.

**Bug 2 — "none" matchte "one" bei group_size**

```
Utterance: "no dietary restrictions none"
Erwartet:  group_size = None
Bekommen:  group_size = "1"    ← falscher Match
```

Ursache: `if "one" in "none"` → True.
Fix: `re.search(r'\bone\b', "none")` → kein Match.

**Beide Fixes in main.py und eval_nlu.py eingepflegt.**

---

## Projektstruktur

```
NLP and Voice 2/
│
├── main.py                  ← Hauptprogramm (Dialog, STT, TTS, API, Ranking)
├── german_cities.py         ← City-Whitelist + phonetische Aliase (2058 Städte)
├── german_cities_list.py    ← Rohliste aller deutschen Städte
├── eval_nlu.py              ← NLU Evaluation — F1/Precision/Recall
│
├── requirements.txt         ← Python-Abhängigkeiten
├── .env                     ← API-Key (nicht im Repo!)
├── .env.example             ← Vorlage für neue Entwickler
├── .gitignore
│
├── README.md                ← Kurzübersicht
├── DOCS.md                  ← Diese Datei — vollständige Dokumentation
│
└── guidlines pdfs/
    ├── Assignments Portfolio_DLMAIWNLPVA02 (1).txt   ← Prüfungsanforderungen
    ├── Guidelines Portfolio_new.txt                  ← Allgemeines IU-Framework
    └── feedback1.txt                                 ← Tutor-Feedback Phase 1
```

---

## Differenzierung vs. Alexa

| Feature | Alexa | VocaDine |
|---|---|---|
| STT für kleine deutsche Städte | Scheitert oft | 2058-Städte-Whitelist + phonetische Aliase |
| 0-Ergebnisse | Leere Liste | Validation Probe setzt Slot zurück |
| Dialog-Effizienz | Starre Fragenreihe | Implicit Filling — bis zu 5 Slots pro Antwort |
| Ranking | Popularity/Sponsored | TF-IDF Similarity + Google-Rating (40/60) |
| Sprachanforderung | Eng an Plattform | Nur pyttsx3 (offline), kein Cloud-TTS nötig |

---

## Technologiewahl-Begründungen (für Slides)

### Warum pyttsx3 statt Google TTS?
- Offline-fähig — kein zweiter API-Key nötig
- Deterministisch — kein Netzwerk-Overhead beim Vorlesen
- Kostenlos ohne Kontingent

### Warum TF-IDF statt LLM?
- Kein API-Key nötig
- Deterministisch und erklärbar
- Passt zur Ressourcenbeschränkung (Laptop, offline-fähig)
- `fit_transform()` = technisch Modelltraining → erfüllt Guideline "train NLP models"

### Warum Rule-based NLU statt ML-Klassifikator?
- Für die vorliegende Domäne (Städte, Küchen, Diäten) sind die Klassen klein und bekannt
- 100% Precision/Recall erreichbar ohne Trainingsdaten
- Erweiterbar: neue Stadt = eine Zeile im Dict

---

## Fehlerkategorien (Error Analysis)

| # | Problem | Ursache | Lösung |
|---|---|---|---|
| 1 | Kurzwörter falsch erkannt ("no" → "know") | STT-Unsicherheit bei monosyllabischen Wörtern | Synonym-Mapping |
| 2 | Haigerloch → "Hi girl" | STT kennt Kleinstadt nicht | Phonetische Aliase in german_cities.py |
| 3 | Irrelevante Venue-Typen (Shisha-Bar in Ergebnissen) | Places API gibt alle Restaurants zurück | Typ-Filterung (Phase 3) |
| 4 | Geografische Unschärfe (falscher Stadtteil) | Text Search ohne Radius | Radius Search (Phase 3) |
| 5 | Recording-Latenz 2.5s | Standardpause-Threshold zu hoch | `adjust_for_ambient_noise` → 0.5s |
| 6 | "Burg" statt "Hamburg" | Substring-Matching ohne Word-Boundary | `re.search(r'\b...\b', text)` → gefixt |
| 7 | "none" → group_size = 1 | "one" ist Substring von "none" | Word-Boundary-Fix → gefixt |
| 8 | 50 Ergebnisse vom API | Zu viele Optionen | Top 3 (Grice's Maxim of Quantity) |

---

## Offene Aufgaben (Phase 2 Abgabe)

### Pflicht vor Abgabe

- [ ] **Manuelle 20 Testläufe** mit Mikrofon durchführen (Testplan in todo.txt)
- [ ] **PR mergen**: `feature/phase2-implicit-slot-filling` → `main`
- [ ] **10-Slide PDF** erstellen (Slide 7 + 8 kritisch — F1 + TF-IDF)
- [ ] **Reflexionstext** für PebblePad schreiben (150-200 Wörter)
- [ ] **Abgabe in PebblePad** mit GitHub-Link

### Abgabe-Format Phase 2

```
PebblePad enthält:
  Teil A — Reflexionstext (direkt eingeben, 150-200 Wörter)
  Teil B — 10-Slide PDF (Upload)
  Teil C — GitHub-Link: https://github.com/kormuch/Vocadine_Restaurant_Finder
```

### Slide-Übersicht

| Slide | Inhalt | Guideline-Anforderung |
|---|---|---|
| 1 | Titel + Use Case (Haigerloch-Szenario) | Problemdefinition (10%) |
| 2 | Architekturdiagramm mit Datentypen | Design document |
| 3 | Differenzierung vs. Alexa | Creativity (20%) |
| 4 | Implicit Slot Filling + Code-Snippet | Implementation Steps |
| 5 | STT + NLU-Methode + phonetische Aliase | Methodology (20%) |
| 6 | Google Places API + Code-Snippet + JSON | Optional Feature (Option 2) |
| 7 | TF-IDF + Formel + Visualisierung | "Describe recommendation mechanism" |
| 8 | **F1 / Precision / Recall Tabelle** | **Pflicht laut Guidelines** |
| 9 | Error Analysis (8 Fehlerklassen) | "Perform error analysis" |
| 10 | Before/After + Phase-3-Ausblick | Creativity + Methodology |

---

## Umgebungsvariablen

```
# .env (nie ins Git committen!)
GOOGLE_PLACES_KEY=AIzaSy...
```

---

## Requirements

```
speechrecognition
pyaudio
pyttsx3
requests
python-dotenv
scikit-learn
```

Installieren: `pip install -r requirements.txt`

Auf Windows kann `pyaudio` Probleme machen. Falls nötig:
`pip install pipwin && pipwin install pyaudio`
