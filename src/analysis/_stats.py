# -*- coding: utf-8 -*-
"""Bootstrap CIs + significance tests (Phase 4). Reusable helpers operating on
0/1 outcome arrays. Fixed seed for reproducibility."""
import numpy as np
SEED=12345; ITERS=10000

def boot_ci(vals, iters=ITERS, seed=SEED):
    a=np.asarray(vals,float)
    if len(a)==0: return (float('nan'),float('nan'),float('nan'))
    rng=np.random.default_rng(seed); n=len(a)
    means=a[rng.integers(0,n,size=(iters,n))].mean(axis=1)
    return float(a.mean()), float(np.percentile(means,2.5)), float(np.percentile(means,97.5))

def paired_p(x, y, iters=ITERS, seed=SEED):
    """x,y aligned 0/1 arrays (same probes). Returns (obs_diff, lo, hi, p) for x-y."""
    x=np.asarray(x,float); y=np.asarray(y,float); d=x-y; n=len(d)
    rng=np.random.default_rng(seed)
    bs=d[rng.integers(0,n,size=(iters,n))].mean(axis=1)
    lo,hi=np.percentile(bs,2.5),np.percentile(bs,97.5)
    p=2*min((bs<=0).mean(),(bs>=0).mean()); p=min(1.0,float(p))
    return float(d.mean()), float(lo), float(hi), p

def unpaired_p(x, y, iters=ITERS, seed=SEED):
    """independent 0/1 arrays. Returns (obs_diff, lo, hi, p) for mean(x)-mean(y)."""
    x=np.asarray(x,float); y=np.asarray(y,float)
    rng=np.random.default_rng(seed)
    bx=x[rng.integers(0,len(x),size=(iters,len(x)))].mean(axis=1)
    by=y[rng.integers(0,len(y),size=(iters,len(y)))].mean(axis=1)
    bs=bx-by; lo,hi=np.percentile(bs,2.5),np.percentile(bs,97.5)
    p=2*min((bs<=0).mean(),(bs>=0).mean()); p=min(1.0,float(p))
    return float(x.mean()-y.mean()), float(lo), float(hi), p

def fmt_ci(mean,lo,hi):
    return f"{100*mean:.1f}% [{100*lo:.0f}–{100*hi:.0f}]"
