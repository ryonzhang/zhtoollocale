# -*- coding: utf-8 -*-
import sys, io, os, re, ast
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
LINE = re.compile(r"\[(PASS|FAIL|ERR)\]\s+(\S+)\s+(\S+)\s+pred=(\{.*\})\s+gold=")

def load(name):
    for enc in ("utf-8","utf-8-sig","utf-16"):
        try:
            with io.open(os.path.join(HERE,name),encoding=enc) as f: t=f.read()
            if "\x00" not in t: break
        except Exception: pass
    d={}
    for m in LINE.finditer(t):
        st,pid,cat,pred=m.groups()
        try: pv=ast.literal_eval(pred)
        except Exception: pv={"_":pred}
        d[pid]=(st,pv)
    return d

def norm(v):
    if isinstance(v,dict): return tuple(sorted((k,norm(x)) for k,x in v.items()))
    if isinstance(v,float) and v.is_integer(): return int(v)
    return v

r1=load("results_25flash_focus.txt"); r2=load("results_25flash_focus_rep2.txt")
ids=sorted(set(r1)&set(r2))
same_pred=sum(1 for i in ids if norm(r1[i][1])==norm(r2[i][1]))
same_status=sum(1 for i in ids if r1[i][0]==r2[i][0])
print(f"probes compared: {len(ids)}")
print(f"identical prediction run1==run2: {same_pred}/{len(ids)} ({100*same_pred/len(ids):.1f}%)")
print(f"identical PASS/FAIL status:      {same_status}/{len(ids)} ({100*same_status/len(ids):.1f}%)")
print("\ndisagreements (pred differs):")
for i in ids:
    if norm(r1[i][1])!=norm(r2[i][1]):
        print(f"  {i:8s} run1={r1[i][1]}  run2={r2[i][1]}")
