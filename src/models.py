"""
ZhToolLocale - model adapter (OpenAI-compatible; Gemini/DeepSeek/Qwen/Kimi/GLM/Ollama).

  pip install openai
  export ZTL_PROVIDER=gemini
  export ZTL_API_KEY=YOUR_GEMINI_KEY
  export ZTL_MODEL=gemini-2.5-flash
  python models.py                          # runs probes_seed.json (tier-1)
  ZTL_PROBES=probes_hard_seed.json python models.py   # runs tier-2 hard set
"""
from __future__ import annotations
import os, re, sys, json, time
from harness import load_probes, evaluate, report

PROVIDERS = {
    "gemini":    "https://generativelanguage.googleapis.com/v1beta/openai/",
    "openai":    "https://api.openai.com/v1",
    "deepseek":  "https://api.deepseek.com/v1",
    "dashscope": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "moonshot":  "https://api.moonshot.cn/v1",
    "zhipu":     "https://open.bigmodel.cn/api/paas/v4",
    "ollama":    "http://localhost:11434/v1",
}
DEFAULT_MODEL = {"gemini": "gemini-2.5-flash", "deepseek": "deepseek-chat",
                 "ollama": "qwen2.5", "mock": "mock-model"}

SYSTEM = (
    "You are a function-calling assistant. Given the user's request (in Chinese) "
    "and a tool signature, output ONLY a JSON object of the tool arguments. "
    "Use canonical executable formats: dates as ISO yyyy-mm-dd, times as HH:MM, "
    "numbers as Arabic digits, weight in kg, distance in m, money as a CNY number. "
    "String-valued slots (item names, people, places) must preserve the user's "
    "source-language text verbatim - do NOT translate them. "
    "Output JSON only, no explanation."
)

# Injected into every prompt so relative dates are solvable.
# v0.1 omitted this - a task-validity bug the first Gemini run exposed.
REFERENCE_DATE = None


def build_prompt(utterance, tool_spec, prior_error=None):
    msg = ""
    if REFERENCE_DATE:
        msg += "Today's date is " + REFERENCE_DATE + ". Resolve all relative dates against it.\n"
    msg += "Tool: " + str(tool_spec) + "\nUser request (Chinese): " + str(utterance)
    if prior_error:
        msg += "\nYour previous call was rejected with this error; fix the arguments and output JSON again:\n" + str(prior_error)
    return msg


def extract_json(text):
    if not text:
        return {}
    text = text.replace("```json", "").replace("```", "")
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return {}


class _MockClient:
    _answers = {
        "大后天": '{"date":"2026-06-08","time":"10:00"}',
        "下周三": '{"date":"2026-06-10","time":"15:00"}',
        "一万二到": '{"amount_cny":10002}',
        "两斤苹果": '{"item":"苹果","weight_kg":2}',
        "欧阳娜娜": '{"family_name":"欧","given_name":"阳娜娜"}',
        "三块五": '{"price_cny":3.5}',
        "一米八": '{"height_m":1.8}',
    }

    def reply(self, user_msg):
        for k, v in self._answers.items():
            if k in user_msg:
                return v
        return "{}"


def make_call(provider, model):
    if provider == "mock":
        mock = _MockClient()

        def mock_call(utterance, tool_spec, prior_error=None):
            return extract_json(mock.reply(build_prompt(utterance, tool_spec, prior_error)))
        return mock_call

    from openai import OpenAI
    base_url = PROVIDERS.get(provider)
    if not base_url:
        sys.exit("Unknown provider " + repr(provider) + ". Choose: " + str(list(PROVIDERS)))
    api_key = os.environ.get("ZTL_API_KEY", "ollama" if provider == "ollama" else "")
    if not api_key:
        sys.exit("Set ZTL_API_KEY (not needed for ollama).")
    client = OpenAI(base_url=base_url, api_key=api_key)

    _hint = ""
    _hf = os.environ.get("ZTL_HINT_FILE")
    if _hf and os.path.exists(_hf):
        with open(_hf, encoding="utf-8") as _f:
            _hint = " " + _f.read().strip()

    def real_call(utterance, tool_spec, prior_error=None):
        sys_content = SYSTEM + _hint  # Phase D hint ablation (empty unless ZTL_HINT_FILE set)
        messages = [{"role": "system", "content": sys_content},
                    {"role": "user", "content": build_prompt(utterance, tool_spec, prior_error)}]
        for attempt in range(5):
            try:
                resp = client.chat.completions.create(model=model, messages=messages, temperature=0)
                return extract_json(resp.choices[0].message.content)
            except Exception as exc:
                t = str(exc)
                if "429" in t or "rate" in t.lower():
                    wait = 2 ** attempt
                    print("  [rate-limited, waiting " + str(wait) + "s]")
                    time.sleep(wait)
                    continue
                print("  [error] " + t)
                return {"__api_error__": t}
        return {"__api_error__": "exhausted retries (persistent rate-limit)"}
    return real_call


if __name__ == "__main__":
    provider = os.environ.get("ZTL_PROVIDER", "mock")
    model = os.environ.get("ZTL_MODEL", DEFAULT_MODEL.get(provider, "default"))
    probes_path = os.environ.get("ZTL_PROBES")  # optional: probes_hard_seed.json
    print("Provider=" + provider + "  Model=" + model + "  Probes=" + (probes_path or "probes_seed.json") + "\n")
    data = load_probes(probes_path)
    REFERENCE_DATE = data.get("reference_date", "") + " (" + data.get("reference_weekday", "") + ")"
    print("Reference date injected: " + REFERENCE_DATE + "\n")
    call = make_call(provider, model)
    rows, by_cat, by_layer = evaluate(data, call=call)
    report(rows, by_cat, by_layer)
