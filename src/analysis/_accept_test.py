# -*- coding: utf-8 -*-
"""Deterministic acceptance test for the ERR-vs-FAIL harness patch (no network)."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from harness import load_probes, evaluate

data = load_probes("probes_seed.json")          # tier-1, 23 probes

# A) every call returns the api-error sentinel  -> all ERR, 0 scored
def err_call(utterance, tool_spec, prior_error=None):
    return {"__api_error__": "404 model-not-found (simulated)"}
rows, by_cat, by_layer = evaluate(data, call=err_call)
n_err = sum(1 for r in rows if r[3] == "ERR")
n_pass = sum(1 for r in rows if r[3] == "PASS")
n_fail = sum(1 for r in rows if r[3] == "FAIL")
scored_total = sum(n for _, n in by_cat.values())
print("A) all-error model:")
print(f"   rows={len(rows)}  ERR={n_err}  FAIL={n_fail}  PASS={n_pass}  scored(in by_cat)={scored_total}")
assert n_err == len(rows) and n_fail == 0 and n_pass == 0 and scored_total == 0, "FAILED A"
print("   PASS: all ERR, 0 scored, 0 counted as FAIL  ->  not 0%, but '0 scored'")

# B) a half-broken model: errors on odd probes, returns {} (wrong) on even
def mixed_call(utterance, tool_spec, prior_error=None):
    mixed_call.n += 1
    return {"__api_error__": "boom"} if mixed_call.n % 2 else {}
mixed_call.n = 0
rows, by_cat, by_layer = evaluate(data, call=mixed_call)
n_err = sum(1 for r in rows if r[3] == "ERR")
scored = sum(n for _, n in by_cat.values())
print("\nB) half-error model:")
print(f"   rows={len(rows)}  ERR={n_err}  scored(denominator)={scored}  (denominator EXCLUDES the {n_err} ERR)")
assert n_err + scored == len(rows), "FAILED B: ERR not excluded from denominator"
print("   PASS: errored probes excluded from denominator")

print("\nALL ACCEPTANCE CHECKS PASSED")
