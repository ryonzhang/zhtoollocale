# -*- coding: utf-8 -*-
import sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from lunardate import LunarDate

fest = {"春节/大年初一": (1, 1), "元宵": (1, 15), "端午": (5, 5), "七夕": (7, 7),
        "中秋": (8, 15), "重阳": (9, 9), "腊八": (12, 8), "小年(腊月廿三)": (12, 23)}
print("=== lunar festival golds ===")
for label, (m, d) in fest.items():
    for y in (2026, 2027, 2028):
        s = LunarDate(y, m, d, False).toSolarDate()
        print(f"{label:22s} lunar {y}-{m:02d}-{d:02d} -> {s.isoformat()}")
    print()

print("=== leap months 2025-2028 ===")
seen = set()
d = datetime.date(2025, 1, 1)
while d <= datetime.date(2028, 12, 31):
    ld = LunarDate.fromSolarDate(d.year, d.month, d.day)
    if getattr(ld, "isLeapMonth", False):
        key = (ld.year, ld.month)
        if key not in seen:
            seen.add(key)
            first = LunarDate(ld.year, ld.month, 1, True).toSolarDate()
            print(f"leap: lunar {ld.year} run-{ld.month}-yue  1st -> {first.isoformat()}, "
                  f"15th -> {LunarDate(ld.year, ld.month, 15, True).toSolarDate().isoformat()}")
    d += datetime.timedelta(days=1)

print("\n=== Qingming (solar longitude 15 deg), China UTC+8 ===")
try:
    import ephem
    def solar_term(year, deg):
        lo = ephem.Date(datetime.datetime(year, 3, 1))
        hi = ephem.Date(datetime.datetime(year, 5, 1))
        for _ in range(80):
            mid = ephem.Date((lo + hi) / 2)
            lon = ephem.Ecliptic(ephem.Sun(mid)).lon * 180.0 / ephem.pi
            if lon < deg:
                lo = mid
            else:
                hi = mid
        cn = ephem.Date((lo + hi) / 2).datetime() + datetime.timedelta(hours=8)
        return cn.date()
    for y in (2026, 2027, 2028):
        print(f"Qingming {y} -> {solar_term(y, 15).isoformat()}")
except Exception as e:
    print("ephem unavailable:", e)
