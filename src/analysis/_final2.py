# -*- coding: utf-8 -*-
"""Compile FINAL_RESULTS_v2.md — STRONG-ACCEPT pack.
Canonical: official deepseek-chat (api.deepseek.com).
Adds bootstrap CIs, significance tests, llama routing, memo-control contingency."""
import sys, io, os, re, ast, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
from harness import args_match
from collections import Counter, defaultdict
import _stats as S

EXCLUDE={"f-L07"}
# canonical 6 models
MATRIX=[("gemini-2.5-flash","25flash"),("gemini-2.5-flash-lite","lite"),
        ("gpt-4o-mini","4omini"),("deepseek-chat","dschat"),
        ("qwen2.5:7b","qwen"),("llama3.1:8b","llama")]
ROUTE=MATRIX[:]                       # all six routed (llama added, Phase 2)
MEMO=[("gemini-2.5-flash","25flash"),("gemini-2.5-flash-lite","lite"),
      ("gpt-4o-mini","4omini"),("deepseek-chat","dschat"),("qwen2.5:7b","qwen")]
FAMS=["lunar","internal_zero","elliptical","capital","mixed_digit","long_chain","units_half"]
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
def rescore_txt(name, drop_excl=True):
    out={}
    for m in LINE.finditer(readf(name)):
        st,pid,cat,pred,gold=m.groups()
        if drop_excl and META.get(pid,{}).get("variant_group") in EXCLUDE: continue
        try: pv=ast.literal_eval(pred)
        except Exception: pv={}
        try: gv=ast.literal_eval(gold)
        except Exception: gv={}
        if isinstance(pv,dict) and ("__api_error__" in pv or not pv): out[pid]=("ERR",pv,gv); continue
        out[pid]=("PASS" if args_match(pv,gv) else "FAIL",pv,gv)
    return out
def route_rows(tag,cond):
    p=os.path.join(HERE,f"routing_{tag}_{cond}.json")
    if not os.path.exists(p): return None
    j=json.load(io.open(p,encoding="utf-8")); rows=[]
    for r in j["rows"]:
        if META.get(r["id"],{}).get("variant_group") in EXCLUDE: continue
        f=r["final"]
        st="ERR" if (isinstance(f,dict) and ("__api_error__" in f or not f)) else ("PASS" if args_match(f,r["gold"]) else "FAIL")
        rows.append((r["id"],r["family"],st,r.get("calls",[])))
    return rows

# cache focused/tier1
FOC={}; T1={}
for mname,stem in MATRIX:
    FOC[stem]=rescore_txt(f"results_{stem}_focus.txt"); T1[stem]=rescore_txt(f"results_{stem}_tier1.txt")
def vec(d, fam=None, control=None):
    out=[]
    for pid,(s,pv,gv) in d.items():
        if s=="ERR": continue
        f=META.get(pid,{}).get("family")
        if fam and f!=fam: continue
        if control=="fixed" and META.get(pid,{}).get("variant_group") not in ("f-C2","f-C3"): continue
        out.append(1 if s=="PASS" else 0)
    return out

out=[]; W=out.append
W("# ZhToolLocale — FINAL_RESULTS_v2.md (STRONG-ACCEPT pack)\n")
W("Reference 2026-06-05 (Fri), temp 0. `[ERR]` excluded from num+denom. f-L07 removed. "
  "Tool-call envelopes unwrapped. **Canonical DeepSeek = official `deepseek-chat` "
  "(api.deepseek.com)**. Bootstrap CIs: "
  "10,000 resamples, seed 12345.\n")

# 1. master matrix with CI
W("## 1. Master matrix (tier-1 / focused) with 95% bootstrap CIs\n")
W("| Model | tier-1 | focused (105) |")
W("|---|---|---|")
for mname,stem in MATRIX:
    t=[1 if s=='PASS' else 0 for s,_,_ in T1[stem].values() if s!='ERR']
    f=[1 if s=='PASS' else 0 for s,_,_ in FOC[stem].values() if s!='ERR']
    W(f"| `{mname}` | {S.fmt_ci(*S.boot_ci(t))} | {S.fmt_ci(*S.boot_ci(f))} |")
W("\n_deepseek-chat is the canonical Chinese-native model alongside qwen2.5:7b._\n")

# 2. routing with CI (incl llama)
W("## 2. Routing experiment with CIs — incl. llama3.1:8b (Phase 2)\n")
W("| Model | BASELINE | AVAILABLE | FORCED | routing% av→fo |")
W("|---|---|---|---|---|")
route_cache={}
for mname,stem in ROUTE:
    base=vec({k:v for k,v in FOC[stem].items() if META[k]['family']!='control'})
    cells=[S.fmt_ci(*S.boot_ci(base))]; rr=[]
    for cond in ("available","forced"):
        rows=route_rows(stem,cond); route_cache[(stem,cond)]=rows
        if not rows: cells.append("—"); rr.append("—"); continue
        v=[1 if s=='PASS' else 0 for _,_,s,_ in rows if s!='ERR']
        e=sum(1 for _,_,s,_ in rows if s=='ERR'); rd=sum(1 for _,_,_,c in rows if c)
        cells.append(S.fmt_ci(*S.boot_ci(v))+(f" ({e}err)" if e else "")); rr.append(f"{100*rd/len(rows):.0f}%")
    W(f"| `{mname}` | {cells[0]} | {cells[1]} | {cells[2]} | {rr[0]}→{rr[1]} |")

# 3. memorization contingency (Phase 3)
W("\n## 3. Memorization matched-pair control (Phase 3) — BASELINE, no tools\n")
W("Gold table (lunardate, next occurrence ≥ 2026-06-05): 中秋 2026-09-25 · 春节 2027-02-06 · "
  "端午 2026-06-19 · 元宵 2027-02-20 · 重阳 2026-10-18. Name-version and date-version of each "
  "pair share the identical gold.\n")
W("| Model | name✓&date✓ | **name✓&date✗** | name✗&date✓ | both✗ | name-acc | date-acc |")
W("|---|---|---|---|---|---|---|")
memo_decisive={}
for mname,stem in MEMO:
    d=rescore_txt(f"results_memo_{stem}.txt", drop_excl=False)
    nr_dr=nr_dw=nw_dr=nw_dw=0; nacc=dacc=ntot=0
    for fest in ("中秋","春节","端午","元宵","重阳"):
        for para in ("a","b"):
            nid=f"m-{fest}-name-{para}"; did=f"m-{fest}-date-{para}"
            if nid not in d or did not in d: continue
            nok=d[nid][0]=="PASS"; dok=d[did][0]=="PASS"
            ntot+=1; nacc+=nok; dacc+=dok
            if nok and dok: nr_dr+=1
            elif nok and not dok: nr_dw+=1
            elif not nok and dok: nw_dr+=1
            else: nw_dw+=1
    memo_decisive[mname]=(nr_dw, nw_dr, ntot, nacc, dacc)
    na=f"{100*nacc/ntot:.0f}%" if ntot else "—"; da=f"{100*dacc/ntot:.0f}%" if ntot else "—"
    W(f"| `{mname}` | {nr_dr} | **{nr_dw}** | {nw_dr} | {nw_dw} | {na} | {da} |")
tot_dec=sum(v[0] for v in memo_decisive.values()); tot_rev=sum(v[1] for v in memo_decisive.values())
W(f"\n_**RESULT (report as-is): the pre-registered decisive cell name✓&date✗ = {tot_dec} across "
  f"ALL models — i.e. NO memorization signal.** The reverse cell name✗&date✓ = {tot_rev} (non-zero): "
  "where the two differ, the explicit 农历 date is EASIER than the festival name (e.g. flash on 元宵: "
  "name→2026-03-03 = last-passed instance, wrong year; date 农历正月十五→2027-02-20 correct). "
  "The festival NAME adds a year-disambiguation step that triggers recall of a past instance. "
  "⇒ The matched-pair control does NOT support 'recall-not-conversion'; failure is uniform "
  "conversion difficulty. See CLAIMS_TO_SOFTEN._\n")

# 4. significance + CLAIMS_TO_SOFTEN
W("## 4. Significance tests (bootstrap, 10k) \n")
soften=[]
W("### 4a. BASELINE vs AVAILABLE (routing), paired on shared probes")
W("| Model | Δacc (avail−base) | 95% CI | p |")
W("|---|---|---|---|")
for mname,stem in ROUTE:
    rows=route_cache.get((stem,"available"))
    if not rows: continue
    # align on probes present & non-ERR in both baseline(focused) and available
    av={pid:(1 if s=='PASS' else 0) for pid,fam,s,_ in rows if s!='ERR'}
    bl={pid:(1 if v[0]=='PASS' else 0) for pid,v in FOC[stem].items() if v[0]!='ERR' and META[pid]['family']!='control'}
    common=[pid for pid in av if pid in bl]
    x=[av[p] for p in common]; y=[bl[p] for p in common]
    diff,lo,hi,p=S.paired_p(x,y)
    sig="" if p<0.05 else "  (NS)"
    W(f"| `{mname}` | {100*diff:+.1f} | [{100*lo:+.0f},{100*hi:+.0f}] | {p:.4f}{sig} |")
    if not (p<0.05 and diff>0):
        soften.append(f"routing helps {mname}: Δ={100*diff:+.1f}pp, p={p:.3f}")

W("\n### 4b. flash vs lite focused (unpaired)")
xf=[1 if s=='PASS' else 0 for s,_,_ in FOC['25flash'].values() if s!='ERR']
xl=[1 if s=='PASS' else 0 for s,_,_ in FOC['lite'].values() if s!='ERR']
diff,lo,hi,p=S.unpaired_p(xf,xl)
W(f"flash−lite focused Δ={100*diff:+.1f}pp, 95% CI [{100*lo:+.0f},{100*hi:+.0f}], p={p:.4f}"+("" if p<0.05 else "  (NS)"))
if p>=0.05: soften.append(f"flash>lite focused: p={p:.3f} (NS)")

W("\n### 4c. lunar vs fixed-date-control accuracy within each model (unpaired)")
W("| Model | lunar acc | fixed-control acc | Δ | p |")
W("|---|---|---|---|---|")
for mname,stem in MATRIX:
    lv=vec(FOC[stem],fam="lunar"); cv=vec(FOC[stem],control="fixed")
    if not lv or not cv: continue
    diff,lo,hi,p=S.unpaired_p(cv,lv)  # control - lunar
    W(f"| `{mname}` | {100*sum(lv)/len(lv):.0f}% | {100*sum(cv)/len(cv):.0f}% | {100*diff:+.0f} | {p:.4f}"+("" if p<0.05 else "  (NS)")+" |")
    if p>=0.05: soften.append(f"{mname}: lunar<fixed-control not significant (p={p:.3f})")

if tot_dec==0:
    soften.insert(0, f"**MEMORIZATION ('recall-not-conversion') — NOT SUPPORTED.** Matched-pair "
      f"decisive cell name✓&date✗ = 0 across all {len(MEMO)} models; reverse cell name✗&date✓ "
      f"= {tot_rev}. Explicit 农历 dates are if anything EASIER than festival names. Drop the "
      "memorization framing; the lunar failure is uniform conversion difficulty (routing result unaffected).")
W("\n### CLAIMS_TO_SOFTEN (not supported by the data)")
if soften:
    for s in soften: W(f"- {s}")
else:
    W("- (all tested claims significant at p<.05)")
W("")

# 5. lunar decomposition (canonical, deepseek-chat)
W("## 5. Lunar decomposition by type × model (baseline focused)\n")
TYPE={"f-L01":"famous+hint","f-L06":"famous+hint","f-L02":"name-only","f-L03":"name-only",
      "f-L04":"name-only","f-L05":"name-only","f-L08":"name-only","f-L09":"name-only","f-L13":"name-only",
      "f-L10":"pure-lunar-date","f-L11":"pure-lunar-date","f-L12":"leap-month",
      "f-C1":"control:清明(solar)","f-C2":"control:国庆(fixed)","f-C3":"control:圣诞(fixed)"}
TYPES=["famous+hint","name-only","pure-lunar-date","leap-month","control:清明(solar)","control:国庆(fixed)","control:圣诞(fixed)"]
W("| Type | "+" | ".join(s for _,s in MATRIX)+" |")
W("|---|"+"---|"*len(MATRIX))
for typ in TYPES:
    row=[typ]
    for mname,stem in MATRIX:
        ok=n=0
        for pid,(s,pv,gv) in FOC[stem].items():
            if TYPE.get(META[pid]["variant_group"])!=typ or s=="ERR": continue
            n+=1; ok+=(s=="PASS")
        row.append(f"{100*ok/n:.0f}%" if n else "—")
    W("| "+" | ".join(row)+" |")

# 6. determinism
W("\n## 6. Determinism (20 probes × 3, temp 0)\n")
W("| Model | identical/total | % |")
W("|---|---|---|")
for mname,stem in (("gemini-2.5-flash","25flash"),("qwen2.5:7b","qwen")):
    runs=[]
    for r in (1,2,3):
        dd={}
        for m in LINE.finditer(readf(f"results_det_{stem}_r{r}.txt")):
            st,pid,cat,pred,gold=m.groups()
            try: dd[pid]=norm(ast.literal_eval(pred))
            except Exception: dd[pid]=None
        runs.append(dd)
    ids=set(runs[0])&set(runs[1])&set(runs[2])
    same=sum(1 for i in ids if runs[0][i]==runs[1][i]==runs[2][i])
    W(f"| `{mname}` | {same}/{len(ids)} | {100*same/len(ids):.0f}% |" if ids else f"| `{mname}` | — | — |")

# 7. figures + repro
W("\n## 7. Figure files (Phase 5) & reproducibility (Phase 6)\n")
W("- `figures_paper/fig1_lunar_decomp.{png,pdf}` — lunar decomposition, type×model, controls separated.")
W("- `figures_paper/fig2_routing_gradient.{png,pdf}` — BASELINE/AVAILABLE/FORCED per model, routing% annotated.")
W("- `figures_paper/fig3_memorization.{png,pdf}` — name✓&date✗ rate per model.")
W("- `repro_manifest.md` — exact model/endpoint/version pins, library versions, OS, git commit.")

# 8. changelog
W("\n## 8. Changelog\n")
W("- **DeepSeek:** official **deepseek-chat** (api.deepseek.com) used across tier-1/focused/routing/hint/memo.")
W("- **llama3.1:8b added to routing (Phase 2):** second 7–8B model; confirms the low-routing finding.")
W("- **Memorization control added (Phase 3):** matched name/date pairs, decisive name✓&date✗ cell.")
W("- **CIs + significance added (Phase 4):** all matrix/routing cells now have 95% bootstrap CIs; "
  "see CLAIMS_TO_SOFTEN for anything not significant at p<.05.")
W("- **Figures (Phase 5) + repro manifest (Phase 6)** generated.")

# ---- dump figures_data.json (decouples plotting) ----
figdata={"models":[s for _,s in MATRIX],"model_names":[m for m,_ in MATRIX],
         "lunar_types":TYPES,"lunar":{}, "routing":{}, "memo":{}}
for typ in TYPES:
    figdata["lunar"][typ]={}
    for mname,stem in MATRIX:
        ok=n=0
        for pid,(s,pv,gv) in FOC[stem].items():
            if TYPE.get(META[pid]["variant_group"])!=typ or s=="ERR": continue
            n+=1; ok+=(s=="PASS")
        figdata["lunar"][typ][stem]=(100*ok/n if n else None)
for mname,stem in ROUTE:
    base=vec({k:v for k,v in FOC[stem].items() if META[k]['family']!='control'})
    d={"baseline":100*sum(base)/len(base) if base else None}
    for cond in ("available","forced"):
        rows=route_cache.get((stem,cond))
        if rows:
            v=[1 if s=='PASS' else 0 for _,_,s,_ in rows if s!='ERR']
            d[cond]=100*sum(v)/len(v) if v else None
            d["route_"+cond]=100*sum(1 for _,_,_,c in rows if c)/len(rows)
        else: d[cond]=None; d["route_"+cond]=None
    figdata["routing"][stem]=d
for mname,stem in MEMO:
    nr_dw,nw_dr,ntot,nacc,dacc=memo_decisive[mname]
    figdata["memo"][stem]={"name":mname,"rate":100*nr_dw/ntot if ntot else 0,"nr_dw":nr_dw,
        "nw_dr":nw_dr,"ntot":ntot,"name_acc":100*nacc/ntot if ntot else 0,"date_acc":100*dacc/ntot if ntot else 0}
json.dump(figdata, io.open(os.path.join(HERE,"figures_data.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)

io.open(os.path.join(HERE,"FINAL_RESULTS_v2.md"),"w",encoding="utf-8").write("\n".join(out)+"\n")
print("FINAL_RESULTS_v2.md written:", len(out), "lines")
print("memo decisive (name-right&date-wrong):", {k:v for k,v in memo_decisive.items()})
