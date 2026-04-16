# VocaDine — Documented STT & NLU Problems

---

## P-001 — Tübingen → "tubing in" (STT phonetic error)

**Datum:** 2026-04-12
**Input (gesprochen):** "I'm in Tübingen Germany and I'm looking for a burger place"
**STT Output:** "I'm in tubing in ich"
**Problem:** Google STT (en-US) kennt "Tübingen" nicht → phonetische Annäherung "tubing in". Zusätzlich Sprachrest "ich" am Ende (vermutlich Hintergrundrauschen oder Übergang).
**Fix:** Aliases `"tubing"`, `"tubing in"`, `"tubingen"` → `"Tübingen"` in `german_cities.py` ergänzt.
**Status:** Gefixt ✅

---

## P-002 — "burger" nicht in Cuisine-Liste

**Datum:** 2026-04-12
**Input:** "I'm looking for a burger place"
**Problem:** `_extract_multiple_slots()` kannte "burger" nicht → cuisine-Slot blieb leer.
**Fix:** "burger", "burgers", "pizza", "sushi", "kebab", "vietnamese", "spanish" zur Cuisine-Liste ergänzt.
**Status:** Gefixt ✅

---

## P-003 — Implizite Slots nicht abgefangen (Brainstorming 2026-04-12)

**Problem:** Freie Spracheingabe enthält viele Ausdrücke die semantisch Slot-Werte bedeuten, aber nicht als Keywords erkannt wurden.
**Fix:** `_extract_multiple_slots()` erweitert um:

| Ausdruck | Slot | Wert |
|----------|------|------|
| "romantic", "anniversary" | occasion | date |
| "kids", "children", "family" | occasion | family |
| "fancy", "upscale", "high end" | budget | fine dining |
| "nothing fancy", "not too expensive" | budget | moderate |
| "affordable", "inexpensive" | budget | cheap |
| "close by", "nearby", "not too far" | distance | walking |
| "just the two of us" | group_size | 2 |
| "me and my wife/partner/friend" | group_size | 2 |
| "around X" | group_size | X |
| "surprise me", "anything", "whatever" | alle leeren Slots | any |

**Status:** Gefixt ✅

---

## P-004 — Ambiguity Handling fehlte (2026-04-12)

**Problem:** Bei Antworten wie "Italian or maybe Greek" wurde blind der erste Treffer ("Italian") genommen, ohne den User zu fragen. Anne forderte explizit: *"follow-up clarification triggered when system detects ambiguous responses."*

**Fix:** Zwei neue Methoden in `DialogStateManager`:
- `_detect_ambiguity(transcript)` — prüft ob ≥2 Cuisines im Transcript → gibt `(slot, [option_a, option_b])` zurück
- `_resolve_ambiguity(slot, options)` — stellt Rückfrage: *"I noticed you mentioned Italian and Greek. Which would you prefer?"* → hört nochmal zu → setzt Slot korrekt

Aufgerufen nach offener Einstiegsfrage UND nach jeder `_ask_slot()`-Antwort.

**Status:** Gefixt ✅

---

## P-005 — "egal" / Indifferenz nicht abgefangen (2026-04-12)

**Problem:** User sagt "egal", "I don't care", "whatever" → keine Extraktion, alle Slots blieben leer → System fragte trotzdem alle Folgefragen ab.
**Erwartetes Verhalten:** System akzeptiert Indifferenz, füllt alle leeren Slots mit "any", antwortet: *"Ok, I'll surprise you!"*
**Fix:** "egal", "i don't care", "don't care" zu Surprise-Trigger ergänzt. Sentinel `__surprise__` in confirmed-Liste → TTS-Sonderantwort statt Standard-Bestätigung.
**Status:** Gefixt ✅

---

## P-006 — Ambiguity & implicit slots unerkannt durch Rule-Based NLU (2026-04-12)

**Problem:** Rule-based `_extract_multiple_slots()` versagt bei unerwarteten Formulierungen (z. B. "somewhere cozy and not too formal" → budget/occasion unklar) und bei phonetisch verzerrten Städtenamen die nicht im Alias-Dict sind. `_detect_ambiguity()` kann nur vordefinierte Cuisine-Keywords prüfen.
**Lösung:** `ClaudeNLUFallback` — zweistufige NLU-Pipeline:
1. Rule-based extraction läuft zuerst (deterministisch, kein API-Call).
2. Falls nach Extraktion noch Slots leer sind, wird `ClaudeNLUFallback.extract_slots()` aufgerufen (Anthropic API, `claude-haiku-4-5-20251001`, max 150 Token).
3. Claude gibt flaches JSON zurück, das in leere Slots gemergt wird.

**Integration:**
- `run_interview()`: Claude-Fallback nach offener Einstiegsfrage.
- `_ask_slot()`: Claude-Fallback nach Rule-Based + NLU, falls Ziel-Slot noch `None`.
- Nur aufgerufen wenn `ANTHROPIC_API_KEY` gesetzt — graceful degradation ohne Key.

**Status:** Gefixt ✅

---

## P-007 — "germany" → "German cuisine" (Substring false positive)

**Datum:** 2026-04-12
**Input:** "I'm looking for a burger place in tubing in Germany"
**Problem:** `"german"` war als Cuisine-Keyword eingetragen. `"germany"` enthält `"german"` als Substring → false positive, cuisine auf "German" gesetzt obwohl User kein deutsches Essen meinte.
**Fix:** `"german"` entfernt, ersetzt durch `"german food"` und `"traditional german"`.
**Status:** Gefixt ✅

---

## P-008 — Diet-Verneinung nicht erkannt ("no restrictions")

**Datum:** 2026-04-12
**Input:** "no I'm eating everything" / "I eat meat"
**Problem:** Nur explizite Diät-Keywords geprüft. Verneinungen und positive Aussagen ("eat everything", "eat meat") → diet blieb `None`. `NLU.extract()` gab Rohtext zurück statt `None`.
**Fix:** Negations-Pattern ergänzt: `"no restrictions"`, `"eat everything"`, `"eat meat"`, `"meat eater"` etc. → `diet = "none"`. `NLU.extract()` gibt für Nicht-Location-Slots `None` zurück.
**Status:** Gefixt ✅

---

## P-009 — "I don't care" triggerte Surprise auf allen Slots

**Datum:** 2026-04-12
**Input:** "I don't care like actually I just want burgers I'm not that expensive"
**Problem:** `"i don't care"` im globalen Surprise-Trigger → alle leeren Slots auf `"any"`, obwohl User nur den Budget-Slot überspringen wollte.
**Fix:** `"i don't care"` aus Surprise-Trigger entfernt. Slot-spezifischer Indifferenz-Fallback in `_ask_slot()`: nur der aktuell gefragte Slot wird auf `"any"` gesetzt.
**Status:** Gefixt ✅

---

## P-010 — "average price" / "normal budget" nicht in budget_map

**Datum:** 2026-04-12
**Input:** "average price", "normal budget"
**Problem:** Fehlende Keywords für "moderate". `"budget"` als Standalone traf auf "normal budget" → false positive "cheap".
**Fix:** `"average"`, `"average price"`, `"normal price"`, `"regular"` → `"moderate"` ergänzt. `"budget"` ersetzt durch `"tight budget"`, `"low budget"`, `"on a budget"`.
**Status:** Gefixt ✅

---

## P-011 — "just want to have dinner" → occasion nicht erkannt

**Datum:** 2026-04-12
**Input:** "I just want to have dinner"
**Problem:** `"dinner"` / `"have dinner"` fehlten in occasion_map.
**Fix:** `"have dinner"`, `"have lunch"`, `"grab a bite"`, `"just dinner"`, `"just want to eat"` → `"casual"` ergänzt.
**Status:** Gefixt ✅

---

## P-012 — Ungeduld des Users nicht erkannt / kein vorzeitiger Abbruch

**Datum:** 2026-04-12
**Input:** "you know it's taking too long I just want to go stop asking"
**Problem:** System fragte weiter nach optionalen Slots trotz explizitem Abbruchsignal.
**Fix:** `ImpatienceDetector`-Klasse mit VADER-Sentiment + Keyword-Pattern. Bei Detektion: alle leeren Slots → `"any"`, TTS: *"I'm sorry for taking so long!"* Dazu `__stop__`-Sentinel in `_extract_multiple_slots()`.
**Status:** Gefixt ✅

---

## P-013 — TTS sagt "searching in any" wenn Location unbekannt

**Datum:** 2026-04-12
**Problem:** Location-Slot = `"any"` → TTS: *"searching for best matches in any"*.
**Fix:** `city_display = city if city and city != "any" else "Germany"`.
**Status:** Gefixt ✅

---

## P-014 — "me and my family" → group_size = 2 (sollte > 2 sein)

**Datum:** 2026-04-12
**Problem:** Pattern `\bme and my \w+\b` traf auch auf `"family"`, `"friends"` → group_size = 2.
**Fix:** Zwei Patterns: `"(me and my|with my) (family|friends|team|…)"` → 4; `"(me and my|with my) (wife|girlfriend|partner|…)"` → 2.
**Status:** Gefixt ✅

---

## P-015 — Location unbekannt → stummes "any" ohne Retry

**Datum:** 2026-04-12
**Input:** "Simon Harper Mecca at the moment" (STT-Fehler für unbekannte Stadt)
**Problem:** Keine Alias → Location = `"any"` → Suche ohne Stadtbezug.
**Fix:** Einmaliger Retry in `_ask_slot("location")`: *"I'm sorry, I didn't catch the city. Could you spell it out or try again?"*
**Status:** Gefixt ✅

---

## P-016 — "with my girlfriend" nicht als group_size=2 erkannt

**Datum:** 2026-04-12
**Input:** "I want to go there with my girlfriend"
**Problem:** Pattern prüfte nur `"me and my X"`, nicht `"with my X"`.
**Fix:** Pattern auf `\b(me and my|with my) …\b` erweitert.
**Status:** Gefixt ✅

---

## P-017 — "I just explained" / "told you" nicht im Impatience-Detector

**Datum:** 2026-04-12
**Input:** "I just explained to you I'm not explaining again"
**Problem:** Formulierungen wie "I already told you", "I just said", "not explaining again" lösten keine Impatience aus.
**Fix:** Keywords ergänzt: `"i already told"`, `"i just said"`, `"i just explained"`, `"not explaining"`, `"told you"`, `"said that already"`.
**Status:** Gefixt ✅

---

## P-018 — Slot-spezifische Indifferenz ("I don't care about budget") nicht erkannt

**Datum:** 2026-04-12
**Input:** "I don't care about budget"
**Problem:** Nach Entfernung von `"don't care"` aus Surprise-Trigger: slot-spezifische Indifferenz nicht mehr abgefangen → Slot blieb `None`.
**Fix:** Indifferenz-Fallback in `_ask_slot()`: `"don't care"` / `"doesn't matter"` / `"up to you"` / `"whatever"` → Slot = `"any"`.
**Status:** Gefixt ✅

---

## P-019 — "Horb am Neckar" → "hope America" (STT phonetic error)

**Datum:** 2026-04-12
**Input (gesprochen):** "I'm in Horb am Neckar"
**STT Output:** "hope America"
**Problem:** Google STT (en-US) kennt "Horb am Neckar" nicht. Phonetische Annäherung: "Horb" → "hope", "Neckar" → "America".
**Fix:** Aliases `"hope america"`, `"hope am neckar"`, `"horb"` → `"Horb am Neckar"` in `german_cities.py` ergänzt.
**Status:** Gefixt ✅

---

## P-020 — "Döner" → "doona" (STT phonetic error, Cuisine)

**Datum:** 2026-04-12
**Input (gesprochen):** "I'm looking for a döner place"
**STT Output:** "doona place"
**Problem:** Google STT (en-US) kennt "Döner" nicht → phonetische Annäherung "doona".
**Fix:** `"doona"`, `"dooner"`, `"doner"`, `"döner"` zur Cuisine-Liste in `_extract_multiple_slots()` ergänzt.
**Status:** Gefixt ✅

---

## P-021 — VADER Impatience: "fuck you" korrekt erkannt ✅

**Datum:** 2026-04-12
**Input:** "fuck you"
**VADER compound:** -0.54 → `vader_strong = True` (Schwelle: < -0.5)
**Ergebnis:** System hat sofort abgebrochen und nach Restaurants gesucht. Kein weiterer Fix nötig — dokumentiert als Erfolgsbeispiel für die Slides.
**Status:** Kein Fix erforderlich ✅

---
