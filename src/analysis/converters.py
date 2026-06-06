# -*- coding: utf-8 -*-
"""Deterministic converter tools for the routing experiment (executed with real
code, never an LLM). Self-tested against the focused-set golds."""
import re
from lunardate import LunarDate

# ---------- lunar_to_gregorian ----------
def lunar_to_gregorian(lunar_year, lunar_month, lunar_day, is_leap_month=False):
    return LunarDate(int(lunar_year), int(lunar_month), int(lunar_day),
                     bool(is_leap_month)).toSolarDate().isoformat()

# ---------- chinese_number_to_value ----------
_CAP = str.maketrans("壹贰叁肆伍陆柒捌玖拾佰仟萬亿零兩", "一二三四五六七八九十百千万亿零两")
_FW  = str.maketrans("０１２３４５６７８９．", "0123456789.")
_DIG = {"零":0,"〇":0,"一":1,"二":2,"两":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9}
_SMALL = {"十":10,"百":100,"千":1000}
_BIG = {"万":10000,"亿":100000000}

def _parse_pure_cn(s):
    """Parse a pure-Chinese numeral (no arabic) incl. 零 and 万/亿 nesting.
    Ellipsis (trailing bare digit, e.g. 三万五) handled by caller."""
    total = 0      # accumulated across 亿/万 boundaries
    section = 0    # current <万 section
    number = 0     # pending digit
    for ch in s:
        if ch in _DIG:
            number = _DIG[ch]
        elif ch in _SMALL:
            section += (number if number else 1) * _SMALL[ch]
            number = 0
        elif ch in _BIG:
            section += number
            total += section * _BIG[ch]
            section = 0
            number = 0
    return total + section + number

def _last_unit_magnitude(s):
    mag = 1
    for ch in s:
        if ch in _SMALL: mag = _SMALL[ch]
        elif ch in _BIG: mag = _BIG[ch]
    return mag

def chinese_number_to_value(text):
    s = str(text).translate(_FW).translate(_CAP)
    s = re.sub(r"[元整块钱人民币,，\s]", "", s)
    # mixed arabic+chinese big units, e.g. 1.2亿 / 3万5
    m = re.fullmatch(r"(\d+(?:\.\d+)?)(亿|万)(\d+)?", s)
    if m:
        base = float(m.group(1)) * _BIG[m.group(2)]
        if m.group(3):  # trailing arabic = next lower unit (3万5 -> +5*1000)
            base += int(m.group(3)) * (_BIG[m.group(2)] // 10)
        return int(base) if base == int(base) else base
    if re.fullmatch(r"\d+(?:\.\d+)?", s):
        f = float(s); return int(f) if f == int(f) else f
    # pure chinese
    val = _parse_pure_cn(s)
    # ellipsis: trailing bare digit with NO 零 separating it from the last unit
    mlast = re.search(r"([一二两三四五六七八九])$", s)
    if mlast:
        # find chars after the last unit char
        last_unit_pos = max([i for i,ch in enumerate(s) if ch in _SMALL or ch in _BIG], default=-1)
        tail = s[last_unit_pos+1:] if last_unit_pos >= 0 else s
        if last_unit_pos >= 0 and "零" not in tail and len(tail) == 1:
            d = _DIG[mlast.group(1)]
            U = _last_unit_magnitude(s)
            val = val - d + d * (U // 10)
    return val

# ---------- convert_to_kg ----------
_UNIT_KG = {"斤":0.5, "两":0.05, "公斤":1.0, "kg":1.0, "千克":1.0, "克":0.001, "g":0.001}
def convert_to_kg(value, unit):
    u = str(unit).strip()
    if u not in _UNIT_KG:
        raise ValueError(f"unknown unit {unit!r}")
    return round(float(value) * _UNIT_KG[u], 6)


if __name__ == "__main__":
    import sys, io, json, os
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    HERE = os.path.dirname(os.path.abspath(__file__))
    # numeral self-test: parse the surface numeral from each numeral probe's gold note
    cases = {
        "一万二":12000, "三万五":35000, "两千八":2800, "一百二":120, "三千五":3500,
        "一亿零五十万":100500000, "十万零五百":100500, "一万零五十":10050, "一万零五":10005,
        "一亿零五万":100050000, "壹万贰仟":12000, "叁佰伍拾":350, "1.2亿":120000000,
        "3万5":35000, "两亿三千零五十万":230500000,
        "十二亿三千四百五十六万七千八百":1234567800, "两百五十万":2500000, "五十万":500000,
    }
    bad=0
    for s,exp in cases.items():
        got=chinese_number_to_value(s)
        ok = got==exp
        bad += not ok
        print(f"  [{'OK' if ok else 'XX'}] {s:30s} -> {got}  (exp {exp})")
    # unit self-test
    units = {(2.5,"两"):0.125,(3.5,"斤"):1.75,(0.5,"两"):0.025,(2,"公斤"):2.0,(2,"斤"):1.0,(3,"公斤"):3.0}
    for (v,u),exp in units.items():
        got=convert_to_kg(v,u); ok=abs(got-exp)<1e-9; bad+=not ok
        print(f"  [{'OK' if ok else 'XX'}] convert_to_kg({v},{u}) -> {got} (exp {exp})")
    # lunar self-test
    for (y,m,d,leap),exp in {(2026,5,5,False):"2026-06-19",(2028,5,15,True):"2028-07-07"}.items():
        got=lunar_to_gregorian(y,m,d,leap); ok=got==exp; bad+=not ok
        print(f"  [{'OK' if ok else 'XX'}] lunar {y}-{m}-{d} leap={leap} -> {got} (exp {exp})")
    print(f"\n{'ALL GREEN' if bad==0 else str(bad)+' FAILURES'}")
