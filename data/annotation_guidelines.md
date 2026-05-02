# VocaDine NER — Annotation Guidelines

**Project:** VocaDine Germany — NLP & Voice 2 (DLMAIWNLPVA02)
**Model:** spaCy blank English NER
**Dataset:** 600 utterances, 5 entity labels
**Last updated:** 2026-04-29

---

## Overview

These guidelines describe how to label named entities in VocaDine utterances.
VocaDine is a spoken restaurant-finder for English-speaking tourists in Germany.
All input comes from automatic speech recognition (ASR) — transcripts may contain
misspellings, missing punctuation, and informal phrasing.

Each utterance may contain zero, one, or several entities.
Label only the **minimal span** that identifies the entity value.
Do not include surrounding articles, prepositions, or filler words.

---

## Entity Labels

### LOCATION
**Definition:** A German city or recognisable district/neighbourhood the user
is currently in or explicitly travelling to for the purpose of finding a restaurant.

**Annotate:** The city name only — no country, no surrounding words.

| Utterance | Span | Label |
|-----------|------|-------|
| "Are there any restaurants in **Berlin**?" | Berlin | LOCATION |
| "We are visiting **Munich** this weekend." | Munich | LOCATION |
| "Can you find something in **Hamburg city centre**?" | Hamburg | LOCATION |

**Do NOT annotate:**
- Cities mentioned only as comparison or past experience ("I loved Milan last year")
- Country names ("We are in Germany" — too broad, not a city)
- Vague location words ("near me", "close by", "downtown" without a city)

**Edge cases:**
- Alternate spellings and ASR variants are valid: "Cologne" = "Köln", "Nuremberg" = "Nürnberg"
- Annotate the surface form exactly as it appears in the transcript

---

### CUISINE
**Definition:** A food type, culinary tradition, or specific dish category the user
explicitly requests.

**Annotate:** The minimal descriptor — cuisine adjective or noun phrase.

| Utterance | Span | Label |
|-----------|------|-------|
| "I'm in the mood for **Italian** food." | Italian | CUISINE |
| "Something **traditional German** would be great." | traditional German | CUISINE |
| "We want **sushi** tonight." | sushi | CUISINE |

**Do NOT annotate:**
- Generic terms without cuisine signal ("good food", "something nice", "a restaurant")
- Brand names or specific restaurant names

**Edge cases:**
- Compound phrases: annotate the full meaningful span ("traditional German", not just "German")
- Dish names that imply cuisine: "sushi" → CUISINE, "pizza" → CUISINE, "döner" → CUISINE
- ASR variants: "doner", "dooner", "doona" are all valid CUISINE spans

---

### DIET
**Definition:** An explicit dietary requirement, restriction, or lifestyle preference
stated by the user.

**Annotate:** The specific diet keyword or short phrase.

| Utterance | Span | Label |
|-----------|------|-------|
| "I'm **vegan** so the menu needs to work for me." | vegan | DIET |
| "My friend is **gluten-free**." | gluten-free | DIET |
| "We eat **halal** only." | halal | DIET |

**Recognised values:** vegan, vegetarian, gluten-free, halal, kosher, dairy-free, nut-free

**Do NOT annotate:**
- Negations of restrictions ("no dietary restrictions", "I eat everything") — these are
  implicit "none" values handled by rule-based logic, not NER
- Preferences without restriction signal ("I prefer light food")

**Edge cases:**
- "plant-based" → annotate as DIET (maps to vegan in normalisation)
- "no meat" → annotate as DIET if phrased as restriction, not as casual preference

---

### BUDGET
**Definition:** An explicit price-range preference or budget category stated by the user.

**Annotate:** The minimal span expressing the budget level.

| Utterance | Span | Label |
|-----------|------|-------|
| "Something **cheap** please." | cheap | BUDGET |
| "**Fine dining** is fine, we're celebrating." | fine dining | BUDGET |
| "I'm on a **tight budget**." | tight budget | BUDGET |

**Normalisation targets:** cheap · moderate · fine dining
(Annotators label the surface span; normalisation to these three values happens in code.)

**Recognised surface forms:**
- cheap: "cheap", "affordable", "inexpensive", "budget", "tight budget", "low budget"
- moderate: "moderate", "mid-range", "not too expensive", "nothing fancy", "somewhere in between"
- fine dining: "fine dining", "upscale", "fancy", "expensive", "high end"

**Do NOT annotate:**
- Specific price figures ("under 20 euros") — these are not covered by the model
- Vague hedges without clear budget signal ("reasonable", "fair")

---

### GROUP_SIZE
**Definition:** The number of people the user is booking or searching for.

**Annotate:** The number word, digit, or short phrase expressing the group size.

| Utterance | Span | Label |
|-----------|------|-------|
| "Table for **four** please." | four | GROUP_SIZE |
| "There are **two of us**." | two of us | GROUP_SIZE |
| "We are a group of **six**." | six | GROUP_SIZE |

**Annotate digits and word forms:** "2", "two", "a party of five" → annotate "five"

**Edge cases:**
- "just the two of us" → annotate "two of us"
- "me and my wife" → do NOT annotate (no explicit number; rule-based logic handles this)
- "me and three friends" → annotate "three" (the explicit number)
- Solo traveller: "just me", "only me", "I'm alone" → annotate "me" as GROUP_SIZE span

---

## General Rules

### Span boundaries
- Label the **minimal meaningful span**: no leading/trailing articles or prepositions
- Correct: `"Italian"` | Wrong: `"for Italian food"`
- Exception: multi-word entities where all words are part of the value
  ("fine dining", "traditional German", "tight budget")

### Overlapping entities
- Overlapping spans are **not allowed**
- If two interpretations are possible, choose the label with higher specificity

### Empty annotations
- Utterances with no entity are valid training examples (negative examples)
- Do not force a label on ambiguous spans

### ASR noise
- Annotate the surface form exactly as it appears — do not correct spelling
- If the intent is clear despite noise ("veejin" for "vegan"), annotate as DIET
- If the span is genuinely ambiguous due to noise, skip it

### Language
- All utterances are English
- German city names with umlauts are valid LOCATION spans (Düsseldorf, Köln, München)

---

## Data Split

| Split | Size | Purpose |
|-------|------|---------|
| Train | 420 (70%) | Weight updates |
| Val   |  90 (15%) | Epoch-level F1, model selection |
| Test  |  90 (15%) | Final held-out evaluation (run once) |

Split is deterministic via `random.seed(42)` in `data/training_data.py → split_data()`.

---

## Inter-Annotator Agreement

Target: Cohen's κ ≥ 0.85 on a 50-sentence sample before full annotation begins.
Disagreements are resolved by majority vote among three annotators, or by the
project lead if only two annotators are available.

---

## Quality Checks

Before adding examples to `training_data.py`:
1. Run `make_example()` — any `WARNING:` in output indicates a span not found → fix text or span
2. Check for overlapping entity warnings
3. Confirm distribution stays balanced across labels (see target counts in `training_data.py` header)
4. Re-run `train_nlu.py` after adding ≥ 20 new examples
