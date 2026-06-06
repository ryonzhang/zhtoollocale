# -*- coding: utf-8 -*-
import io, os, json
HERE=os.path.dirname(os.path.abspath(__file__))
sel=["f-L01-a","f-L02-a","f-L05-a","f-L10-a","f-L12-a",      # lunar (5)
     "f-N01-a","f-N02-a","f-N04-a",                          # internal_zero (3)
     "f-N05-a","f-N06-a","f-N07-a",                          # elliptical (3)
     "f-N08-a","f-N10-a","f-N12-a","f-N13-a",                # capital/mixed/long (4)
     "f-U01-a","f-U02-a","f-U04-a","f-U06-a",                # units (4)
     "f-C1-a"]                                               # control (1)
d=json.load(io.open(os.path.join(HERE,"probes_focus_seed.json"),encoding="utf-8"))
sub=[p for p in d["probes"] if p["id"] in sel]
out=dict(d); out["benchmark"]="ZhToolLocale-det20"; out["probes"]=sub
json.dump(out, io.open(os.path.join(HERE,"probes_det20.json"),"w",encoding="utf-8"),
          ensure_ascii=False,indent=1)
print(f"det20: {len(sub)} probes across families:",
      sorted({p['family'] for p in sub}))
