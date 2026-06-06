# REVIEWER_FIXES.md (STEP 6 — additions only, from saved raw outputs)

No new API calls. f-L07 excluded, envelopes unwrapped, [ERR] excluded — same conventions as FINAL_RESULTS_v2.md. These are ADDITIONS; no existing canonical cell changes.

## A. deepseek-chat — detection & deployment (rows to ADD)

**A1 disagreement-as-detector** (append to A1 table):
| Model | A&R | A&W | D&R | D&W | prec=P(WRONG\|DISAGREE) | rec=P(DISAGREE\|WRONG) |
|---|---|---|---|---|---|---|
| `deepseek-chat` | 32 | 2 | 1 | 0 | 0.00 | 0.00 |

**A2 consistent-but-WRONG by category** (append to A2 table):
| Model | lunar | internal_zero | elliptical | capital | mixed_digit | long_chain | units_half | TOT |
|---|---|---|---|---|---|---|---|---|
| `deepseek-chat` | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |

**A4 deployment card** (deepseek-chat column / per-family band):
| family | deepseek-chat |
|---|---|
| lunar | CAUTION (81%) |
| internal_zero | SAFE (100%) |
| elliptical | SAFE (100%) |
| capital | SAFE (100%) |
| mixed_digit | SAFE (100%) |
| long_chain | SAFE (100%) |
| units_half | SAFE (100%) |

## B. FORCED − BASELINE paired bootstrap (10k, seed 12345) — all models

Baseline = focused locale-sensitive (no tools); paired on probes present & non-ERR in both.

| Model | AVAILABLE−BASE Δ (p) | **FORCED−BASE Δ** | 95% CI | p |
|---|---|---|---|---|
| `gemini-2.5-flash` | +27.1pp (p=0.0000) | +27.1pp | [+19,+36] | 0.0000 |
| **`gemini-2.5-flash-lite`** | +6.5pp (p=0.0668) | **+21.7pp** | [+13,+32] | 0.0000 |
| `gpt-4o-mini` | +44.8pp (p=0.0000) | +44.8pp | [+33,+56] | 0.0000 |
| `deepseek-chat` | +7.3pp (p=0.0012) | +7.3pp | [+2,+12] | 0.0012 |
| `qwen2.5:7b` | -1.1pp (p=0.8666) | -4.3pp | [-11,+1] | 0.2070  (NS) |
| `llama3.1:8b` | +1.1pp (p=0.8828) | -1.2pp | [-8,+6] | 0.8554  (NS) |

_lite highlighted: AVAILABLE−BASE was NS (p=.067); FORCED−BASE shown above._

## C. deepseek-chat — hint-injection per-family deltas vs baseline

| family | baseline | +hint | delta |
|---|---|---|---|
| lunar | 81% | 83% | +3 |
| internal_zero | 100% | 100% | +0 |
| elliptical | 100% | 100% | +0 |
| capital | 100% | 100% | +0 |
| mixed_digit | 100% | 100% | +0 |
| long_chain | 100% | 100% | +0 |
| units_half | 100% | 100% | +0 |

## D. Canonical-tables confirmation

- ✅ These are **additions only** (one new model row in A1/A2/deployment, one new column in the routing significance table, one new hint sub-table). **No value in any existing FINAL_RESULTS_v2.md canonical table was modified** — the same saved raw outputs and the same scoring (args_match w/ envelope unwrap, f-L07 excluded, [ERR] excluded) were re-read.
