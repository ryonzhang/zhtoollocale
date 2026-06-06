# -*- coding: utf-8 -*-
"""Phase 3 — build matched-pair memorization-control probes. Golds computed
via lunardate BEFORE any model run; name-version and date-version of a pair
share an identical gold (the next upcoming occurrence from ref 2026-06-05)."""
import io, os, json, datetime
from lunardate import LunarDate
HERE=os.path.dirname(os.path.abspath(__file__))
REF=datetime.date(2026,6,5)

# (festival, lunar_month, lunar_day, festival-name phrase, lunar-date phrase)
FEST=[
 ("中秋", 8,15, "中秋节",   "农历八月十五"),
 ("春节", 1, 1, "春节",     "农历正月初一"),
 ("端午", 5, 5, "端午节",   "农历五月初五"),
 ("元宵", 1,15, "元宵节",   "农历正月十五"),
 ("重阳", 9, 9, "重阳节",   "农历九月初九"),
]
def upcoming(m,d):
    """next occurrence of lunar (m,d) on/after REF."""
    for y in (2026,2027,2028):
        s=LunarDate(y,m,d).toSolarDate()
        if s>=REF: return s.isoformat()
    return None

# two paraphrase templates (shared between name and date versions)
TPL=["{X}那天帮我订一桌饭。", "帮我把{X}那天的饭订了。"]
TOOL="reserve_table(date: yyyy-mm-dd)"

probes=[]; goldtable=[]
for fest,m,d,namep,datep in FEST:
    gold=upcoming(m,d)
    goldtable.append((fest,m,d,namep,datep,gold))
    for vi,tpl in enumerate(TPL):
        sfx="ab"[vi]
        probes.append({"id":f"m-{fest}-name-{sfx}","category":"memo_name","pair":fest,
            "para":sfx,"variant_group":f"m-{fest}-name","layer":"arguments",
            "utterance_zh":tpl.format(X=namep),"tool":TOOL,"expected_args":{"date":gold}})
        probes.append({"id":f"m-{fest}-date-{sfx}","category":"memo_date","pair":fest,
            "para":sfx,"variant_group":f"m-{fest}-date","layer":"arguments",
            "utterance_zh":tpl.format(X=datep),"tool":TOOL,"expected_args":{"date":gold}})

data={"benchmark":"ZhToolLocale-memo","reference_date":"2026-06-05","reference_weekday":"Friday",
      "layers":["arguments"],"categories":["memo_name","memo_date"],"probes":probes}
json.dump(data, io.open(os.path.join(HERE,"probes_memo.json"),"w",encoding="utf-8"),
          ensure_ascii=False, indent=1)

import sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8")
print(f"Built probes_memo.json: {len(probes)} probes ({len(FEST)} festivals x name/date x 2 paraphrases)\n")
print("GOLD TABLE (computed via lunardate, next occurrence >= 2026-06-05):")
print(f"{'festival':10s} {'lunar':8s} {'name phrase':12s} {'date phrase':16s} {'gold':12s}")
for fest,m,d,namep,datep,gold in goldtable:
    print(f"{fest:10s} {str(m)+'/'+str(d):8s} {namep:12s} {datep:16s} {gold}")
print("\nWithin each pair, name-version and date-version share the SAME gold above.")
