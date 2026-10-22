"""Fetch monthly visitation for the 63 national parks from the NPS IRMA
visitor use statistics REST service (v3), and write

  data/processed/visits_monthly.csv  code,year,month,recreation_visits,nonrecreation_visits
  data/processed/visits_annual.csv   code,year,recreation_visits,months_reported

Two IRMA sources, both cached under data/raw/irma/ so the build reruns offline:

1. Final years: the REST service, one XML file per park (data/raw/irma/<CODE>.xml).
   As of Oct 2026 it returns nothing for the current calendar year.
2. Current-year preliminary months: the IRMA Stats SSRS report "Monthly Public
   Use" (one CSV export per park-month, data/raw/irma/prelim/<CODE>_<YYYY>-<MM>.csv),
   for months after the last month the REST service returns. The NPS labels
   these months preliminary until the year is finalized (first quarter of the
   next year). Each export also carries the same month one year earlier; that
   value is checked against the REST service. Pass --final-only to skip this
   step and keep only what the REST service returns.

Without --refresh the cache is used (a park with no preliminary cache is
fetched once); with it everything is downloaded again.

Checks (hard failures): HTTP errors, an empty response, a unit code we did not
ask for, a UnitName that does not match the park in config/parks.json, a
duplicate (code, year, month), an unparseable number, or a month outside
1 to 12. Negative values are kept as published and printed.
No gap filling: months IRMA does not return stay absent.

Prints each park's first and last month in IRMA and any missing months
inside that range (written to no file, per research/CONTRACT.md).
"""
import csv
import datetime as dt
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/irma"
OUT = ROOT / "data/processed"
URL = "https://irmaservices.nps.gov/v3/rest/stats/visitation"
NS = "{http://schemas.datacontract.org/2004/07/NPS.IrmaServices.Rest.v3.Stats}"
START_YEAR = 1979
PRELIM = RAW / "prelim"
STATS = "https://irma.nps.gov"
MPU = "/Stats/SSRSReports/" + quote("Park Specific Reports/Monthly Public Use")
FIELDS = ("Month", "NonRecreationVisitors", "RecreationVisitors", "UnitCode", "UnitName", "Year")

# IRMA abbreviates unit types in UnitName. These are expanded before the name
# is compared with config/parks.json.
ABBREV = [(r"\bNP\b", "National Park"), (r"\bN PARK\b", "National Park"),
          (r"\bNPRES\b", "National Preserve"), (r"\bPRES\b", "Preserve"),
          (r"\bNM\b", "National Monument"), (r"\bNMEM\b", "National Memorial"),
          (r"\bNPP\b", "National Park and Preserve"), (r"&", "and")]


def core(name: str) -> str:
    """Reduce a park name to its place-name part for comparison."""
    s = name
    for pat, rep in ABBREV:
        s = re.sub(pat, rep, s)
    s = s.lower().replace("&", "and")
    s = re.sub(r"['\u2018\u2019\u02bb]", "", s)  # Hawai'i vs Hawaii
    s = re.sub(r"\b(national|park|preserve|parks|and|of|the|monument|memorial)\b", " ", s)
    s = re.sub(r"[^a-z ]", " ", s)
    return " ".join(s.split())


def fetch(code: str, end_year: int) -> bytes:
    params = {"unitCodes": code, "startMonth": 1, "startYear": START_YEAR,
              "endMonth": 12, "endYear": end_year}
    for attempt in range(4):
        try:
            r = requests.get(URL, params=params, timeout=120)
            r.raise_for_status()
            return r.content
        except requests.RequestException as e:
            if attempt == 3:
                raise SystemExit(f"{code}: download failed: {e}")
            time.sleep(5 * (attempt + 1))
    raise AssertionError


def fetch_mpu(code: str, year: int, month: int) -> bytes | None:
    """CSV export of the Monthly Public Use report, or None if the month is not posted."""
    for attempt in range(4):
        try:
            return _fetch_mpu(code, year, month)
        except requests.RequestException as e:
            if attempt == 3:
                raise SystemExit(f"{code} {year}-{month:02d}: Monthly Public Use failed: {e}")
            time.sleep(10 * (attempt + 1))
    raise AssertionError


def _fetch_mpu(code: str, year: int, month: int) -> bytes | None:
    sess = requests.Session()
    shell = sess.get(f"{STATS}{MPU}?Park={code}&RptDate={month}/1/{year}", timeout=180).text
    m = re.search(r'src="(/Stats/MvcReportViewer\.aspx[^"]+)"', shell)
    if not m:  # retried by fetch_mpu; a server error page has no frame
        raise requests.RequestException(f"{code}: Monthly Public Use viewer frame not found")
    viewer = sess.get(STATS + m.group(1).replace("&amp;", "&"), timeout=180).text
    m = re.search(r'ExportUrlBase":"([^"]+)"', viewer)
    if not m:
        # The report's "Rpt Date" list holds only the months this park has
        # posted. A month missing from it is not posted yet; a listed month
        # that fails to render is a server problem and is retried.
        i = viewer.find("Rpt Date")
        posted = re.findall(r"<option[^>]*>([A-Z][a-z]{2})&nbsp;(\d{4})</option>",
                            viewer[i:i + 20000]) if i >= 0 else []
        if not posted:
            raise requests.RequestException(f"{code}: report date list not found")
        label = (dt.date(year, month, 1).strftime("%b"), str(year))
        if label not in posted:
            return None
        raise requests.RequestException(f"{code} {year}-{month:02d}: listed but not rendered")
    r = sess.get(STATS + m.group(1).replace("\\u0026", "&") + "CSV", timeout=180)
    r.raise_for_status()
    return r.content


def num(code: str, field: str, text: str) -> int:
    t = text.replace(",", "").strip()
    if not re.fullmatch(r"-?\d+", t):
        raise SystemExit(f"{code}: unparseable {field} value {text!r}")
    return int(t)


def preliminary(code: str, name: str, after: tuple[int, int], refresh: bool,
                final: dict) -> dict[tuple[int, int], tuple[int, int]]:
    """Preliminary months after `after` (year, month) up to last month."""
    today = dt.date.today()
    stop = (today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12)
    marker = PRELIM / f"{code}_checked.txt"
    online = refresh or not marker.exists()
    out = {}
    y, m = after
    while True:
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
        if (y, m) > stop:
            break
        path = PRELIM / f"{code}_{y}-{m:02d}.csv"
        if online:
            raw = fetch_mpu(code, y, m)
            time.sleep(0.2)
            if raw is None:
                break
            path.write_bytes(raw)
        elif not path.exists():
            break
        rows = list(csv.reader(path.read_bytes().decode("utf-8-sig").splitlines()))
        if len(rows) < 2:
            raise SystemExit(f"{path}: no data row")
        rec = dict(zip(rows[0], rows[1]))
        if rec.get("Textbox33") != f"{m}/{y}":
            raise SystemExit(f"{path}: report month is {rec.get('Textbox33')!r}")
        if core(rec.get("ParkName", "")) != core(name):
            raise SystemExit(f"{path}: report park is {rec.get('ParkName')!r}")
        rv, nrv = num(code, "Field1", rec["Field1"]), num(code, "Field2", rec["Field2"])
        if (num(code, "Field26", rec["Field26"]), num(code, "Field29", rec["Field29"])) != (rv, nrv):
            raise SystemExit(f"{path}: month totals disagree inside the report")
        prior = final.get((code, y - 1, m))
        got = (num(code, "Field27", rec["Field27"]), num(code, "Field30", rec["Field30"]))
        if prior is not None and got != prior:
            raise SystemExit(f"{path}: prior-year month {got} differs from REST {prior}")
        out[(y, m)] = (rv, nrv)
    if online:
        marker.write_text(f"checked {today.isoformat()}; months found: {len(out)}\n")
    return out


def to_int(code: str, field: str, text: str | None) -> int:
    if text is None or not re.fullmatch(r"-?\d+", text.strip()):
        raise SystemExit(f"{code}: unparseable {field} value {text!r}")
    v = int(text)
    return v


def main() -> None:
    refresh = "--refresh" in sys.argv[1:]
    final_only = "--final-only" in sys.argv[1:]
    parks = json.loads((ROOT / "config/parks.json").read_text())
    names = {p["code"]: p["name"] for p in parks}
    if len(names) != 63:
        raise SystemExit(f"expected 63 parks in config/parks.json, got {len(names)}")
    RAW.mkdir(parents=True, exist_ok=True)
    PRELIM.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    end_year = dt.date.today().year

    monthly: dict[tuple[str, int, int], tuple[int, int]] = {}
    api_names: dict[str, set[str]] = {}
    for code in sorted(names):
        path = RAW / f"{code}.xml"
        if refresh or not path.exists():
            path.write_bytes(fetch(code, end_year))
            time.sleep(0.3)
        root = ET.fromstring(path.read_bytes())
        rows = root.findall(f"{NS}VisitationData")
        if not rows:
            raise SystemExit(f"{code}: IRMA returned no rows")
        for el in rows:
            rec = {f: (el.findtext(f"{NS}{f}")) for f in FIELDS}
            if rec["UnitCode"] != code:
                raise SystemExit(f"{code}: response has unit code {rec['UnitCode']!r}")
            api_names.setdefault(code, set()).add(rec["UnitName"] or "")
            year = to_int(code, "Year", rec["Year"])
            month = to_int(code, "Month", rec["Month"])
            if not 1 <= month <= 12 or not START_YEAR <= year <= end_year:
                raise SystemExit(f"{code}: bad year/month {year}-{month}")
            key = (code, year, month)
            if key in monthly:
                raise SystemExit(f"duplicate key {key}")
            monthly[key] = (to_int(code, "RecreationVisitors", rec["RecreationVisitors"]),
                            to_int(code, "NonRecreationVisitors", rec["NonRecreationVisitors"]))

    bad = []
    for code, ns in sorted(api_names.items()):
        if len(ns) != 1:
            bad.append(f"{code}: more than one UnitName {sorted(ns)}")
        elif core(next(iter(ns))) != core(names[code]):
            bad.append(f"{code}: IRMA name {next(iter(ns))!r} vs config {names[code]!r}")
    if bad:
        raise SystemExit("UnitName check failed:\n  " + "\n  ".join(bad))

    prelim_rows = {}
    if not final_only:
        final = dict(monthly)
        for code in sorted(names):
            last = max((y, m) for (c, y, m) in final if c == code)
            for (y, m), v in preliminary(code, next(iter(api_names[code])), last,
                                         refresh, final).items():
                if (code, y, m) in monthly:
                    raise SystemExit(f"duplicate key {(code, y, m)}")
                monthly[(code, y, m)] = v
                prelim_rows[(code, y, m)] = v

    with open(OUT / "visits_monthly.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["code", "year", "month", "recreation_visits", "nonrecreation_visits"])
        for (code, y, m), (rv, nrv) in sorted(monthly.items()):
            w.writerow([code, y, m, rv, nrv])

    annual: dict[tuple[str, int], list[int]] = {}
    for (code, y, m), (rv, _) in monthly.items():
        a = annual.setdefault((code, y), [0, 0])
        a[0] += rv
        a[1] += 1
    with open(OUT / "visits_annual.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["code", "year", "recreation_visits", "months_reported"])
        for (code, y), (rv, n) in sorted(annual.items()):
            w.writerow([code, y, rv, n])

    coverage = {}
    for code in sorted(names):
        keys = sorted((y, m) for (c, y, m) in monthly if c == code and (c, y, m) not in prelim_rows)
        first, last = keys[0], keys[-1]
        have = set(keys)
        gaps = []
        y, m = first
        while (y, m) <= last:
            if (y, m) not in have:
                gaps.append(f"{y}-{m:02d}")
            y, m = (y + 1, 1) if m == 12 else (y, m + 1)
        coverage[code] = {"irma_name": next(iter(api_names[code])),
                          "first": f"{first[0]}-{first[1]:02d}", "last": f"{last[0]}-{last[1]:02d}",
                          "missing_months_inside_range": gaps}

    late = {c: v["first"] for c, v in coverage.items() if v["first"] != f"{START_YEAR}-01"}
    print(f"wrote {len(monthly)} monthly rows, {len(annual)} annual rows for {len(names)} parks")
    print(f"latest month from the REST service: {max(v['last'] for v in coverage.values())}")
    pm = {}
    for (c, y, m) in prelim_rows:
        pm.setdefault(f"{y}-{m:02d}", []).append(c)
    print(f"preliminary rows added from Monthly Public Use: {len(prelim_rows)}; "
          f"parks per month: {dict(sorted((k, len(v)) for k, v in pm.items()))}")
    print(f"parks whose IRMA history starts after {START_YEAR}-01: {late}")
    gaps = {c: v["missing_months_inside_range"] for c, v in coverage.items()
            if v["missing_months_inside_range"]}
    neg = [f"{c} {y}-{m:02d} rec={rv} nonrec={nrv}"
           for (c, y, m), (rv, nrv) in sorted(monthly.items()) if rv < 0 or nrv < 0]
    print(f"negative values kept as published: {neg}")
    print(f"parks with missing months inside their range: {gaps}")


if __name__ == "__main__":
    main()
