# VocaDine — Phase 2 Submission Matrix
**Quellen:** Assignments Portfolio DLMAIWNLPVA02, Guidelines Portfolio, feedback1.txt (Phase 1), feedback2_anne_schwerk.txt (Phase 2)
**Stand:** 2026-04-30

---

## Phase 2 Abgabe — Was, wo, wie

PebblePad verlangt **drei Teile**:

| Part | Was | Format | Status |
|---|---|---|---|
| **A** | Reflection Text (max. 0,5 A4-Seite) | Direkt in PebblePad eingeben | ❌ Nicht geschrieben |
| **B** | 10-Slide Presentation | PDF-Upload | ⚠️ HTML fertig → PDF-Export fehlt |
| **C** | GitHub-Link | Text-Feld in PebblePad | ✅ https://github.com/kormuch/Vocadine_Restaurant_Finder |

**Dateiname:** `Much-Korbinian_[MatrNr]_Voice Assistants_P2_S.pdf`

---

## Matrix: Anforderungen vs. Ergebnis

### A — Formale Pflichtanforderungen (Assignments Portfolio)

| # | Anforderung | Quelle | Ergebnis | Status |
|---|---|---|---|---|
| 1 | 10-Slide PDF | Assignments Portfolio | `vocadine_p2.html` (10 Slides) — PDF-Export noch nicht gemacht | ⚠️ |
| 2 | Visuelle Elemente in Slides | Assignments Portfolio | Tabellen, F1-Balken, Pipeline-Diagramm, Code-Boxen, Stat-Cards | ✅ |
| 3 | Hyperlinks zu Frameworks | Assignments Portfolio | In `slides_konzept_v2.md` vorhanden — in HTML noch nicht als `<a href>` eingebaut | ⚠️ |
| 4 | Precision / Recall / F1 | Assignments Portfolio | Slide 7: Per-Label + Macro, Balkendiagramm | ✅ |
| 5 | Setup frameworks | Assignments Portfolio | Slide 2: Stack-Tabelle mit Begründungen | ✅ |
| 6 | Collect training data | Assignments Portfolio | Slide 5: 600 Utterances, 420/90/90 Split, Annotation Guidelines | ✅ |
| 7 | Train NLP models | Assignments Portfolio | Slide 5: spaCy NER, 40 Epochen, Macro-F1=0.881 | ✅ |
| 8 | Error analysis | Assignments Portfolio | Slide 9: 13 Fehler dokumentiert, 10 behoben, 3 offen/bekannt | ✅ |
| 9 | Optional Feature (Pick 1) | Assignments Portfolio | Google Places API (Option 2: Open data) — Slide 6 | ✅ |
| 10 | Reflection Text max. 0,5 A4 | Guidelines Portfolio | Nicht geschrieben | ❌ |

---

### B — Inhaltliche Anforderungen aus Annes Feedbacks

#### Anne Phase 1 Feedback (noch nicht vollständig adressiert in v1)

| # | Annes Punkt (Phase 1) | In v2 adressiert? | Wo | Status |
|---|---|---|---|---|
| B1 | Recommendation-Mechanismus konkret spezifizieren (Features, User Encoding, Ranking) | Ja | Slide 6: Feature-Strings, Formel, Attribute-Bonuses | ✅ |
| B2 | Technologieentscheidungen begründen (warum TF-IDF, warum diese TTS) | Ja | Slide 2: Tabelle Component/Choice/Why inkl. pyttsx3-Begründung | ✅ |
| B3 | Architekturdiagramm mit klaren Komponentengrenzen und Datenflusspfeilen | Teilweise | Pipeline-Zeile auf Slide 2 vorhanden — kein echtes draw.io-Diagramm | ⚠️ |

#### Anne Phase 2 Feedback (27.04.2026)

| # | Annes Punkt (Phase 2) | In v2 adressiert? | Wo | Status |
|---|---|---|---|---|
| C1 | Feature Engineering vertiefen: warum `name + types`? Was wenn types generisch? | Ja | Slide 6: Reviews + Attributes erklärt, Generic-Types-Problem benannt | ✅ |
| C2 | 40/60-Gewichtung begründen — empirisch oder Designentscheidung? | Ja | Slide 6: explizit als Designentscheidung begründet | ✅ |
| C3 | TF-IDF "Training"-Argument ehrlich einräumen | Ja | Slide 6: Einschränkung direkt benannt, spaCy als echter ML-Nachweis | ✅ |
| C4 | F1=1.000 auf 20 Utterances ist kein Beleg für Robustheit | Ja | Slide 7: 0.881 auf 90 Holdout-Utterances, ehrliche Rahmung, GROUP_SIZE-Limitation erklärt | ✅ |
| C5 | Spannung F1=1.000 vs. 11 Bugs in Error Analysis auflösen | Ja | Slide 7 + 9: neue Metriken, altes F1=1.000 komplett ersetzt | ✅ |
| C6 | Latenz: 1.8s vs. 8s Diskrepanz klären | Ja | Slide 7: lokale Latenz (1.8s) vs. E2E inkl. API (~6–9s) getrennt | ✅ |
| C7 | Privacy: Audio geht an Google Cloud — ehrlich benennen | Ja | Slide 8: Datenflusstabelle, GDPR-Hinweis, "no always-on mic" als Mindeststandard eingeordnet | ✅ |
| C8 | pyttsx3 → edge-tts: Wechsel nirgendwo erklärt | Ja | Slide 2: Spyder/IPython-Inkompatibilität explizit als Grund | ✅ |
| C9 | Alexa als Strohmann — Stärken einräumen | Ja | Slide 3: Alexa-Stärken-Liste, Vergleich auf Use Case begrenzt | ✅ |
| C10 | "0 Typing Required" ist trivial — ersetzen | Ja | Ersetzt durch "600 annotated utterances" auf Slide 1 | ✅ |
| C11 | Grice-Zitat dekorativ — straffen | Ja | Grice gestrichen; Literaturliste auf 5 relevante Referenzen reduziert | ✅ |
| C12 | Architekturdiagramm: Komponenten klarer trennen | Teilweise | Pipeline-Grafik auf Slide 2 vorhanden — kein formales UML | ⚠️ |

---

### C — Mandatory Documentation Checklist (Phase 3 — zur Information)

Diese sind für Phase 3 fällig, aber gut, sie jetzt schon zu kennen:

| Dokument | Status | Datei |
|---|---|---|
| Functional & non-functional requirements | ❌ | Fehlt |
| Design document mit Architekturübersicht | ⚠️ | README hat Inhalt, kein formales Dokument |
| Data annotation guidelines | ✅ | `data/annotation_guidelines.md` |
| Dataset description | ⚠️ | `training_data.py` vorhanden, kein separates Dokument |
| Evaluation metrics table | ✅ | Slide 7 + `test_results.json` |
| GitHub link | ✅ | https://github.com/kormuch/Vocadine_Restaurant_Finder |

---

## Offene Aufgaben für Phase 2 Abgabe

| Priorität | Aufgabe | Aufwand |
|---|---|---|
| 🔴 P1 | **Reflection Text schreiben** (150–200 Wörter, Part A PebblePad) | 20 min |
| 🔴 P1 | **Hyperlinks** in `vocadine_p2.html` einbauen (SpeechRecognition, edge-tts, scikit-learn, Google Places) | 10 min |
| 🔴 P1 | **PDF exportieren** aus Browser (Ctrl+P → "Background graphics" an → Save as PDF) | 5 min |
| 🔴 P1 | **In PebblePad einreichen**: Part A (Text), Part B (PDF-Upload), Part C (GitHub-Link) | 10 min |
| 🟡 P2 | Draw.io / Mermaid Architekturdiagramm — Anne hat es zweimal angemerkt | 30 min |

---

## Was wir NICHT brauchen für Phase 2

- ZIP-Ordner (Phase 3)
- 2-seitiges Abstract / "Making Of" (Phase 3)
- Functional & non-functional requirements doc (Phase 3)
- Eidesstattliche Erklärung (Phase 3)

---

## Fazit

**Phase 2 ist inhaltlich bereit.** Alle Feedback-Punkte von Anne sind adressiert.
Fehlend für die Abgabe: Reflection Text (❌), Hyperlinks im HTML (⚠️), PDF-Export (⚠️).
