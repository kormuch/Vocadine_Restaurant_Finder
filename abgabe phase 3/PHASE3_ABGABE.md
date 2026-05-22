# VocaDine Phase 3 — Abgabe-Handover
**Stand:** 2026-05-20 | **Nächste Session:** Einreichen in PebblePad + myCampus

---

## Was wurde erledigt (diese Session)

### Code
| Was | Datei | Status |
|---|---|---|
| Venue type filter `_is_food_venue()` + `_FOOD_TYPES` allowlist | `voice assistant/main.py` | ✅ Done (v0.3) |
| Radius search: `_geocode_city()` + `locationBias` 3km | `voice assistant/main.py` | ✅ Done (v0.3) |
| GitHub gepusht (v0.3 + Phase 3 Ordner) | github.com/kormuch/Vocadine_Restaurant_Finder | ✅ Done |

### Dokumente
| Was | Datei | Status |
|---|---|---|
| Making Of (fertig, plain text, bereit für Word) | `111.txt` | ✅ Done |
| Requirements (FR-01..FR-16, NFR-01..NFR-12) | `requirements.md` | ✅ Done |
| Design Document (6 Sektionen, ASCII-Architektur) | `design_document.md` | ✅ Done |
| Dataset Description (600 Utterances, 8 Sektionen) | `dataset_description.md` | ✅ Done |
| Final Product PDF-Vorlage (mit GitHub Link) | `final_product.md` | ✅ Done |
| User Documentation | `ZIP/04-Finished voice assistant/README_user.md` | ✅ Done |
| Literature + Zitationsstrategie | `literature.md` | ✅ Done |

### Präsentation
| Was | Status |
|---|---|
| Titel + Footer: "Phase 3 · May 2026" | ✅ Done |
| Slide 5: Label → "spaCy NER Pipeline" | ✅ Done |
| Slide 9: Error #12+#13 auf grün (mit Fix-Namen) | ✅ Done |
| Slide 10: Roadmap aktualisiert (#1+#2 done, #3+#4 realistisch) | ✅ Done |
| Slide 7: "20 self-conducted test sessions by the author" | ✅ Done |
| Slide 10: "90% (18/20 · author-conducted)" | ✅ Done |
| Datei | `vocadine_p3.html` | ✅ Done |

### ZIP
| Was | Status |
|---|---|
| `01-Research-and-Development/` — alle Docs | ✅ Done |
| `diagrams/` — architecture + presentation HTML | ✅ Done |
| `voice assistant/` — main.py, train, eval, data, models | ✅ Done |
| `04-Finished voice assistant/` — README_user, final_product | ✅ Done |
| ZIP-Datei korrekt benannt | `Much-Korbinian_IU14127772_Voice Assistants_P3_S.zip` | ✅ Done |

### Gegenprüfung (Gemini)
| Was | Status |
|---|---|
| 7 Merged-Dateien für Gemini-Upload | `überprüfung/` | ✅ Done |

---

## Was noch manuell zu tun ist (nächste Session)

### Schritt 1 — PDFs erstellen

#### Making Of PDF
1. `111.txt` öffnen (Notepad oder direkt in Word)
2. Alles markieren → einfügen in Word (neues Dokument)
3. Font: **Arial 11pt**, Zeilenabstand: **1.5**
4. Header: `Making Of — VocaDine | Korbinian Much | IU14127772 | DLMAIWNLPVA02`
5. Footer: Seitenzahlen
6. Prüfen: muss **genau 2 Seiten** sein
7. Exportieren als PDF → Name: `Much-Korbinian_IU14127772_Voice Assistants_P3_S_MakingOf.pdf`

#### Final Product PDF
1. `final_product.md` in Browser öffnen (via Typora, VS Code Preview, oder Markdown-to-PDF-Tool)
   - Alternativ: Copy-Paste in Word → als PDF exportieren
2. Name: `Much-Korbinian_IU14127772_Voice Assistants_P3_S_FinalProduct.pdf`

#### Presentation PDF
1. `vocadine_p3.html` im Browser öffnen (Chrome empfohlen)
2. Drucken → "Als PDF speichern" (Hochformat, alle Folien)
3. Name: `Much-Korbinian_IU14127772_Voice Assistants_P3_S_Presentation.pdf`

---

### Schritt 2 — Optionaler Gemini-Gegencheck
1. Gemini öffnen
2. Alle 7 Dateien aus `überprüfung/` hochladen:
   - `LIES_MICH_ZUERST.md`
   - `01_guidelines_and_requirements.txt`
   - `02_anne_feedback.txt`
   - `03_making_of.txt`
   - `04_phase3_documents.md`
   - `05_literature_and_issues.md`
   - `test_results.json`
3. Frage: *"Prüfe ob die Phase 3 Abgabe alle Anforderungen erfüllt. Gibt es inhaltliche Lücken oder Schwächen?"*
4. Feedback umsetzen falls nötig → PDFs neu exportieren

---

### Schritt 3 — PebblePad-Upload

Login: IU PebblePad → Portfolio DLMAIWNLPVA02

**Was hochladen:**

| Dokument | Datei |
|---|---|
| Phase 1 Ergebnis (re-upload) | — (aus Phase 1 Ordner) |
| Phase 2 Ergebnis (re-upload) | — (aus Phase 2 Ordner) |
| Phase 3 Making Of | `..._MakingOf.pdf` |
| Phase 3 Final Product | `..._FinalProduct.pdf` |
| Phase 3 ZIP | `Much-Korbinian_IU14127772_Voice Assistants_P3_S.zip` |

> Hinweis: GitHub Link ist im Final Product PDF enthalten. Nicht separat als Datei nötig.

---

### Schritt 4 — myCampus Eidesstattliche Erklärung

1. myCampus öffnen
2. Kurs DLMAIWNLPVA02 → Eidesstattliche Erklärung abgeben
3. Screenshot/Bestätigung sichern

---

## ZIP-Inhalt zur Kontrolle

```
Much-Korbinian_IU14127772_Voice Assistants_P3_S.zip
├── 01-Research-and-Development/
│   ├── annotation_guidelines.md
│   ├── dataset_description.md
│   ├── design_document.md
│   ├── literature.md
│   └── requirements.md
├── diagrams/
│   ├── architecture_diagram.html
│   └── vocadine_p3.html
├── voice assistant/
│   ├── main.py
│   ├── train_nlu.py
│   ├── eval_nlu.py
│   ├── german_cities.py
│   ├── requirements.txt
│   ├── data/
│   │   ├── training_data.py
│   │   └── annotation_guidelines.md
│   └── models/
│       └── vocadine_nlu/
└── 04-Finished voice assistant/
    ├── README_user.md
    └── final_product.md
```

---

## Bewertungserwartung (ehrliche Einschätzung)

| Kriterium | Gewicht | Erwartung |
|---|---|---|
| Quality of Implementation | 40% | Gut — NER F1=0.881, v0.3 mit venue filter + radius, 90% task completion |
| Creativity / Correctness | 20% | Gut — phonetic aliases, implicit filling, VADER sind echte NLP-Anwendungen |
| Methodology / Ideas | 20% | Ausreichend bis gut — Making Of adressiert alle Anne-Kritikpunkte direkt |
| Problem Solving | 10% | Gut — Problemdefinition klar (Sarah, kleine deutsche Stadt, Englisch) |
| Formal Requirements | 10% | Gut — wenn alle Dateien korrekt eingereicht werden |

---

## Dateipfade (Referenz)

| Datei | Pfad |
|---|---|
| Making Of (plain text) | `abgabe phase 3/111.txt` |
| Making Of (MD-Version) | `abgabe phase 3/making_of_draft.md` |
| Präsentation HTML | `abgabe phase 3/vocadine_p3.html` |
| ZIP | `abgabe phase 3/Much-Korbinian_IU14127772_Voice Assistants_P3_S.zip` |
| Gegenprüfung Ordner | `abgabe phase 3/überprüfung/` |
| GitHub | https://github.com/kormuch/Vocadine_Restaurant_Finder |
