# VocaDine — Testscript (20 Runs)
**Zweck:** Dokumentation echter Testruns für Phase 2 Evaluation (Task Completion, Latenz, STT-Qualität)
**Vorgehen:** Jeden Run starten, Sätze laut vorlesen, Ergebnis im Log festhalten.

> Standardfälle zuerst (Run 01–12), Edge Cases am Ende (Run 13–20).

---

## Standardfälle

---

### Run 01 — Einfach, eine große Stadt, eine Cuisine
**Erwartetes Ergebnis:** location + cuisine erkannt, alle anderen Slots abgefragt, Empfehlung geliefert.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"I'm looking for Italian food in Berlin."* |
| past_experience | *"I really enjoyed a cozy pasta place with dim lighting."* |
| diet | *"none"* |
| budget | *"moderate"* |
| group/occasion/special | *"Two people, casual dinner, no special requirements."* |

---

### Run 02 — Multi-Slot in einer Utterance
**Erwartetes Ergebnis:** Mindestens 4 Slots aus der ersten Utterance extrahiert, wenige Folgefragen.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"I want vegan Thai food in Munich for three people, something cheap."* |
| past_experience | *"Last time I loved a small street food place."* |
| occasion/special | *"casual, no special requirements"* |

---

### Run 03 — Hamburg, Japanisch, Fine Dining
**Erwartetes Ergebnis:** Alle Pflichtslots sauber erkannt.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"Japanese restaurant in Hamburg please."* |
| past_experience | *"I enjoyed a sushi place with great sake selection."* |
| diet | *"no restrictions"* |
| budget | *"fine dining"* |
| group/occasion/special | *"just me, business dinner, private room if possible"* |

---

### Run 04 — Negation bei Diet
**Erwartetes Ergebnis:** diet = "none" korrekt erkannt trotz Negation.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"Looking for a Greek restaurant in Cologne."* |
| past_experience | *"I liked a taverna with live music once."* |
| diet | *"I have no dietary restrictions at all."* |
| budget | *"moderate"* |
| group/occasion/special | *"four people, casual, outdoor seating"* |

---

### Run 05 — Zahlwort statt Ziffer
**Erwartetes Ergebnis:** group_size = 6 aus "six" erkannt.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"German food in Frankfurt."* |
| past_experience | *"I had a great schnitzel last time."* |
| diet | *"vegetarian"* |
| budget | *"cheap"* |
| group/occasion/special | *"six people, birthday dinner"* |

---

### Run 06 — Köln, Türkisch, Immer-Günstig
**Erwartetes Ergebnis:** Budget-Synonym "budget friendly" → cheap.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"I'm in Cologne looking for Turkish food, something budget friendly."* |
| past_experience | *"I loved a kebab place with fresh bread."* |
| diet | *"halal"* |
| group/occasion/special | *"two people, casual, nothing special"* |

---

### Run 07 — Stuttgart, Indisch, Gruppe
**Erwartetes Ergebnis:** Alle Slots sauber, 50 Venues gecheckt, Top 3 geliefert.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"Indian restaurant in Stuttgart for eight people."* |
| past_experience | *"I enjoyed a curry place with great naan bread."* |
| diet | *"none"* |
| budget | *"moderate"* |
| occasion/special | *"family dinner, no special requirements"* |

---

### Run 08 — Düsseldorf, Chinesisch, Romantisch
**Erwartetes Ergebnis:** occasion = "date" korrekt erkannt.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"Chinese restaurant in Düsseldorf."* |
| past_experience | *"I loved a dim sum place with great atmosphere."* |
| diet | *"gluten-free"* |
| budget | *"fine dining"* |
| group/occasion/special | *"two people, romantic date, indoor seating"* |

---

### Run 09 — Nuremberg, Mexikanisch
**Erwartetes Ergebnis:** Nürnberg erkannt, Mexican cuisine.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"Mexican food in Nuremberg."* |
| past_experience | *"I liked a place with good guacamole and margaritas."* |
| diet | *"none"* |
| budget | *"cheap"* |
| group/occasion/special | *"five people, casual, outdoor"* |

---

### Run 10 — Vollständige Utterance, Kaum Folgefragen
**Erwartetes Ergebnis:** Maximal 1–2 Folgefragen.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"I'm in Berlin looking for a moderate Italian restaurant for two people tonight, I'm vegan."* |
| past_experience | *"I enjoyed a nice pizza place with wood-fired oven."* |
| special | *"no special requirements"* |

---

### Run 11 — Kleine Stadt, Gut Ausgesprochen
**Erwartetes Ergebnis:** Haigerloch korrekt erkannt ohne phonetischen Fehler.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"Restaurant in Haigerloch."* |
| past_experience | *"Something cozy, like the last place I visited."* |
| diet | *"none"* |
| budget | *"moderate"* |
| group/occasion/special | *"just me, casual"* |

---

### Run 12 — "Surprise me" — Indifferenz
**Erwartetes Ergebnis:** Alle offenen Slots werden auf "any" gesetzt, sofortige Suche.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"Restaurant in Munich."* |
| past_experience | *"I don't know, anything is fine."* |
| diet | *"surprise me"* |

---

## Edge Cases

---

### Run 13 — Phonetischer STT-Fehler: Haigerloch
**Zweck:** Phonetischer Alias funktioniert bei schlechter Aussprache.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"I'm in Hi girl loch looking for a burger place."* |
| past_experience | *"I liked a diner with crispy fries."* |
| diet | *"none"* |
| budget | *"moderate"* |
| group/occasion/special | *"alone, casual"* |

---

### Run 14 — Phonetischer STT-Fehler: Tübingen
**Zweck:** "tubing in" → Tübingen.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"I'm visiting Tübingen, looking for Italian food."* |
| past_experience | *"I liked a place near a river."* |
| diet | *"vegetarian"* |
| budget | *"moderate"* |
| group/occasion/special | *"two people, casual"* |

---

### Run 15 — Ambiguität: Zwei Cuisines
**Zweck:** _detect_ambiguity() greift ein, System fragt nach.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"I'm in Berlin, looking for Italian or maybe Greek food."* |
| Klärungsfrage | *(System fragt welche) → "Italian please."* |
| past_experience | *"I enjoyed a Mediterranean place once."* |
| diet | *"none"* |
| budget | *"moderate"* |
| group/occasion/special | *"two, casual"* |

---

### Run 16 — Ungeduld: VADER greift ein
**Zweck:** ImpatienceDetector setzt alle Slots auf "any", sofortige Suche.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"Restaurant in Hamburg."* |
| past_experience | *"Stop asking me so many questions, just find something!"* |

**Erwartetes Ergebnis:** System erkennt Ungeduld, sucht sofort ohne weitere Fragen.

---

### Run 17 — Unbekannte Stadt
**Zweck:** Validation Probe schlägt fehl, System fragt erneut nach.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"I'm in Blorptville looking for Italian food."* |
| Retry | *(System fragt nochmal) → "I'm in Berlin."* |
| Weiter normal | *(restliche Slots normal befüllen)* |

---

### Run 18 — Gruppengrößen-Edge-Case: Familie
**Zweck:** "me and my family" → group_size = 4.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"Italian restaurant in Munich."* |
| past_experience | *"I liked a family-friendly place with a kids menu."* |
| diet | *"none"* |
| budget | *"moderate"* |
| group/occasion/special | *"me and my family, casual dinner"* |

---

### Run 19 — 0 API-Ergebnisse in kleiner Stadt
**Zweck:** Validation Probe → kein Ergebnis → Slot wird zurückgerollt.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"Vegan fine dining in Haigerloch."* |
| *(System rollt zurück)* | *"Okay, let's try moderate budget then."* |
| Weiter normal | *(restliche Slots normal befüllen)* |

---

### Run 20 — Alles auf einmal, Dense Multi-Slot
**Zweck:** Maximale Slot-Dichte in einer Utterance, minimale Folgefragen.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"I'm in Frankfurt, looking for gluten-free Chinese fine dining for two people tonight, it's a romantic date and I'd love outdoor seating."* |
| past_experience | *"I had an amazing Peking duck last time."* |

**Erwartetes Ergebnis:** location, cuisine, diet, budget, group_size, datetime, occasion, special_features — alle aus 1–2 Utterances.

---

### Run 21 — Diet-Inferenz: Fleisch positiv erwähnt
**Zweck:** past_experience enthält Fleisch-Keyword ohne Negation → diet = "none" wird automatisch gesetzt, Frage übersprungen.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"Italian restaurant in Berlin."* |
| past_experience | *"I really loved the meatballs and the steak there."* |
| *(diet-Frage sollte übersprungen werden)* | |
| budget | *(kommt direkt)* → *"moderate"* |
| group/occasion | *"two people, casual"* |

**Erwartetes Ergebnis:** diet-Frage wird nicht gestellt, diet=none im Hintergrund gesetzt.

---

### Run 22 — Diet-Inferenz: Fleisch mit Negation (bekannter Edge Case)
**Zweck:** "they served meat and I don't like meat" → Inferenz schlägt fehl → System fragt trotzdem nach diet.

| Slot | Was du sagst |
|---|---|
| Offene Frage | *"Restaurant in Munich."* |
| past_experience | *"They served meat and I don't like meat, I prefer vegetables."* |
| *(diet-Frage sollte trotzdem kommen)* | → *"vegetarian"* |
| budget | *"moderate"* |
| group/occasion | *"alone, casual"* |

**Erwartetes Ergebnis:** Negation erkannt → keine automatische Inferenz → diet-Frage wird gestellt. Dokumentierter Edge Case: shallow negation detection.

---

## Auswertungstabelle

Nach den Runs ausfüllen:

| Run | Task Completion | Slots korrekt | STT-Fehler | Anmerkung |
|---|---|---|---|---|
| 01 | ✅ / ❌ | / 5 | | |
| 02 | ✅ / ❌ | / 5 | | |
| 03 | ✅ / ❌ | / 5 | | |
| 04 | ✅ / ❌ | / 5 | | |
| 05 | ✅ / ❌ | / 5 | | |
| 06 | ✅ / ❌ | / 5 | | |
| 07 | ✅ / ❌ | / 5 | | |
| 08 | ✅ / ❌ | / 5 | | |
| 09 | ✅ / ❌ | / 5 | | |
| 10 | ✅ / ❌ | / 5 | | |
| 11 | ✅ / ❌ | / 5 | | |
| 12 | ✅ / ❌ | / 5 | | |
| 13 (Edge) | ✅ / ❌ | / 5 | | |
| 14 (Edge) | ✅ / ❌ | / 5 | | |
| 15 (Edge) | ✅ / ❌ | / 5 | | |
| 16 (Edge) | ✅ / ❌ | / 5 | | |
| 17 (Edge) | ✅ / ❌ | / 5 | | |
| 18 (Edge) | ✅ / ❌ | / 5 | | |
| 19 (Edge) | ✅ / ❌ | / 5 | | |
| 20 (Edge) | ✅ / ❌ | / 5 | | |
| **Gesamt** | **/ 20** | | | |
