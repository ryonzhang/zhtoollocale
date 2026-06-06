# Mitigation experiment — lunar conversion as tool routing

**Model:** gemini-2.5-flash · **probes:** 39 lunar (focused set) · **resolver:** `lunardate` (deterministic) · temp 0.

## Headline

| Condition | What the model does | Accuracy |
|---|---|---|
| **Baseline** | emits the Gregorian date directly | **11/39 (28.2%)** |
| **Tool-routing** | emits only lunar fields (年/月/日/闰); resolver converts | **34/39 (87.2%)** |
| **Oracle** | gold lunar fields → resolver (ceiling) | **39/39 (100%)** |
| — model lunar-field *parsing* correct | — | 34/39 (87.2%) |

**Baseline → Tool: +59.0 points.** Giving the model a `lunar_to_gregorian` tool
and asking it only to *parse* the lunar fields (not perform the calendar math)
triples its accuracy. Oracle = 100% confirms the resolver + date-placement path
is sound, so the entire residual is in field parsing.

## The residual 5/39 is ONE specific bug, not a conversion gap

All 5 tool-condition failures have an identical cause: the model emitted
`lunar_year = 4723` or `4724` instead of 2026/2027. That is the **黄帝纪元 (Yellow
Emperor calendar) year** for 2026 CE (2026 + 2697 = 4723) — an era-numbering
artifact, raised on some paraphrases but not others (e.g. f-L01-a parsed 2026
correctly, f-L01-b emitted 4723). It is not a failure to know the festival's
lunar month/day.

Notably, the harder parsing cases were handled correctly under the tool:
- **Leap month** f-L12 (闰五月十五, `is_leap=True`) → parsed correctly, 3/3.
- **Year-boundary** f-L07 (腊八 → lunar_year 2026, falls 2027-01-15) → parsed
  correctly, 3/3.

## Interpretation

The lunar failure is a **tool-routing / knowledge-availability problem, not a
reasoning problem**. Models reliably know *which* lunar date a festival is
(月/日), and even handle leap months and year boundaries; what they cannot do is
the lunar→Gregorian arithmetic internally (§ determinism: that step is even
non-deterministic at temp 0). A deterministic resolver removes the failure almost
entirely; the small remainder is a fixable parsing quirk (era-year numbering),
addressable with one line of output constraint.

Raw per-probe data: `mitigation_results.json`. Reproduce: `mitigation.py`.
