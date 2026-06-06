# -*- coding: utf-8 -*-
"""PHASE C — routing experiment. Offers 3 REAL converter tools via OpenAI
function-calling with a 2-step loop. Conditions: AVAILABLE (tools, no instruction)
/ FORCED (tools + one must-call line). BASELINE is reused from focused results.
env: ZTL_PROVIDER ZTL_MODEL ZTL_API_KEY ZTL_COND(available|forced)"""
import sys, io, os, re, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
from openai import OpenAI
from harness import args_match
import converters

PROVIDERS = {"gemini":"https://generativelanguage.googleapis.com/v1beta/openai/",
             "ollama":"http://localhost:11434/v1",
             "openai":"https://api.openai.com/v1", "deepseek":"https://api.deepseek.com/v1"}
REF = "Today's date is 2026-06-05 (Friday). Resolve all relative dates against it."
SYSTEM = ("You are a function-calling assistant. Given the user's request (in Chinese) "
          "and a tool signature, output ONLY a JSON object of the tool arguments. "
          "Use canonical executable formats: dates as ISO yyyy-mm-dd, numbers as Arabic digits, "
          "weight in kg. String slots keep the source-language text. Output JSON only.")
FORCE_LINE = (" For lunar dates, Chinese numerals, and weight units, you MUST call the "
              "corresponding converter tool rather than converting inline.")

TOOLS = [
 {"type":"function","function":{"name":"lunar_to_gregorian",
   "description":"Convert a Chinese lunar-calendar date to a Gregorian ISO date yyyy-mm-dd.",
   "parameters":{"type":"object","properties":{
     "lunar_year":{"type":"integer"},"lunar_month":{"type":"integer"},
     "lunar_day":{"type":"integer"},"is_leap_month":{"type":"boolean"}},
     "required":["lunar_year","lunar_month","lunar_day"]}}},
 {"type":"function","function":{"name":"chinese_number_to_value",
   "description":"Parse a Chinese numeral string (incl. 万/亿, capital forms, elliptical, full/half width) into a numeric value.",
   "parameters":{"type":"object","properties":{"text":{"type":"string"}},"required":["text"]}}},
 {"type":"function","function":{"name":"convert_to_kg",
   "description":"Convert a weight to kilograms. unit one of 斤,两,公斤,kg,克,g.",
   "parameters":{"type":"object","properties":{"value":{"type":"number"},"unit":{"type":"string"}},
     "required":["value","unit"]}}},
]
EXEC = {"lunar_to_gregorian":converters.lunar_to_gregorian,
        "chinese_number_to_value":converters.chinese_number_to_value,
        "convert_to_kg":converters.convert_to_kg}
EXPECTED = {"lunar":"lunar_to_gregorian","internal_zero":"chinese_number_to_value",
            "elliptical":"chinese_number_to_value","capital":"chinese_number_to_value",
            "mixed_digit":"chinese_number_to_value","long_chain":"chinese_number_to_value",
            "units_half":"convert_to_kg"}

def extract_json(t):
    if not t: return {}
    t=t.replace("```json","").replace("```","")
    i,j=t.find("{"),t.rfind("}")
    if i<0 or j<=i: return {}
    try: return json.loads(t[i:j+1])
    except Exception: return {}

def parse_target(spec):
    """'schedule_event(date: yyyy-mm-dd)' -> ('schedule_event', schema). A call to
    this target tool counts as the model SUBMITTING its final args (agentic style)."""
    name=spec.split("(",1)[0].strip()
    inside=spec[spec.find("(")+1:spec.rfind(")")]
    props={}; req=[]
    for part in inside.split(","):
        an=part.split(":",1)[0].strip()
        if not an: continue
        props[an]={"type":"string" if an=="date" else "number"}
        req.append(an)
    return name, {"type":"function","function":{"name":name,
        "description":"Submit the final tool arguments for the user's request.",
        "parameters":{"type":"object","properties":props,"required":req}}}

def run():
    prov=os.environ["ZTL_PROVIDER"]; model=os.environ["ZTL_MODEL"]; cond=os.environ["ZTL_COND"]
    key=os.environ.get("ZTL_API_KEY","ollama")
    client=OpenAI(base_url=PROVIDERS[prov], api_key=key)
    sysmsg=SYSTEM + (FORCE_LINE if cond=="forced" else "")
    with io.open(os.path.join(HERE,"probes_focus_seed.json"),encoding="utf-8") as f:
        probes=[p for p in json.load(f)["probes"] if p["family"]!="control"]
    rows=[]; ok=n=routed=0; mis=[]
    for p in probes:
        gold=p["expected_args"]; fam=p["family"]
        target_name, target_schema = parse_target(p["tool"])
        tools_p = TOOLS + [target_schema]
        user=f"{REF}\nTool: {p['tool']}\nUser request (Chinese): {p['utterance_zh']}"
        messages=[{"role":"system","content":sysmsg},{"role":"user","content":user}]
        calls=[]
        final={}
        for _round in range(5):
            try:
                r=client.chat.completions.create(model=model,messages=messages,
                    tools=tools_p,tool_choice="auto",temperature=0)
            except Exception as e:
                final={"__api_error__":str(e)}; break
            m=r.choices[0].message
            tcs=getattr(m,"tool_calls",None)
            if tcs:
                # a call to the target tool = the model submitting its final args
                sub=next((tc for tc in tcs if tc.function.name==target_name), None)
                if sub is not None:
                    try: final=json.loads(sub.function.arguments or "{}")
                    except Exception: final={}
                    break
                messages.append({"role":"assistant","content":m.content or "",
                    "tool_calls":[{"id":tc.id,"type":"function",
                      "function":{"name":tc.function.name,"arguments":tc.function.arguments}} for tc in tcs]})
                for tc in tcs:
                    name=tc.function.name
                    try: a=json.loads(tc.function.arguments or "{}")
                    except Exception: a={}
                    try: res=EXEC[name](**a)
                    except Exception as e: res=f"ERROR:{e}"
                    calls.append({"tool":name,"args":a,"result":res})
                    messages.append({"role":"tool","tool_call_id":tc.id,"content":str(res)})
                continue
            final=extract_json(m.content); break
        if "__api_error__" in final or not final:
            # api error OR no parseable args produced (abstention) -> ERR, excluded
            rows.append((p["id"],fam,"ERR",final,gold,calls)); continue
        passed=args_match(final,gold)
        n+=1; ok+=passed
        did_route=len(calls)>0
        routed+=did_route
        # mis-routing: called a converter whose category != expected for this family
        exp=EXPECTED.get(fam)
        for c in calls:
            if exp and c["tool"]!=exp:
                mis.append((p["id"],fam,"wrong-tool",c));
            if isinstance(c["result"],str) and c["result"].startswith("ERROR"):
                mis.append((p["id"],fam,"tool-error",c))
        rows.append((p["id"],fam,"PASS" if passed else "FAIL",final,gold,calls))
    tag=os.environ.get("ZTL_TAG",model.replace(":","").replace(".",""))
    nerr=sum(1 for r in rows if r[2]=="ERR")
    out={"model":model,"cond":cond,"n":n,"correct":ok,"errored":nerr,"routed":routed,
         "total":len(probes),
         "rows":[{"id":r[0],"family":r[1],"status":r[2],"final":r[3],"gold":r[4],"calls":r[5]} for r in rows],
         "misrouting":mis}
    with io.open(os.path.join(HERE,f"routing_{tag}_{cond}.json"),"w",encoding="utf-8") as f:
        json.dump(out,f,ensure_ascii=False,indent=1)
    acc = f"{100*ok/n:.1f}%" if n else "n/a"
    print(f"{model} [{cond}]: acc {ok}/{n} ({acc}) err={nerr}  routing {routed}/{len(probes)} ({100*routed/len(probes):.0f}%)  misroute={len(mis)}")

if __name__=="__main__":
    run()
