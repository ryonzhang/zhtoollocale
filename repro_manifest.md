# Reproducibility manifest (Phase 6)

- **Access date (all model runs):** 2026-06-05
- **OS:** Windows-11-10.0.26200-SP0  ·  Python 3.12.3
- **Libraries:** openai=2.41.0, lunardate=0.2.2, ephem=4.2.1, numpy=2.4.6, scipy=1.17.1, matplotlib=3.10.9
- **Bootstrap:** numpy default_rng, seed=12345, 10,000 resamples.

### Model endpoints / version strings (as accessed 2026-06-05)
| Model id | provider | endpoint |
|---|---|---|
| gemini-2.5-flash | Google | https://generativelanguage.googleapis.com/v1beta/openai/ |
| gemini-2.5-flash-lite | Google | (same) |
| gpt-4o-mini | OpenAI | https://api.openai.com/v1 |
| deepseek-chat | DeepSeek | https://api.deepseek.com/v1 (CANONICAL) |
| qwen2.5:7b | Ollama (local) | http://localhost:11434/v1 ; ollama 0.30.4 |
| llama3.1:8b | Ollama (local) | (same) |

_NB: hosted models (Gemini/OpenAI/DeepSeek) are versioned server-side by the alias; exact weights are not pinnable. Local Ollama models are content-addressed: qwen2.5:7b sha 845dbda0ea48, llama3.1:8b sha 46e0c10c039e._

- **Benchmark git commit:** `f14f257ac038d60567261e901e3a17af17393987`
