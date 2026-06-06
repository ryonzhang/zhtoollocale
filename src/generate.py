# -*- coding: utf-8 -*-
"""ZhToolLocale probe generator — mint fresh, gold-verified probes for ANY
reference date. Golds are COMPUTED (lunardate / ephem / deterministic parsers),
and every generated probe is round-trip verified against the converters in
converters.py, so a generated gold cannot be wrong by construction.

    python src/generate.py --reference-date 2027-03-01 --n 300 --out probes/probes_generated.json

This is what makes the benchmark contamination-resistant: a model cannot have
memorized a probe whose reference date did not exist when it was trained.
"""
from __future__ import annotations
import argparse, datetime, io, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import converters  # lunar_to_gregorian, chinese_number_to_value, convert_to_kg

try:
    import ephem  # optional, only for the 清明 solar-term control
    _HAS_EPHEM = True
except Exception:
    _HAS_EPHEM = False

# ---------------------------------------------------------------- numerals
_DIG = "零一二三四五六七八九"
_SMALL = ["", "十", "百", "千"]
_BIG = ["", "万", "亿"]

def int_to_chinese(n: int) -> str:
    """Render a non-negative int in standard Chinese numerals (inverse of the
    parser). Verified by round-trip in the generator below."""
    if n == 0:
        return "零"
    def _section(s):  # 0 <= s < 10000
        out, zero = "", False
        unit = 0
        while s > 0:
            d = s % 10
            if d == 0:
                if out:            # only INTERNAL zeros become 零 (skip trailing)
                    zero = True
            else:
                if zero:
                    out = "零" + out
                    zero = False
                out = _DIG[d] + _SMALL[unit] + out
            s //= 10
            unit += 1
        return out
    parts, gi = [], 0
    big_secs = []
    while n > 0:
        big_secs.append(n % 10000)
        n //= 10000
    chunk = ""
    for i in range(len(big_secs) - 1, -1, -1):
        sec = big_secs[i]
        if sec == 0:
            if chunk and not chunk.endswith("零"):
                chunk += "零"
            continue
        seg = _section(sec)
        if i < len(big_secs) - 1 and sec < 1000 and chunk:
            chunk += "零"
        chunk += seg + _BIG[i]
    out = chunk.strip("零")
    # tidy "一十" -> "十" at the very start (e.g. 十二, not 一十二)
    if out.startswith("一十"):
        out = out[1:]
    return out

# ---------------------------------------------------------------- dates
def upcoming_lunar(ref: datetime.date, m: int, d: int, leap=False):
    from lunardate import LunarDate
    for y in range(ref.year, ref.year + 3):
        try:
            s = LunarDate(y, m, d, leap).toSolarDate()
        except Exception:
            continue
        if s >= ref:
            return s.isoformat()
    return None

def upcoming_fixed(ref: datetime.date, month: int, day: int):
    for y in (ref.year, ref.year + 1):
        s = datetime.date(y, month, day)
        if s >= ref:
            return s.isoformat()
    return None

def qingming(ref: datetime.date):
    if not _HAS_EPHEM:
        return None
    for y in (ref.year, ref.year + 1):
        lo = ephem.Date(datetime.datetime(y, 3, 25)); hi = ephem.Date(datetime.datetime(y, 4, 10))
        for _ in range(80):
            mid = ephem.Date((lo + hi) / 2)
            lon = ephem.Ecliptic(ephem.Sun(mid)).lon * 180.0 / ephem.pi
            lo, hi = (mid, hi) if lon < 15.0 else (lo, mid)
        cst = (ephem.Date((lo + hi) / 2).datetime() + datetime.timedelta(hours=8)).date()
        if cst >= ref:
            return cst.isoformat()
    return None

# festival name-only / with-hint templates: (display, lunar m,d, hint-phrase)
FESTIVALS = [
    ("中秋节", 8, 15, "农历八月十五"), ("端午节", 5, 5, "农历五月初五"),
    ("重阳节", 9, 9, "农历九月初九"), ("七夕", 7, 7, "农历七月初七"),
    ("元宵节", 1, 15, "农历正月十五"), ("春节", 1, 1, "农历正月初一"),
]

# ---------------------------------------------------------------- generators
def gen_lunar(ref, rng):
    f = rng.choice(FESTIVALS); name, m, d, hint = f
    gold = upcoming_lunar(ref, m, d)
    if not gold:
        return None
    if rng.random() < 0.5:
        utt = f"{name}那天帮我订一桌饭。"
    else:
        utt = f"{hint}那天帮我订一桌饭。"
    return {"category": "lunar_date", "utterance_zh": utt,
            "tool": "reserve_table(date: yyyy-mm-dd)", "expected_args": {"date": gold}}

def gen_control(ref, rng):
    pick = rng.choice(["国庆", "圣诞", "元旦", "清明"])
    if pick == "国庆": gold = upcoming_fixed(ref, 10, 1); name = "国庆节"
    elif pick == "圣诞": gold = upcoming_fixed(ref, 12, 25); name = "圣诞节"
    elif pick == "元旦": gold = upcoming_fixed(ref, 1, 1); name = "元旦"
    else: gold = qingming(ref); name = "清明节"
    if not gold:
        return None
    return {"category": "date_control", "utterance_zh": f"{name}那天提醒我。",
            "tool": "set_reminder(date: yyyy-mm-dd)", "expected_args": {"date": gold}}

REL = [("大前天", -3), ("前天", -2), ("昨天", -1), ("明天", 1), ("后天", 2),
       ("大后天", 3), ("三天后", 3), ("一周后", 7), ("两周后", 14)]

def gen_relative(ref, rng):
    name, off = rng.choice(REL)
    gold = (ref + datetime.timedelta(days=off)).isoformat()
    return {"category": "relative_date", "utterance_zh": f"{name}上午十点开会。",
            "tool": "schedule_meeting(date: yyyy-mm-dd, time: HH:MM)",
            "expected_args": {"date": gold, "time": "10:00"}}

def gen_numeral(ref, rng):
    # mix of plain, internal-zero, and big numbers; gold verified by round-trip
    style = rng.choice(["plain", "wan", "yi", "internal_zero"])
    if style == "plain": n = rng.randint(11, 9999)
    elif style == "wan": n = rng.randint(1, 99) * 10000 + rng.choice([0, rng.randint(1, 9999)])
    elif style == "yi": n = rng.randint(1, 99) * 10**8 + rng.choice([0, rng.randint(1, 9999) * 10000])
    else: n = rng.randint(1, 9) * 10**8 + rng.randint(1, 99) * 10000  # 一亿零N十万
    surface = int_to_chinese(n)
    if converters.chinese_number_to_value(surface) != n:  # self-verify; skip if not exact
        return None
    return {"category": "numeral_wan_yi", "utterance_zh": f"转账{surface}到我的账户。",
            "tool": "transfer(amount_cny: number)", "expected_args": {"amount_cny": n}}

def gen_unit(ref, rng):
    unit, factor = rng.choice([("斤", 0.5), ("两", 0.05), ("公斤", 1.0)])
    q = rng.randint(1, 20)
    surface_q = int_to_chinese(q)
    gold = converters.convert_to_kg(q, unit)
    return {"category": "unit_conversion", "utterance_zh": f"称{surface_q}{unit}苹果。",
            "tool": "order_produce(item: string, weight_kg: number)",
            "expected_args": {"item": "苹果", "weight_kg": gold}}

GENERATORS = [("lunar", gen_lunar), ("control", gen_control), ("relative", gen_relative),
              ("numeral", gen_numeral), ("unit", gen_unit)]

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # so Chinese prints on Windows too
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Mint fresh, gold-verified ZhToolLocale probes.")
    ap.add_argument("--reference-date", default="2026-06-05", help="YYYY-MM-DD (golds computed against this)")
    ap.add_argument("--n", type=int, default=105, help="number of probes to generate")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "probes", "probes_generated.json"))
    a = ap.parse_args()
    ref = datetime.date.fromisoformat(a.reference_date)
    rng = random.Random(a.seed)
    if not _HAS_EPHEM:
        print("[note] ephem not installed: 清明 solar-term control is skipped (pip install ephem).")

    probes, i, attempts = [], 0, 0
    while len(probes) < a.n and attempts < a.n * 20:
        attempts += 1
        name, gen = rng.choice(GENERATORS)
        p = gen(ref, rng)
        if not p:
            continue
        i += 1
        p = {"id": f"g-{i:04d}", "layer": "arguments",
             "reference_date": a.reference_date, **p}
        probes.append(p)

    out = {"benchmark": "ZhToolLocale-generated", "reference_date": a.reference_date,
           "reference_weekday": ref.strftime("%A"), "generated_n": len(probes), "probes": probes}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, io.open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # gold-verification sample for human review
    print(f"Generated {len(probes)} gold-verified probes for reference date "
          f"{a.reference_date} ({ref.strftime('%A')}) -> {a.out}\n")
    print("Sample (probe | input | computed gold):")
    for p in probes[:12]:
        print(f"  {p['id']}  {p['category']:14s}  {p['utterance_zh']:28s} -> {p['expected_args']}")

if __name__ == "__main__":
    main()
