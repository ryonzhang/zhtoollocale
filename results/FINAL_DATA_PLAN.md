# ZhToolLocale — FINAL data-collection instruction

**Principle: this is the last data pass. After the two runs below land, data
collection is CLOSED and all remaining effort goes to writing.** The finding has
already survived three escalations and an adversarial gold audit; further models
add less value than a clean introduction.

Status legend: ☑ done · ◐ runnable now · ☐ needs an input.

---

## A. Cleanups (turn the existing data paper-ready) — no new models

1. ☑ **Recompute excluding ambiguous probes.** Done (`_recompute_clean.py`).
   Dropping the 2 flagged-ambiguous groups (f-L07, f-N07 → 102 probes) moves
   every model <2 pts (e.g. 2.5-flash 74.1→74.5%). Headline numbers are robust.
   → Report both in the paper: "headline / validity-filtered".
2. ◐ **Formalize the numeral-decomposition table** for the appendix: one row per
   numeral probe — surface form · decomposition · gold · the canonical wrong
   answer models produce (e.g. 一亿零五十万 = 1e8 + 50·1e4 = 100,500,000; common
   error 105,000,000 from 零五十万→零五百万). Source: `_gen_focus.py` table.
3. ◐ **Determinism repeat.** Re-run gemini-2.5-flash focused at temp 0 a 2nd
   time (`results_25flash_focus_rep2.txt`), report probe-level agreement vs run 1
   as the noise floor. (Running now.)

## B. The two Findings-grade additions — then STOP

4. ☐ **DeepSeek-chat (second Chinese-native family).** ~$1, one evening.
   - Needs: a DeepSeek API key.
   - Run: `ZTL_PROVIDER=deepseek ZTL_MODEL=deepseek-chat` over `probes_seed.json`
     (tier-1) and `probes_focus_seed.json` (focused). Save
     `results_deepseek_tier1.txt`, `results_deepseek_focus.txt`; re-run
     `_compile_summary3.py` (add `("deepseek-chat","deepseek")` to MODELS).
   - Why: turns "Qwen also fails" into "Chinese pre-training does not rescue
     lunar conversion in ANY family" — the universality claim reviewers probe.
   - Expected: lunar family ≈ 0–3/39, mirroring Qwen. If DeepSeek *beats* the
     others on lunar, that is itself a publishable wrinkle — report either way.

5. ◐ **Mitigation experiment (the constructive ending).** ~1 day. Runnable now
   on gemini-2.5-flash (key in hand); no DeepSeek key required.
   - **Design (2-turn tool-routing):** build `probes_focus_lunar.json` (the 39
     lunar variants). Add a tool `lunar_to_gregorian(year, month, day, is_leap)`
     to the toolset. Protocol: turn 1 the model, instead of guessing a date,
     emits a call to `lunar_to_gregorian` with the lunar fields it parsed; the
     harness resolves it deterministically with `lunardate` and returns the ISO
     date; turn 2 the model places that date into the original tool's `date` arg.
   - **Score two conditions** on the same 39 probes: (i) baseline (current
     numbers), (ii) tool-augmented. Report the delta.
   - **Hypothesis:** lunar accuracy jumps from ~0–28% to ~95%+, with the residual
     being lunar-field *parsing* errors (e.g. mis-identifying 闰月), not
     conversion. This reframes the paper from "models are broken" to "locale
     conversion is a tool-routing problem with a known fix."
   - **Ablation to include:** also test "model parses lunar fields" vs "oracle
     lunar fields" to separate parsing error from routing error.

## C. Explicitly OUT of scope (do NOT run — perfectionism guard)
- No 6th base model. No tier-2/tier-3 backfill on the new models (focused
  supersedes them). No probe-count expansion beyond 108+39. No temperature sweep
  beyond the single determinism repeat.

## Deliverables when B is done
- `summary3.md` regenerated with the DeepSeek column.
- `mitigation.md`: 39-probe baseline-vs-tool table + the parsing/routing ablation.
- Paper results & mitigation sections take final numbers; **submit.**
