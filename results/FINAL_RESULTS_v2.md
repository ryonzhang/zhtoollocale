# ZhToolLocale — FINAL_RESULTS_v2.md (STRONG-ACCEPT pack)

Reference 2026-06-05 (Fri), temp 0. `[ERR]` excluded from num+denom. f-L07 removed. Tool-call envelopes unwrapped. **Canonical DeepSeek = official `deepseek-chat` (api.deepseek.com)**. Bootstrap CIs: 10,000 resamples, seed 12345.

## 1. Master matrix (tier-1 / focused) with 95% bootstrap CIs

| Model | tier-1 | focused (105) |
|---|---|---|
| `gemini-2.5-flash` | 100.0% [100–100] | 75.2% [67–83] |
| `gemini-2.5-flash-lite` | 95.7% [87–100] | 60.0% [50–70] |
| `gpt-4o-mini` | 91.3% [78–100] | 54.3% [45–64] |
| `deepseek-chat` | 95.7% [87–100] | 93.3% [89–98] |
| `qwen2.5:7b` | 78.3% [61–96] | 55.9% [46–65] |
| `llama3.1:8b` | 47.8% [30–70] | 25.7% [18–34] |

_deepseek-chat is the canonical Chinese-native model alongside qwen2.5:7b._

## 2. Routing experiment with CIs — incl. llama3.1:8b (Phase 2)

| Model | BASELINE | AVAILABLE | FORCED | routing% av→fo |
|---|---|---|---|---|
| `gemini-2.5-flash` | 72.9% [64–81] | 100.0% [100–100] | 100.0% [100–100] | 93%→96% |
| `gemini-2.5-flash-lite` | 59.4% [50–69] | 66.3% [57–76] (4err) | 81.5% [73–89] (4err) | 41%→71% |
| `gpt-4o-mini` | 50.0% [40–59] | 94.8% [90–99] | 94.8% [90–99] | 97%→99% |
| `deepseek-chat` | 92.7% [88–98] | 100.0% [100–100] | 100.0% [100–100] | 99%→100% |
| `qwen2.5:7b` | 54.8% [44–65] | 54.2% [44–64] | 51.0% [42–60] | 3%→3% |
| `llama3.1:8b` | 25.0% [17–33] | 26.6% [18–36] (2err) | 26.2% [17–36] (12err) | 2%→10% |

## 3. Memorization matched-pair control (Phase 3) — BASELINE, no tools

Gold table (lunardate, next occurrence ≥ 2026-06-05): 中秋 2026-09-25 · 春节 2027-02-06 · 端午 2026-06-19 · 元宵 2027-02-20 · 重阳 2026-10-18. Name-version and date-version of each pair share the identical gold.

| Model | name✓&date✓ | **name✓&date✗** | name✗&date✓ | both✗ | name-acc | date-acc |
|---|---|---|---|---|---|---|
| `gemini-2.5-flash` | 3 | **0** | 3 | 4 | 30% | 60% |
| `gemini-2.5-flash-lite` | 0 | **0** | 0 | 10 | 0% | 0% |
| `gpt-4o-mini` | 0 | **0** | 0 | 10 | 0% | 0% |
| `deepseek-chat` | 3 | **0** | 1 | 6 | 30% | 40% |
| `qwen2.5:7b` | 0 | **0** | 0 | 10 | 0% | 0% |

_**RESULT (report as-is): the pre-registered decisive cell name✓&date✗ = 0 across ALL models — i.e. NO memorization signal.** The reverse cell name✗&date✓ = 4 (non-zero): where the two differ, the explicit 农历 date is EASIER than the festival name (e.g. flash on 元宵: name→2026-03-03 = last-passed instance, wrong year; date 农历正月十五→2027-02-20 correct). The festival NAME adds a year-disambiguation step that triggers recall of a past instance. ⇒ The matched-pair control does NOT support 'recall-not-conversion'; failure is uniform conversion difficulty. See CLAIMS_TO_SOFTEN._

## 4. Significance tests (bootstrap, 10k) 

### 4a. BASELINE vs AVAILABLE (routing), paired on shared probes
| Model | Δacc (avail−base) | 95% CI | p |
|---|---|---|---|
| `gemini-2.5-flash` | +27.1 | [+19,+36] | 0.0000 |
| `gemini-2.5-flash-lite` | +6.5 | [+0,+13] | 0.0668  (NS) |
| `gpt-4o-mini` | +44.8 | [+33,+56] | 0.0000 |
| `deepseek-chat` | +7.3 | [+2,+12] | 0.0012 |
| `qwen2.5:7b` | -1.1 | [-6,+4] | 0.8666  (NS) |
| `llama3.1:8b` | +1.1 | [-5,+7] | 0.8828  (NS) |

### 4b. flash vs lite focused (unpaired)
flash−lite focused Δ=+15.2pp, 95% CI [+3,+29], p=0.0230

### 4c. lunar vs fixed-date-control accuracy within each model (unpaired)
| Model | lunar acc | fixed-control acc | Δ | p |
|---|---|---|---|---|
| `gemini-2.5-flash` | 28% | 100% | +72 | 0.0000 |
| `gemini-2.5-flash-lite` | 3% | 100% | +97 | 0.0000 |
| `gpt-4o-mini` | 0% | 100% | +100 | 0.0000 |
| `deepseek-chat` | 81% | 100% | +19 | 0.0002 |
| `qwen2.5:7b` | 3% | 100% | +97 | 0.0000 |
| `llama3.1:8b` | 0% | 50% | +50 | 0.0308 |

### CLAIMS_TO_SOFTEN (not supported by the data)
- **MEMORIZATION ('recall-not-conversion') — NOT SUPPORTED.** Matched-pair decisive cell name✓&date✗ = 0 across all 5 models; reverse cell name✗&date✓ = 4. Explicit 农历 dates are if anything EASIER than festival names. Drop the memorization framing; the lunar failure is uniform conversion difficulty (routing result unaffected).
- routing helps gemini-2.5-flash-lite: Δ=+6.5pp, p=0.067
- routing helps qwen2.5:7b: Δ=-1.1pp, p=0.867
- routing helps llama3.1:8b: Δ=+1.1pp, p=0.883

## 5. Lunar decomposition by type × model (baseline focused)

| Type | 25flash | lite | 4omini | dschat | qwen | llama |
|---|---|---|---|---|---|---|
| famous+hint | 17% | 0% | 0% | 100% | 0% | 0% |
| name-only | 33% | 5% | 0% | 81% | 0% | 0% |
| pure-lunar-date | 33% | 0% | 0% | 50% | 17% | 0% |
| leap-month | 0% | 0% | 0% | 100% | 0% | 0% |
| control:清明(solar) | 100% | 0% | 100% | 100% | 0% | 0% |
| control:国庆(fixed) | 100% | 100% | 100% | 100% | 100% | 0% |
| control:圣诞(fixed) | 100% | 100% | 100% | 100% | 100% | 100% |

## 6. Determinism (20 probes × 3, temp 0)

| Model | identical/total | % |
|---|---|---|
| `gemini-2.5-flash` | 19/20 | 95% |
| `qwen2.5:7b` | 20/20 | 100% |

## 7. Figure files (Phase 5) & reproducibility (Phase 6)

- `figures_paper/fig1_lunar_decomp.{png,pdf}` — lunar decomposition, type×model, controls separated.
- `figures_paper/fig2_routing_gradient.{png,pdf}` — BASELINE/AVAILABLE/FORCED per model, routing% annotated.
- `figures_paper/fig3_memorization.{png,pdf}` — name✓&date✗ rate per model.
- `repro_manifest.md` — exact model/endpoint/version pins, library versions, OS, git commit.

## 8. Changelog

- **DeepSeek:** official **deepseek-chat** (api.deepseek.com) used across tier-1/focused/routing/hint/memo.
- **llama3.1:8b added to routing (Phase 2):** second 7–8B model; confirms the low-routing finding.
- **Memorization control added (Phase 3):** matched name/date pairs, decisive name✓&date✗ cell.
- **CIs + significance added (Phase 4):** all matrix/routing cells now have 95% bootstrap CIs; see CLAIMS_TO_SOFTEN for anything not significant at p<.05.
- **Figures (Phase 5) + repro manifest (Phase 6)** generated.
