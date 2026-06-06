# -*- coding: utf-8 -*-
"""Phase 5 — publication figures from figures_data.json. 300dpi PNG+PDF,
grayscale-safe (distinct gray fills + hatches), no in-image titles."""
import io, os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(HERE,"figures_paper"); os.makedirs(OUT,exist_ok=True)
plt.rcParams.update({"font.size":9,"axes.linewidth":0.8})
D=json.load(io.open(os.path.join(HERE,"figures_data.json"),encoding="utf-8"))
stems=D["models"]; labels=[n.replace("gemini-","").replace(":7b","").replace(":8b","").replace("3.1","-3.1") for n in D["model_names"]]
# grayscale-safe palette
GRAYS=["0.15","0.35","0.5","0.65","0.8","0.92"]
HATCH=["", "///","...","xxx","\\\\\\","ooo"]
def save(fig,name):
    fig.savefig(os.path.join(OUT,name+".png"),dpi=300,bbox_inches="tight")
    fig.savefig(os.path.join(OUT,name+".pdf"),bbox_inches="tight")
    plt.close(fig)

# ---- Fig 1: lunar decomposition ----
types=D["lunar_types"]; nT=len(types); nM=len(stems)
fig,ax=plt.subplots(figsize=(9,3.6))
x=np.arange(nT); w=0.8/nM
for j,stem in enumerate(stems):
    vals=[(D["lunar"][t][stem] if D["lunar"][t][stem] is not None else 0) for t in types]
    ax.bar(x+j*w-0.4+w/2, vals, w, color=GRAYS[j%len(GRAYS)], hatch=HATCH[j%len(HATCH)],
           edgecolor="black", linewidth=0.5, label=labels[j])
# separate controls with a vertical line (first control index)
ctrl_start=next((i for i,t in enumerate(types) if t.startswith("control")), None)
if ctrl_start: ax.axvline(ctrl_start-0.5, color="black", ls="--", lw=1)
def clean(t):
    t=t.replace("control:清明(solar)","Qingming\n(solar-term)").replace("control:国庆(fixed)","NationalDay\n(fixed)").replace("control:圣诞(fixed)","Christmas\n(fixed)")
    return t
ax.set_xticks(x); ax.set_xticklabels([clean(t) for t in types], fontsize=7.5)
ax.set_ylabel("baseline accuracy (%)"); ax.set_ylim(0,105)
ax.legend(ncol=3, fontsize=7, loc="upper left", framealpha=0.9)
ax.text(ctrl_start-0.5+0.05, 100, "fixed/solar controls →", fontsize=7, style="italic") if ctrl_start else None
save(fig,"fig1_lunar_decomp")

# ---- Fig 2: routing gradient ----
conds=["baseline","available","forced"]; cg=["0.75","0.45","0.15"]; ch=["","//","xx"]
fig,ax=plt.subplots(figsize=(8,3.6))
x=np.arange(nM); w=0.26
for k,cond in enumerate(conds):
    vals=[(D["routing"][s].get(cond) or 0) for s in stems]
    bars=ax.bar(x+(k-1)*w, vals, w, color=cg[k], hatch=ch[k], edgecolor="black", linewidth=0.5, label=cond.upper())
    if cond in ("available","forced"):
        for i,s in enumerate(stems):
            r=D["routing"][s].get("route_"+cond)
            if r is not None:
                ax.text(x[i]+(k-1)*w, (D["routing"][s].get(cond) or 0)+1.5, f"{r:.0f}%", ha="center", fontsize=6.5, rotation=90)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
ax.set_ylabel("accuracy on locale-sensitive probes (%)"); ax.set_ylim(0,108)
ax.legend(fontsize=8, loc="upper right"); ax.set_axisbelow(True); ax.grid(axis="y",lw=0.3,alpha=0.5)
ax.text(0.0,103,"routing% annotated above AVAILABLE/FORCED bars",fontsize=6.5,style="italic")
save(fig,"fig2_routing_gradient")

# ---- Fig 3: memorization control — name-acc vs date-acc (decisive cell = 0) ----
fig,ax=plt.subplots(figsize=(5.0,3.2))
ms=[s for s in stems if s in D["memo"]]; ml=[labels[stems.index(s)] for s in ms]
nacc=[D["memo"][s]["name_acc"] for s in ms]; dacc=[D["memo"][s]["date_acc"] for s in ms]
x=np.arange(len(ms)); w=0.38
ax.bar(x-w/2, nacc, w, color="0.65", hatch="", edgecolor="black", linewidth=0.5, label="festival NAME")
ax.bar(x+w/2, dacc, w, color="0.30", hatch="//", edgecolor="black", linewidth=0.5, label="explicit lunar DATE")
ax.set_xticks(x); ax.set_xticklabels(ml, fontsize=7.5, rotation=20, ha="right")
ax.set_ylabel("baseline accuracy on matched pairs (%)"); ax.set_ylim(0,max(nacc+dacc+[10])*1.3)
ax.legend(fontsize=7.5, loc="upper right")
ax.text(-0.4, max(nacc+dacc+[10])*1.18, "decisive cell name✓&date✗ = 0 for all models (no memorization signal)",
        fontsize=6.5, style="italic")
save(fig,"fig3_memorization")

print("wrote figures to figures_paper/:", sorted(os.listdir(OUT)))
