"""
train_nlu.py — VocaDine spaCy NER Training
============================================
Trains a blank English spaCy NER model on the 600-utterance dataset
from data/training_data.py (420 train / 90 val / 90 test).

Usage:
    python train_nlu.py

Output:
    models/vocadine_nlu/   — saved spaCy model (loadable with spacy.load())
    training_log.json      — per-epoch F1 on val set

Requirements:
    pip install spacy
    python -m spacy download en_core_web_sm   # optional: only used for tokenizer
"""

import json
import random
import sys
from pathlib import Path

import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MODEL_OUTPUT_DIR = Path("models/vocadine_nlu")
LOG_FILE         = Path("training_log.json")
LABELS           = ["LOCATION", "CUISINE", "DIET", "BUDGET", "GROUP_SIZE"]
N_EPOCHS         = 40
DROPOUT          = 0.35
BATCH_SIZE_START = 4.0
BATCH_SIZE_MAX   = 32.0
SEED             = 42


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------

def evaluate(nlp, examples):
    """
    Compute per-label and macro-averaged Precision / Recall / F1
    on a list of spaCy Example objects.
    Returns: dict with per-label stats + macro averages.
    """
    tp = {label: 0 for label in LABELS}
    fp = {label: 0 for label in LABELS}
    fn = {label: 0 for label in LABELS}

    for example in examples:
        text = example.reference.text
        doc  = nlp(text)

        pred_ents = {(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents}
        gold_ents = {(start, end, label)
                     for start, end, label in
                     [(ent.start_char, ent.end_char, ent.label_)
                      for ent in example.reference.ents]}

        for label in LABELS:
            pred_l = {(s, e) for (s, e, l) in pred_ents if l == label}
            gold_l = {(s, e) for (s, e, l) in gold_ents if l == label}
            tp[label] += len(pred_l & gold_l)
            fp[label] += len(pred_l - gold_l)
            fn[label] += len(gold_l - pred_l)

    results = {}
    precisions, recalls, f1s = [], [], []

    for label in LABELS:
        p = tp[label] / (tp[label] + fp[label]) if (tp[label] + fp[label]) > 0 else 0.0
        r = tp[label] / (tp[label] + fn[label]) if (tp[label] + fn[label]) > 0 else 0.0
        f = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        results[label] = {"precision": round(p, 4), "recall": round(r, 4), "f1": round(f, 4),
                          "tp": tp[label], "fp": fp[label], "fn": fn[label]}
        precisions.append(p); recalls.append(r); f1s.append(f)

    results["macro"] = {
        "precision": round(sum(precisions) / len(precisions), 4),
        "recall":    round(sum(recalls)    / len(recalls),    4),
        "f1":        round(sum(f1s)        / len(f1s),        4),
    }
    return results


def print_eval(results, prefix=""):
    print(f"\n{prefix}Evaluation:")
    print(f"  {'Label':<14} {'P':>6} {'R':>6} {'F1':>6}  TP  FP  FN")
    print(f"  {'-'*50}")
    for label in LABELS:
        r = results[label]
        print(f"  {label:<14} {r['precision']:>6.3f} {r['recall']:>6.3f} {r['f1']:>6.3f}"
              f"  {r['tp']:>2}  {r['fp']:>2}  {r['fn']:>2}")
    m = results["macro"]
    print(f"  {'MACRO':<14} {m['precision']:>6.3f} {m['recall']:>6.3f} {m['f1']:>6.3f}")


# ---------------------------------------------------------------------------
# Build spaCy Example objects
# ---------------------------------------------------------------------------

def make_spacy_examples(nlp, data):
    """Convert spaCy-format tuples into Example objects."""
    examples = []
    skipped  = 0
    for text, annotations in data:
        doc = nlp.make_doc(text)
        try:
            example = Example.from_dict(doc, annotations)
            examples.append(example)
        except Exception as e:
            print(f"  SKIP — {e} | text: {text!r}")
            skipped += 1
    if skipped:
        print(f"  Skipped {skipped} examples due to alignment errors.")
    return examples


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------

def train():
    random.seed(SEED)

    # Import data
    sys.path.insert(0, str(Path(__file__).parent))
    from data.training_data import split_data

    print("Loading training data...")
    train_data, val_data, test_data = split_data(seed=SEED)
    print(f"  Train: {len(train_data)} | Val: {len(val_data)} | Test: {len(test_data)}")

    # Build blank model
    nlp = spacy.blank("en")

    # Add NER pipe
    ner = nlp.add_pipe("ner", last=True)
    for label in LABELS:
        ner.add_label(label)

    # Convert to spaCy Examples (using untrained model for tokenisation only)
    print("Building spaCy examples...")
    train_examples = make_spacy_examples(nlp, train_data)
    val_examples   = make_spacy_examples(nlp, val_data)
    test_examples  = make_spacy_examples(nlp, test_data)
    print(f"  Usable — Train: {len(train_examples)} | Val: {len(val_examples)} | Test: {len(test_examples)}")

    # Initialise weights
    nlp.initialize(lambda: train_examples)

    # Training
    log        = []
    best_f1    = 0.0
    best_epoch = 0

    print(f"\nTraining for {N_EPOCHS} epochs (dropout={DROPOUT})...")
    print(f"{'Epoch':>5}  {'Loss':>9}  {'Val F1':>7}")
    print("-" * 30)

    optimizer = nlp.resume_training()

    for epoch in range(1, N_EPOCHS + 1):
        random.shuffle(train_examples)
        losses = {}

        batches = minibatch(
            train_examples,
            size=compounding(BATCH_SIZE_START, BATCH_SIZE_MAX, 1.001)
        )
        for batch in batches:
            nlp.update(batch, drop=DROPOUT, losses=losses, sgd=optimizer)

        # Evaluate on val set
        val_results = evaluate(nlp, val_examples)
        val_f1      = val_results["macro"]["f1"]
        epoch_loss  = round(losses.get("ner", 0.0), 4)

        print(f"{epoch:>5}  {epoch_loss:>9.4f}  {val_f1:>7.4f}")

        log.append({"epoch": epoch, "loss": epoch_loss, "val_macro_f1": val_f1,
                    "val_per_label": val_results})

        # Save best model
        if val_f1 >= best_f1:
            best_f1    = val_f1
            best_epoch = epoch
            MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            nlp.to_disk(MODEL_OUTPUT_DIR)

    print(f"\nBest model: epoch {best_epoch} — val macro F1 = {best_f1:.4f}")
    print(f"Saved to: {MODEL_OUTPUT_DIR.resolve()}")

    # Save training log
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)
    print(f"Training log: {LOG_FILE.resolve()}")

    # Final evaluation on test set (best saved model)
    print("\nLoading best model for test-set evaluation...")
    best_nlp = spacy.load(MODEL_OUTPUT_DIR)
    test_examples_best = make_spacy_examples(best_nlp, test_data)
    test_results = evaluate(best_nlp, test_examples_best)
    print_eval(test_results, prefix="TEST SET — ")

    # Save test results alongside log
    test_log_path = Path("test_results.json")
    with open(test_log_path, "w") as f:
        json.dump(test_results, f, indent=2)
    print(f"Test results: {test_log_path.resolve()}")

    return test_results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    results = train()
    macro = results["macro"]
    print(f"\nFinal test macro F1: {macro['f1']:.4f}  "
          f"(P={macro['precision']:.4f}, R={macro['recall']:.4f})")
