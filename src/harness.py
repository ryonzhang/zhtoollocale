"""
ZhToolLocale — evaluation harness skeleton (v0)

Tests whether a model converts Chinese locale semantics into CORRECT canonical
tool arguments. Complementary to MLCL (arXiv:2601.05366), which measures
value-language-mismatch; here we measure conversion correctness + recovery.

Offline & deterministic: tools are mocked, ground truth is fixed, so runs are
fully reproducible and cost only inference. Plug your own model into `model_call`.

Usage:
    python harness.py            # runs the dummy model (shows scoring works)
    # then replace model_call() with a real API/local model call.
"""
from __future__ import annotations
import json, os, argparse
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def load_probes(path=None):
    # repo layout: probes live in ../probes/ relative to this file (src/)
    PROBES = os.path.join(HERE, "..", "probes")
    if path is None:
        for cand in (os.path.join(PROBES, "probes_seed.json"),
                     os.path.join(HERE, "probes_seed.json")):
            if os.path.exists(cand):
                path = cand; break
    elif not os.path.isabs(path) and not os.path.exists(path):
        cand = os.path.join(PROBES, os.path.basename(path))
        if os.path.exists(cand):
            path = cand
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------------------------------- model hook
def model_call(utterance_zh, tool_spec, prior_error=None):
    """REPLACE THIS with a real model call.

    Must return a dict of predicted arguments, e.g. {"date": "2026-06-08"}.
    `prior_error` is set on recovery probes (the tool's error message); a real
    agent would use it to correct its previous call.

    The dummy below just returns {} so you can see the harness run end-to-end.
    """
    return {}


# ------------------------------------------------------------------- scoring
def args_match(pred: dict, gold: dict) -> bool:
    """Exact match on every gold key, with light numeric tolerance."""
    # FIX 4: unwrap a tool-call envelope {'name':..,'arguments':{..}} -> {..}
    if (isinstance(pred, dict) and set(pred.keys()) == {"name", "arguments"}
            and isinstance(pred["arguments"], dict)):
        pred = pred["arguments"]
    if not isinstance(pred, dict):
        return False
    for k, gv in gold.items():
        if k not in pred:
            return False
        pv = pred[k]
        if isinstance(gv, (int, float)) and isinstance(pv, (int, float)):
            if abs(float(pv) - float(gv)) > 1e-9:
                return False
        else:
            if str(pv).strip() != str(gv).strip():
                return False
    return True


def is_api_error(pred) -> bool:
    """A probe whose model call raised (non-rate-limit) or exhausted retries.
    models.py signals this with a sentinel dict {'__api_error__': <msg>}."""
    return isinstance(pred, dict) and "__api_error__" in pred


def evaluate(data, call=model_call):
    """`call` is the model function (signature: utterance_zh, tool_spec, prior_error=None).
    Defaults to the dummy `model_call`; pass a real one from models.py.

    A probe that returns the {'__api_error__': ...} sentinel is recorded as
    status 'ERR' and is excluded from BOTH the numerator and the denominator
    of every score (by_cat / by_layer only count successfully-scored probes)."""
    by_cat = defaultdict(lambda: [0, 0])      # category -> [correct, scored]
    by_layer = defaultdict(lambda: [0, 0])    # layer -> [correct, scored]
    rows = []
    for p in data["probes"]:
        layer = p["layer"]
        if layer == "recovery":
            # first call (expected to fail), then recovery with the error message
            _ = call(p["utterance_zh"], p["tool"])
            pred = call(p["utterance_zh"], p["tool"],
                        prior_error=p["tool_error"])
            gold = p["expected_recovery_args"]
        else:
            pred = call(p["utterance_zh"], p["tool"])
            gold = p["expected_args"]
        if is_api_error(pred):
            # excluded from numerator AND denominator
            rows.append((p["id"], p["category"], layer, "ERR", pred, gold))
            continue
        ok = args_match(pred, gold)
        by_cat[p["category"]][0] += ok; by_cat[p["category"]][1] += 1
        by_layer[layer][0] += ok; by_layer[layer][1] += 1
        rows.append((p["id"], p["category"], layer, "PASS" if ok else "FAIL", pred, gold))
    return rows, by_cat, by_layer


def report(rows, by_cat, by_layer):
    n_err = sum(1 for r in rows if r[3] == "ERR")
    n_scored = len(rows) - n_err
    total_ok = sum(1 for r in rows if r[3] == "PASS")
    if n_scored == 0:
        print(f"\n=== ZhToolLocale v0 — 0 scored, {n_err} errored "
              f"(no successful API calls) ===\n")
    else:
        print(f"\n=== ZhToolLocale v0 — {total_ok}/{n_scored} correct "
              f"({100*total_ok/n_scored:.1f}%) ===")
        print(f"({n_scored} scored, {n_err} errored)\n")
    print("By category:")
    for c, (ok, n) in sorted(by_cat.items()):
        pct = f"{100*ok/n:.0f}%" if n else "n/a"
        print(f"  {c:18s} {ok}/{n}  ({pct})")
    print("\nBy layer (the 4-layer attribution):")
    for l, (ok, n) in sorted(by_layer.items()):
        pct = f"{100*ok/n:.0f}%" if n else "n/a"
        print(f"  {l:12s} {ok}/{n}  ({pct})")
    print("\nPer-probe:")
    for pid, cat, layer, status, pred, gold in rows:
        print(f"  [{status}] {pid:8s} {cat:16s} pred={pred} gold={gold}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--probes", default=None)
    args = ap.parse_args()
    data = load_probes(args.probes)
    rows, by_cat, by_layer = evaluate(data)
    report(rows, by_cat, by_layer)
   