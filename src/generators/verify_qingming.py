# -*- coding: utf-8 -*-
import sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import ephem

def qingming_instant(year):
    # bracket and bisect for apparent geocentric solar ecliptic longitude == 15 deg
    lo = ephem.Date(datetime.datetime(year, 3, 25))
    hi = ephem.Date(datetime.datetime(year, 4, 10))
    for _ in range(100):
        mid = ephem.Date((lo + hi) / 2)
        lon = ephem.Ecliptic(ephem.Sun(mid)).lon * 180.0 / ephem.pi
        if lon < 15.0:
            lo = mid
        else:
            hi = mid
    return ephem.Date((lo + hi) / 2).datetime()  # UTC

for y in (2026, 2027, 2028):
    utc = qingming_instant(y)
    cst = utc + datetime.timedelta(hours=8)
    print(f"清明 {y}: UTC {utc:%Y-%m-%d %H:%M}  ->  CST(+8) {cst:%Y-%m-%d %H:%M}  -> date {cst.date()}")
