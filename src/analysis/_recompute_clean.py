# -*- coding: utf-8 -*-
"""Recompute focused scores EXCLUDING genuinely-ambiguous probes, from existing
results files. Reports headline vs validity-filtered numbers side by side."""
import sys, io, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

# genuinely-ambiguous golds to drop (per pre-registered flags). Contrasts
# (f-N14/f-U05/f-U06), controls (f-C*), and hard-but-unambiguous (f-L12) are KEPT.
EXCLUDE_GROUPS = {"f-L07", "f-N07"}

MODELS = [("gemini-2.5-flash","25flash"), ("gemini-2.5-flash-lite","lite"),
          ("gpt-4o-mini","4omini"), ("qwen2.5:7b","qwen"), ("llama3.1:8b","llama")]
LINE = re.compile(r"\[(PASS|FAIL|ERR)\]\s+(\S+)\s+(\S+)\s+pred=")

with io.open(os.path.join(HERE,"probes_focus_seed.json"),encoding="utf-8") as f:
    meta = {p["id"]: p for p in json.load(f)["probes"]}

def readf(name):
    for enc in ("utf-8","utf-8-sig","utf-16"):
        try:
            with io.open(os.path.join(HERE,name),encoding=enc) as f: t=f.read()
            if "\x00" not in t: return t
        except Exception: pass
    return ""

excluded_ids = {pid for pid,m in meta.items() if m["variant_group"] in EXCLUDE_GROUPS}
print(f"Excluding {len(EXCLUDE_GROUPS)} groups ({len(excluded_ids)} probes): {sorted(EXCLUDE_GROUPS)}\n")

print(f"{'Model':24s} {'headline':>16s} {'validity-filtered':>20s}")
print("-"*64)
for mname,stem in MODELS:
    t = readf(f"results_{stem}_focus.txt")
    full_ok=full_n=clean_ok=clean_n=0
    for m in LINE.finditer(t):
        status,pid,cat = m.groups()
        if status=="ERR": continue
        full_n+=1; full_ok+=(status=="PASS")
        if pid in excluded_ids: continue
        clean_n+=1; clean_ok+=(status=="PASS")
    fp = 100*full_ok/full_n if full_n else 0
    cp = 100*clean_ok/clean_n if clean_n else 0
    print(f"{mname:24s} {full_ok:>3}/{full_n:<3} ({fp:4.1f}%) {clean_ok:>4}/{clean_n:<3} ({cp:4.1f}%)")
print(f"\n(headline = all 108; validity-filtered = {108-len(excluded_ids)} probes, ambiguous golds removed)")
