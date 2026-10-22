"""CPI-U (all items, U.S. city average, not seasonally adjusted, CUUR0000SA0)
from the BLS API. Writes data/processed/cpi.csv with calendar-year and
federal fiscal-year (October to September) averages of the monthly index.
"""
import json
import os
from decimal import Decimal, ROUND_HALF_UP
import sys
from pathlib import Path

import requests

sys.path.insert(0, os.path.expanduser("~/.claude/d4tp-process"))
from d4tp_env import load_env, get_key  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/bls"
SERIES = "CUUR0000SA0"
START, END = 1978, 2025

load_env()
RAW.mkdir(parents=True, exist_ok=True)
refresh = "--refresh" in sys.argv
months = {}
unavailable = []
for y0 in range(START, END + 1, 20):
    y1 = min(y0 + 19, END)
    cache = RAW / f"{SERIES}_{y0}_{y1}.json"
    if refresh or not cache.exists():
        r = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/",
                          json={"seriesid": [SERIES], "startyear": str(y0), "endyear": str(y1),
                                "registrationkey": get_key("BLS_API_KEY")}, timeout=60)
        r.raise_for_status()
        cache.write_text(r.text)
    d = json.loads(cache.read_text())
    if d.get("status") != "REQUEST_SUCCEEDED":
        raise SystemExit(f"BLS error: {d.get('message')}")
    for row in d["Results"]["series"][0]["data"]:
        if not row["period"].startswith("M") or row["period"] == "M13":
            continue
        key = (int(row["year"]), int(row["period"][1:]))
        if row["value"] == "-":
            # BLS footnote X: October 2025 was not collected during the 2025 lapse in appropriations
            unavailable.append((key, "; ".join(f["text"] for f in row["footnotes"] if f)))
            continue
        if key in months:
            raise SystemExit(f"duplicate CPI month {key}")
        months[key] = float(row["value"])

def r4(v):
    """Four decimals, half away from zero (the project's rounding rule)."""
    return Decimal(repr(v)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


lines = ["basis,year,cpi,months"]
for y in range(START, END + 1):
    cal = [months[(y, m)] for m in range(1, 13) if (y, m) in months]
    if len(cal) == 12:
        lines.append(f"calendar,{y},{r4(sum(cal) / 12)},12")
    fy = [months[k] for k in [(y - 1, m) for m in (10, 11, 12)] + [(y, m) for m in range(1, 10)] if k in months]
    if len(fy) == 12:
        lines.append(f"fiscal,{y},{r4(sum(fy) / 12)},12")
(ROOT / "data/processed/cpi.csv").write_text("\n".join(lines) + "\n")
print(f"wrote cpi.csv ({len(months)} months, {START}-{END})")
for key, note in unavailable:
    print(f"  unavailable {key[0]}-{key[1]:02d}: {note}")
