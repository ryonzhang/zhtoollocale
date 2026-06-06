# ZhToolLocale

**Do AI agents act correctly when users speak Chinese?** When an agent fills a tool call, the argument *value is the action*: 转一万二 ("transfer twelve thousand") must become `transfer(12000)` — not `transfer(10002)`; 两斤苹果 ("two jin of apples") must become `order(weight_kg=1.0)` — not `2`. ZhToolLocale shows that today's LLMs **silently corrupt these values**: the JSON validates, the API returns 200, and the user finds out when the train ticket is for the wrong day. This repository is the benchmark that measures it, the detector that flags it, and the deterministic fix that prevents it.

📄 **Paper:** [Silent Locale Corruption: Diagnosing and Mitigating Chinese-Locale Semantic Failures in LLM Tool Calling](https://arxiv.org/abs/REPLACE-WITH-ARXIV-ID)

---

## Headline results

Focused-set accuracy (105 probes, 95% bootstrap CIs). **Lunar-date conversion fails near-universally; numeral/unit conversion is largely solved at the top tier but fragile below.**

| Model | Family | Tier-1 | Focused | Lunar |
|---|---|---|---|---|
| deepseek-chat | DeepSeek (zh) | 95.7 | **93.3** [89–98] | 81% |
| gemini-2.5-flash | Google | 100.0 | 75.2 [67–83] | 28% |
| gemini-2.5-flash-lite | Google | 95.7 | 60.0 [50–70] | 3% |
| qwen2.5:7b | Alibaba (zh) | 78.3 | 55.9 [46–65] | 3% |
| gpt-4o-mini | OpenAI | 91.3 | 54.3 [45–64] | 0% |
| llama3.1:8b | Meta | 47.8 | 25.7 [18–34] | 0% |

**The fix:** a deterministic converter tool restores accuracy to **94.8–100%** — *for models that route to it*. Frontier models route voluntarily (93–99%); a 7B model cannot be made to route at all (3%, even when mandated). Deployable-tier safety must be **architectural, not prompted.** See the paper and the per-tier deployment card.

---

## Run it in 30 seconds (no API key)

```bash
git clone https://github.com/ryonzhang/zhtoollocale.git
cd zhtoollocale
pip install -r requirements.txt
ZTL_PROVIDER=mock python src/models.py        # offline demo, zero keys
```

Run a real model:

```bash
ZTL_PROVIDER=gemini   ZTL_API_KEY=...  ZTL_MODEL=gemini-2.5-flash  python src/models.py
ZTL_PROVIDER=deepseek ZTL_API_KEY=...  ZTL_MODEL=deepseek-chat     python src/models.py
ZTL_PROVIDER=ollama                    ZTL_MODEL=qwen2.5:7b        python src/models.py   # local, free
```

Supported providers (OpenAI-compatible): `gemini`, `openai`, `deepseek`, `dashscope` (Qwen), `moonshot` (Kimi), `zhipu` (GLM), `ollama` (local).

---

## A benchmark that can't go stale

ZhToolLocale is a **generator, not a fixed dataset.** Every gold value is *computed* — lunar dates via `lunardate`, solar terms via an ephemeris, 万/亿 numerals and 市制 units via deterministic parsers — so the benchmark mints fresh, gold-verified probes for **any reference date**. This makes it **contamination-resistant by construction**: a model cannot have memorized a probe that didn't exist yet.

```bash
python src/generate.py --reference-date 2027-03-01 --n 300   # mint a fresh probe set
```

**Twelve categories**, three mechanisms: calendar systems (relative + lunar dates, fixed-date controls), numeral semantics (万/亿 grouping, internal zeros, capital 大写, mixed digit-character), and quantity/format (市制 units incl. fractional 半, classifiers, names, addresses, full-width, code-switching).

---

## Design principles

- **Computed golds** — no eyeballed answers; everything from a library or a native-speaker check.
- **ERR ≠ FAIL** — API errors are excluded, never scored as model failures.
- **Paraphrase triplets** — every probe in three phrasings; self-consistency is a measured quantity.
- **Pre-registered audit** — ambiguous probes flagged before runs; cross-model consensus against a gold triggers re-verification of the *gold*. (This protocol refuted our own initial hypothesis — see the paper.)
- **Full changelog** — every raw-to-canonical number is traceable in `results/`.

---

## Repository layout

```
probes/      probe sets (seed, hard, focused, lunar, memorization pairs) + the generator's output schema
src/         harness.py, models.py (provider adapter), converters, generate.py
results/     FINAL_RESULTS_v2.md (canonical), raw outputs, changelog
figures/     paper figures (lunar decomposition, routing gradient, memorization null)
repro_manifest.md   pinned model versions, endpoints, access dates, library versions
```

---

## Citation

```bibtex
@misc{zhang2026zhtoollocale,
  title  = {Silent Locale Corruption: Diagnosing and Mitigating Chinese-Locale Semantic Failures in LLM Tool Calling},
  author = {Ruiyang Zhang},
  year   = {2026},
  eprint = {REPLACE-WITH-ARXIV-ID},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL},
  url    = {https://github.com/ryonzhang/zhtoollocale}
}
```

## License

Code: [MIT](LICENSE). Benchmark data: [CC-BY-4.0](DATA_LICENSE).
