"""
eval_nlu.py — NLU Evaluation for VocaDine Germany
Evaluates _extract_multiple_slots() from main.py using 20 test utterances.
Computes Precision, Recall, F1 per slot.

Usage:
    python eval_nlu.py

Expected output:
    Per-slot table of TP / FP / FN / Precision / Recall / F1
    + Overall macro-averaged F1

References:
    - IU Guidelines Portfolio DLMAIWNLPVA02, Slide 7+8 content
    - Jurafsky & Martin (2024): Ch. 8 (NER/NLU evaluation)
"""

import sys
import types

# ─────────────────────────────────────────────
# MINIMAL STUBS — prevent real I/O from loading
# ─────────────────────────────────────────────
# Stub out heavy/IO modules before importing main components
_stub_modules = [
    "speech_recognition", "pyttsx3", "sklearn",
    "sklearn.feature_extraction", "sklearn.feature_extraction.text",
    "sklearn.metrics", "sklearn.metrics.pairwise",
    "requests", "dotenv",
]
for mod_name in _stub_modules:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = types.ModuleType(mod_name)

# Provide the minimum needed so main.py parses cleanly
sys.modules["dotenv"].load_dotenv = lambda *a, **kw: None
sys.modules["sklearn.feature_extraction.text"].TfidfVectorizer = object
sys.modules["sklearn.metrics.pairwise"].cosine_similarity = lambda *a: [[0]]
sys.modules["requests"].get = lambda *a, **kw: None

# Now we can safely import our logic
import os
os.environ.setdefault("GOOGLE_PLACES_KEY", "DUMMY_FOR_EVAL")

from german_cities import GERMAN_CITIES  # noqa: E402

# ─────────────────────────────────────────────
# IMPORT DIALOG STATE MANAGER LOGIC
# ─────────────────────────────────────────────
# We replicate _extract_multiple_slots() here so the evaluator is self-contained
# and does not require a microphone / TTS / API key at eval time.
# This is the exact logic from main.py — keep in sync manually if main.py changes.

import re

CUISINES = ["italian", "turkish", "asian", "german", "french", "indian",
            "japanese", "chinese", "greek", "mexican", "thai", "american"]
DIETS = ["vegan", "vegetarian", "gluten-free", "halal", "kosher"]
BUDGET_MAP = [
    ("fine dining", "fine dining"), ("expensive", "fine dining"),
    ("moderate", "moderate"), ("cheap", "cheap"), ("budget", "cheap"),
]
WORD_NUMS = {
    "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8",
}


def extract_slots(transcript: str) -> dict:
    """
    Mirrors DialogStateManager._extract_multiple_slots() from main.py.
    Returns dict of extracted slot values (None = not found).
    Slots evaluated: location, cuisine, diet, budget, group_size
    """
    slots = {
        "location": None,
        "cuisine": None,
        "diet": None,
        "budget": None,
        "group_size": None,
    }

    t = transcript.lower().strip()

    # Location — word-boundary matching to avoid "burg" matching "hamburg"
    for key, canonical in GERMAN_CITIES.items():
        if re.search(r'\b' + re.escape(key) + r'\b', t):
            slots["location"] = canonical
            break

    # Cuisine
    for cuisine in CUISINES:
        if cuisine in t:
            slots["cuisine"] = cuisine.title()
            break

    # Diet
    for diet in DIETS:
        if diet in t:
            slots["diet"] = diet
            break
    if slots["diet"] is None and "none" in t:
        slots["diet"] = "none"

    # Budget
    for keyword, label in BUDGET_MAP:
        if keyword in t:
            slots["budget"] = label
            break

    # Group size — digits first, then word numbers
    match = re.search(r'\b(\d+)\b', t)
    if match:
        slots["group_size"] = match.group(1)
    else:
        for word, num in WORD_NUMS.items():
            if re.search(r'\b' + word + r'\b', t):
                slots["group_size"] = num
                break

    return slots


# ─────────────────────────────────────────────
# TEST DATASET — 20 utterances
# Format: (utterance, {slot: expected_value | None})
# None means "should NOT be extracted" (absence is correct negative)
# ─────────────────────────────────────────────
TEST_CASES = [
    # ── Easy single-slot ──────────────────────────────────────────
    (
        "i am in berlin",
        {"location": "Berlin", "cuisine": None, "diet": None, "budget": None, "group_size": None},
    ),
    (
        "i would like italian food",
        {"location": None, "cuisine": "Italian", "diet": None, "budget": None, "group_size": None},
    ),
    (
        "i am vegan",
        {"location": None, "cuisine": None, "diet": "vegan", "budget": None, "group_size": None},
    ),
    (
        "something cheap please",
        {"location": None, "cuisine": None, "diet": None, "budget": "cheap", "group_size": None},
    ),
    (
        "table for four",
        {"location": None, "cuisine": None, "diet": None, "budget": None, "group_size": "4"},
    ),
    # ── Multi-slot in one utterance ──────────────────────────────
    (
        "i am in munich looking for italian food",
        {"location": "München", "cuisine": "Italian", "diet": None, "budget": None, "group_size": None},
    ),
    (
        "vegan restaurant in hamburg for two people",
        {"location": "Hamburg", "cuisine": None, "diet": "vegan", "budget": None, "group_size": "2"},
    ),
    (
        "moderate budget greek food in cologne for three",
        {"location": "Köln", "cuisine": "Greek", "diet": None, "budget": "moderate", "group_size": "3"},
    ),
    (
        "fine dining in frankfurt vegetarian for 6 people",
        {"location": "Frankfurt am Main", "cuisine": None, "diet": "vegetarian", "budget": "fine dining", "group_size": "6"},
    ),
    (
        "cheap asian food berlin group of five",
        {"location": "Berlin", "cuisine": "Asian", "diet": None, "budget": "cheap", "group_size": "5"},
    ),
    # ── Phonetic / STT noise ─────────────────────────────────────
    (
        "i am visiting girl loch",          # phonetic alias for Haigerloch
        {"location": "Haigerloch", "cuisine": None, "diet": None, "budget": None, "group_size": None},
    ),
    (
        "munich turkish moderate",
        {"location": "München", "cuisine": "Turkish", "diet": None, "budget": "moderate", "group_size": None},
    ),
    (
        "looking for a restaurant in dusseldorf",
        {"location": "Düsseldorf", "cuisine": None, "diet": None, "budget": None, "group_size": None},
    ),
    (
        "halal food in stuttgart for eight guests",
        {"location": "Stuttgart", "cuisine": None, "diet": "halal", "budget": None, "group_size": "8"},
    ),
    # ── "None" diet slot — user says no restriction ───────────────
    (
        "no dietary restrictions none",
        {"location": None, "cuisine": None, "diet": "none", "budget": None, "group_size": None},
    ),
    # ── Budget synonyms ──────────────────────────────────────────
    (
        "something expensive for a date in berlin",
        {"location": "Berlin", "cuisine": None, "diet": None, "budget": "fine dining", "group_size": None},
    ),
    (
        "budget friendly japanese in hamburg",
        {"location": "Hamburg", "cuisine": "Japanese", "diet": None, "budget": "cheap", "group_size": None},
    ),  # "budget" triggers cheap; "hamburg" now matched via alias
    # ── Digits in various positions ──────────────────────────────
    (
        "we are 7 people looking for german food",
        {"location": None, "cuisine": "German", "diet": None, "budget": None, "group_size": "7"},
    ),
    # ── No slots expected (all-negative baseline) ─────────────────
    (
        "hello i would like a recommendation",
        {"location": None, "cuisine": None, "diet": None, "budget": None, "group_size": None},
    ),
    # ── Dense multi-slot ────────────────────────────────────────
    (
        "gluten-free chinese fine dining in cologne for 2",
        {"location": "Köln", "cuisine": "Chinese", "diet": "gluten-free", "budget": "fine dining", "group_size": "2"},
    ),
]

SLOTS_EVAL = ["location", "cuisine", "diet", "budget", "group_size"]


# ─────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────

def evaluate():
    # Per-slot counters
    counters = {slot: {"TP": 0, "FP": 0, "FN": 0} for slot in SLOTS_EVAL}

    print("\n" + "=" * 72)
    print(f"{'VOCADINE NLU EVALUATION':^72}")
    print(f"{'_extract_multiple_slots() -- 20 test utterances':^72}")
    print("=" * 72)

    for idx, (utterance, expected) in enumerate(TEST_CASES, 1):
        predicted = extract_slots(utterance)
        print(f"\n[T{idx:02d}] \"{utterance}\"")

        for slot in SLOTS_EVAL:
            exp = expected[slot]
            pred = predicted[slot]

            # Normalize comparison (case-insensitive where values are strings)
            exp_norm = exp.lower() if exp else None
            pred_norm = pred.lower() if pred else None

            if exp_norm is not None and pred_norm == exp_norm:
                counters[slot]["TP"] += 1
                mark = "OK"
            elif exp_norm is None and pred_norm is None:
                mark = "-"  # True negative -- correctly ignored
            elif exp_norm is not None and pred_norm != exp_norm:
                counters[slot]["FN"] += 1
                mark = f"FN (expected={exp}, got={pred})"
            else:  # exp_norm is None but pred_norm is not None
                counters[slot]["FP"] += 1
                mark = f"FP (unexpected={pred})"

            if mark not in ("-", "OK"):
                print(f"      {slot:12s}: {mark}")
            elif mark == "OK":
                print(f"      {slot:12s}: OK  {pred}")

    # ── Results table ────────────────────────────────────────────
    print("\n" + "=" * 72)
    print(f"{'RESULTS PER SLOT':^72}")
    print("=" * 72)
    print(f"{'Slot':<14} {'TP':>4} {'FP':>4} {'FN':>4}  {'Precision':>10} {'Recall':>8} {'F1':>8}")
    print("-" * 72)

    f1_scores = []
    for slot in SLOTS_EVAL:
        tp = counters[slot]["TP"]
        fp = counters[slot]["FP"]
        fn = counters[slot]["FN"]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1        = (2 * precision * recall / (precision + recall)
                     if (precision + recall) > 0 else 0.0)
        f1_scores.append(f1)
        print(f"{slot:<14} {tp:>4} {fp:>4} {fn:>4}  {precision:>10.3f} {recall:>8.3f} {f1:>8.3f}")

    macro_f1 = sum(f1_scores) / len(f1_scores)
    print("-" * 72)
    print(f"{'Macro-avg F1':<14} {'':>4} {'':>4} {'':>4}  {'':>10} {'':>8} {macro_f1:>8.3f}")
    print("=" * 72)
    print(f"\nTotal test cases: {len(TEST_CASES)}")
    print(f"Slots evaluated:  {', '.join(SLOTS_EVAL)}")
    print()


if __name__ == "__main__":
    evaluate()
