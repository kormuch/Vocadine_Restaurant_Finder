# VocaDine — Technisches Briefing für Rückfragen
*Eigene Notizen · nicht zur Abgabe · Stand Mai 2026*

---

## Das Grundprinzip in einem Satz

VocaDine ist ein Sprachassistent: du sprichst hinein, er stellt Rückfragen, und am Ende hört du die drei besten Restaurants vorgelesen — alles auf Englisch, weil die Zielgruppe englischsprachige Touristen in Deutschland sind.

---

## Die 5 wichtigsten Dinge, die ich erklären kann

### 1. Was ist NLU und warum habe ich es trainiert?

**Was es ist:** NLU = Natural Language Understanding. Das ist der Teil des Systems, der versteht, was der User meint. Wenn jemand sagt "I'm looking for cheap Italian food in Berlin for two", muss das System erkennen: Berlin = Stadt, Italian = Küche, cheap = Budget, two = Gruppengrö0e.

**Phase 1:** Das habe ich mit Regeln gemacht. Ich habe Listen mit Wörtern angelegt — wenn "cheap" oder "budget" im Satz steht, ist das Budget = günstig. Das funktioniert auf Beispielen, die ich selbst geschrieben habe, perfekt. Deshalb war F1 = 1.000 — aber das war kein Beleg, dass das System gut ist. Es war ein Beleg, dass ich die Tests auf meine eigenen Regeln zugeschnitten habe.

**Phase 2:** Ich habe stattdessen ein echtes ML-Modell trainiert. Konkret: spaCy NER (Named Entity Recognition). Ich habe 600 Sätze manuell mit Labels versehen — das nennt sich Annotation. Jede Entität (Stadt, Küche, Budget, Diät, Gruppengröße) wurde markiert. Das Modell hat dann gelernt, diese Muster zu erkennen — auch in Sätzen, die es noch nie gesehen hat. Das Ergebnis: Macro-F1 = 0.881 auf 90 Sätzen, die das Modell während des Trainings nie gesehen hat (held-out test set).

**Was ich dazu sagen kann:** "Der Unterschied ist Generalisierung. Regeln funktionieren nur auf dem, was ich erwartet habe. Das trainierte Modell erkennt auch 'somewhere affordable' als Budget, obwohl das Wort nicht in meiner Regelliste stand."

---

### 2. Was bedeuten Precision, Recall und F1?

**Einfache Erklärung:**
- **Precision:** Von allen Dingen, die das System als z.B. "Küche" erkannt hat — wie viele waren wirklich Küchen? (Keine Falschalarm-Rate)
- **Recall:** Von allen echten Küchen im Text — wie viele hat das System gefunden? (Nichts übersehen)
- **F1:** Der Mittelwert aus beiden. Ein System das alles findet aber auch viel Falsches = hoher Recall, niedrige Precision. F1 bestraft beide Extremfälle.

**Warum GROUP_SIZE am schlechtesten (F1 = 0.711)?**
Sätze wie "me and my wife" oder "me and my family" haben keine Zahl drin — man kann sie nicht als Span markieren. Das Modell kann das nicht lernen, weil es keinen Textabschnitt gibt, den man labeln könnte. Dafür gibt es eine separate Regel (family = 4 Personen, partner = 2). Das ist eine bewusste Architekturentscheidung, kein Fehler.

---

### 3. Was ist TF-IDF und wie rankt das System Restaurants?

**Was TF-IDF ist:** Eine Methode, um Text in Zahlen umzuwandeln. Wörter, die in einem Restaurant-Beschreibung häufig vorkommen aber selten in allen anderen Beschreibungen, werden stärker gewichtet. "Vegan" in einer Beschreibung ist wichtiger als "restaurant", das überall steht.

**Wie das Ranking funktioniert:**
```
Score = (Textähnlichkeit × 0.4) + (Google-Bewertung / 5 × 0.6) + Bonuspunkte
```

- Die Textähnlichkeit vergleicht: was der User will vs. was das Restaurant beschreibt
- Die Google-Bewertung ist der Durchschnitt aus hunderten echten Rezensionen
- Bonuspunkte für: Budget passt, Außensitzplätze gewünscht und vorhanden, große Gruppe

**Warum 40/60 und nicht 50/50?** Wenn ein Restaurant nur "restaurant, food" als Beschreibung hat (was bei kleinen Läden vorkommt), ist die Textähnlichkeit wertlos — zu wenig Text. Die Google-Bewertung ist stabiler. 60% Gewicht auf Bewertung = trotzdem gute Ergebnisse auch bei magerer Beschreibung.

**Was ich dazu sagen kann:** "Ich habe bewusst gegen 50/50 entschieden, weil die Qualität der Textbeschreibungen in der Places API stark variiert. Lieber einen gut bewerteten Laden empfehlen als einen zufälligen, weil 'restaurant' im Text steht."

---

### 4. Warum ist das STT-Problem bei deutschen Städten schwer?

**STT** = Speech-to-Text. Ich nutze die Google Web Speech API, die auf Englisch trainiert ist. Das Problem: Deutsche Stadtnamen existieren im englischen Sprachmodell nicht.

- "Haigerloch" → Google hört "Hi girl lock"
- "Tübingen" → "tubing in"
- "Horb am Neckar" → "hope America"

**Meine Lösung:** Eine Whitelist mit 2058+ deutschen Städten und phonetischen Aliasen. Das System prüft nach der STT-Erkennung: gibt es einen bekannten Klangtreffer? "Hi girl" → Haigerloch. Das funktioniert für ~Top 50 Städte zuverlässig.

**Warum nicht einfach deutsches STT nutzen?** Der Tourist spricht Englisch. Ein deutsches STT-Modell würde seinen Akzent und seine englischen Sätze schlechter verstehen als ein englisches.

---

### 5. Was passiert mit den Daten des Users?

Das habe ich bewusst dokumentiert, weil es für ein Tourist-System relevant ist:

- **Audio** geht an Google Cloud (Web Speech API) zur Verarbeitung — Google speichert es laut AGB nicht dauerhaft
- **Standort + Präferenzen** gehen als Suchanfrage an die Google Places API (z.B. "Italian vegan Berlin")
- **Kein dauerhaftes User-Profil** — nach dem Gespräch sind die Slots weg
- **Mikrofon** ist nur aktiv während `recognizer.listen()` — kein Dauerzuhören
- **API-Schlüssel** liegt in einer `.env`-Datei, die nicht im GitHub-Repository ist

---

## Die 3 Entscheidungen, die ich bewusst getroffen habe

**1. pyttsx3 → edge-tts**
pyttsx3 hat in meiner Entwicklungsumgebung (Spyder auf Windows) konsistent Fehler geworfen — COM-Objekt-Fehler, Audio-Treiber-Konflikte. edge-tts nutzt Microsoft Neural Voices, braucht keinen API-Key und hat in keinem Setup Probleme gemacht. Nachteil: braucht Internet. Für einen Touristen-Assistenten akzeptabel.

**2. Top 3 statt alle Ergebnisse**
Google Places liefert bis zu 50 Restaurants. Alle vorlesen = 10 Minuten Zuhören. Ich lese die 3 bestbewerteten und am besten passenden vor. Das nennt sich in der Linguistik "Grice's Maxim of Quantity" — sei so informativ wie nötig, aber nicht mehr.

**3. Bewusste Phase-3-Entscheidungen**
Zwei Probleme habe ich absichtlich nicht gelöst, weil sie zu komplex für Phase 2 sind:
- Shisha-Bars tauchen in türkischen Restaurant-Suchen auf (Google kategorisiert sie falsch) → Phase 3: Typ-Filter
- In Berlin bekommt man Charlottenburg-Empfehlungen obwohl man in Kreuzberg ist → Phase 3: Radius-Suche (3km) via `locationBias`-Parameter der Places API

Das sind keine Fehler, die ich übersehen habe — sie stehen explizit in der Fehleranalyse auf Slide 9.

---

## Was ich über die Bewertung meiner Arbeit sagen kann

Anne Schwerk (meine Tutorin) hat in Phase 2 kritisiert:
- F1 = 1.000 ist kein echtes Ergebnis → ich habe ein ML-Modell trainiert, jetzt 0.881
- Privacy war zu oberflächlich → ich habe Datenflüsse explizit dokumentiert
- TF-IDF-Begründung war ein "Bequemlichkeitsargument" → ich habe die 40/60-Entscheidung sachlich begründet

Ihre positive Rückmeldung: das phonetische Alias-System, das implizite Slot Filling und die Fehleranalyse zeigen "solides ingenieursmäßiges Denken".

---

## Was ich NICHT gemacht habe (und warum das okay ist)

- **Kein LLM (GPT, etc.)** — kein API-Key nötig, deterministisch, erklärbar. Für einen geschlossenen Anwendungsfall mit bekanntem Vokabular übertrieben.
- **Kein Whisper (lokales STT)** — braucht GPU für Echtzeit, zu viel Setup für einen Prototypen
- **Kein dauerhaftes User-Profil / Lernfunktion** — nicht gefordert, wäre DSGVO-relevant
- **Kein deutsches STT** — Zielgruppe spricht Englisch
