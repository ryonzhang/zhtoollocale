# -*- coding: utf-8 -*-
"""STEP 6 — reviewer-fix additions from existing saved outputs. No new API calls.
A: deepseek-chat A1/A2/deployment. B: FORCED-vs-BASELINE paired test all models.
C: deepseek-chat hint deltas. Additions only — canonical cells untouched."""
import sys, io, os, re, ast, json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8")
HERE=os.path.dirname(os.path.abspath(__file__))
from harness import args_match
from collections import Counter, defaultdict
import _stats as S

EXCLUDE={"f-L07"}
FAMS=["lunar","internal_zero","elliptical","capital","mixed_digit","long_chain","units_half"]
ROUTE=[("gemini-2.5-flash","25flash"),("gemini-2.5-flash-lite","lite"),
       ("gpt-4o-mini","4omini"),("deepseek-chat","dschat"),("qwen2.5:7b","qwen"),("llama3.1:8b","llama")]
LINE=re.compile(r"\[(PASS|FAIL|ERR)\]\s+(\S+)\s+(\S+)\s+pred=(\{.*\})\s+gold=(\{.*\})")
META={p["id"]:p for p in json.load(io.open(os.path.join(HERE,"probes_focus_seed.json"),encoding="utf-8"))["probes"]}
GROUPS=defaultdict(list)
for pid,p in META.items(): GROUPS[p["variant_group"]].append(pid)

def readf(n):
    for enc in ("utf-8","utf-8-sig","utf-16"):
        try:
            with io.open(os.path.join(HERE,n),encoding=enc) as f: t=f.read()
            if "\x00" not in t: return t
        except Exception: pass
    return ""
def norm(v):
    if isinstance(v,dict): return tuple(sorted((k,norm(x)) for k,x in v.items() if k!="__api_error__"))
    if isinstance(v,float) and v.is_integer(): return int(v)
    return v
def rescore(name):
    out={}
    for m in LINE.finditer(readf(name)):
        st,pid,cat,pred,gold=m.groups()
        if META.get(pid,{}).get("variant_group") in EXCLUDE: continue
        try: pv=ast.literal_eval(pred); gv=ast.literal_eval(gold)
        except Exception: continue
        if isinstance(pv,dict) and ("__api_error__" in pv or not pv): out[pid]=("ERR",pv,gv); continue
        out[pid]=("PASS" if args_match(pv,gv) else "FAIL",pv,gv)
    return out
def route_rows(tag,cond):
    p=os.path.join(HERE,f"routing_{tag}_{cond}.json")
    if not os.path.exists(p): return None
    j=json.load(io.open(p,encoding="utf-8")); rows={}
    for r in j["rows"]:
        if META.get(r["id"],{}).get("variant_group") in EXCLUDE: continue
        f=r["final"]
        st="ERR" if (isinstance(f,dict) and ("__api_error__" in f or not f)) else ("PASS" if args_match(f,r["gold"]) else "FAIL")
        rows[r["id"]]=st
    return rows
def fam_of(grp): return META[GROUPS[grp][0]]["family"]
def band(p): return "SAFE" if p>=95 else ("CAUTION" if p>=80 else "UNSAFE")

out=[]; W=out.append
W("# REVIEWER_FIXES.md (STEP 6 — additions only, from saved raw outputs)\n")
W("No new API calls. f-L07 excluded, envelopes unwrapped, [ERR] excluded — same conventions "
  "as FINAL_RESULTS_v2.md. These are ADDITIONS; no existing canonical cell changes.\n")

# ===== TASK A — deepseek-chat A1/A2/deployment =====
foc=rescore("results_dschat_focus.txt")
groups={}
for grp,ids in GROUPS.items():
    if grp in EXCLUDE: continue
    vs=[(foc[i][0],norm(foc[i][1])) for i in ids if i in foc and foc[i][0]!="ERR"]
    if vs: groups[grp]=vs

W("## A. deepseek-chat — detection & deployment (rows to ADD)\n")
# A1
AR=AW=DR=DW=0
for grp,vs in groups.items():
    if len(vs)<2: continue
    dis=len({p for _,p in vs})>1; wrong=sum(1 for s,_ in vs if s=="FAIL")>=2
    if dis and wrong: DW+=1
    elif dis: DR+=1
    elif wrong: AW+=1
    else: AR+=1
prec=DW/(DW+DR) if DW+DR else float('nan'); rec=DW/(DW+AW) if DW+AW else float('nan')
W("**A1 disagreement-as-detector** (append to A1 table):")
W("| Model | A&R | A&W | D&R | D&W | prec=P(WRONG\\|DISAGREE) | rec=P(DISAGREE\\|WRONG) |")
W("|---|---|---|---|---|---|---|")
W(f"| `deepseek-chat` | {AR} | {AW} | {DR} | {DW} | {prec:.2f} | {rec:.2f} |")

# A2
per={f:0 for f in FAMS}; tot=0
for grp,vs in groups.items():
    if len(vs)<2: continue
    if len({p for _,p in vs})==1 and all(s=="FAIL" for s,_ in vs):
        f=fam_of(grp)
        if f in per: per[f]+=1; tot+=1
W("\n**A2 consistent-but-WRONG by category** (append to A2 table):")
W("| Model | "+" | ".join(FAMS)+" | TOT |")
W("|---|"+"---|"*(len(FAMS)+1))
W(f"| `deepseek-chat` | "+" | ".join(str(per[f]) for f in FAMS)+f" | {tot} |")

# A4 deployment
W("\n**A4 deployment card** (deepseek-chat column / per-family band):")
W("| family | deepseek-chat |")
W("|---|---|")
for fam in FAMS:
    ok=n=0
    for pid,(s,pv,gv) in foc.items():
        if META[pid]["family"]!=fam or s=="ERR": continue
        n+=1; ok+=(s=="PASS")
    W(f"| {fam} | {band(100*ok/n) if n else '—'} ({100*ok/n:.0f}%) |")

# ===== TASK B — FORCED vs BASELINE paired, all models =====
W("\n## B. FORCED − BASELINE paired bootstrap (10k, seed 12345) — all models\n")
W("Baseline = focused locale-sensitive (no tools); paired on probes present & non-ERR in both.\n")
W("| Model | AVAILABLE−BASE Δ (p) | **FORCED−BASE Δ** | 95% CI | p |")
W("|---|---|---|---|---|")
AVAIL_P={"25flash":("+27.1","0.0000"),"lite":("+6.5","0.0668"),"4omini":("+44.8","0.0000"),
         "dschat":("+7.3","0.0012"),"qwen":("-1.1","0.8666"),"llama":("+1.1","0.8828")}
for mname,stem in ROUTE:
    fo=rescore(f"results_{stem}_focus.txt")
    bl={pid:(1 if s=='PASS' else 0) for pid,(s,_,_) in fo.items() if s!='ERR' and META[pid]['family']!='control'}
    fr=route_rows(stem,"forced")
    if not fr: W(f"| `{mname}` | — | — | — | — |"); continue
    frb={pid:(1 if st=='PASS' else 0) for pid,st in fr.items() if st!='ERR'}
    common=[pid for pid in frb if pid in bl]
    x=[frb[p] for p in common]; y=[bl[p] for p in common]
    diff,lo,hi,p=S.paired_p(x,y)
    av=AVAIL_P.get(stem,("—","—"))
    hl="**" if stem=="lite" else ""
    W(f"| {hl}`{mname}`{hl} | {av[0]}pp (p={av[1]}) | {hl}{100*diff:+.1f}pp{hl} | [{100*lo:+.0f},{100*hi:+.0f}] | {p:.4f}"+("" if p<0.05 else "  (NS)")+" |")
W("\n_lite highlighted: AVAILABLE−BASE was NS (p=.067); FORCED−BASE shown above._")

# ===== TASK C — deepseek-chat hint deltas =====
W("\n## C. deepseek-chat — hint-injection per-family deltas vs baseline\n")
hint=rescore("results_hint_dschat.txt")
W("| family | baseline | +hint | delta |")
W("|---|---|---|---|")
for fam in FAMS:
    bok=bn=hok=hn=0
    for pid,(s,_,_) in foc.items():
        if META[pid]["family"]==fam and s!="ERR": bn+=1; bok+=(s=="PASS")
    for pid,(s,_,_) in hint.items():
        if META[pid]["family"]==fam and s!="ERR": hn+=1; hok+=(s=="PASS")
    if bn and hn:
        W(f"| {fam} | {100*bok/bn:.0f}% | {100*hok/hn:.0f}% | {100*hok/hn-100*bok/bn:+.0f} |")
    else: W(f"| {fam} | — | — | — |")

# ===== confirmation =====
W("\n## D. Canonical-tables confirmation\n")
W("- ✅ These are **additions only** (one new model row in A1/A2/deployment, one new column "
  "in the routing significance table, one new hint sub-table). **No value in any existing "
  "FINAL_RESULTS_v2.md canonical table was modified** — the same saved raw outputs and the "
  "same scoring (args_match w/ envelope unwrap, f-L07 excluded, [ERR] excluded) were re-read.")

io.open(os.path.join(HERE,"REVIEWER_FIXES.md"),"w",encoding="utf-8").write("\n".join(out)+"\n")
print("REVIEWER_FIXES.md written:", len(out), "lines")
