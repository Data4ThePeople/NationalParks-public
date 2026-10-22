"""Tie out data/processed/visits_annual.csv against the published IRMA report
"Annual Park Recreation Visitation (1904 - Last Calendar Year)" for every park.

The report is an SSRS report behind https://irma.nps.gov/Stats/. This script
opens the report viewer for each park, uses the viewer's own CSV export, and
caches the CSV in data/raw/irma_annual_report/<CODE>.csv. It writes no
processed file. It prints every (park, year) where the two differ, for years
1979 through the last year in the report (current-year preliminary months are
not in the report and are skipped).

Run: UV_PROJECT_ENVIRONMENT=.uvenv uv run python -I scripts/check_irma_annual.py [--refresh]
"""
import csv
import io
import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/irma_annual_report"
BASE = "https://irma.nps.gov"
REPORT = ("/Stats/SSRSReports/Park%20Specific%20Reports/"
          "Annual%20Park%20Recreation%20Visitation%20(1904%20-%20Last%20Calendar%20Year)?Park={code}")


def download(code: str) -> bytes:
    s = requests.Session()
    shell = s.get(BASE + REPORT.format(code=code), timeout=120).text
    m = re.search(r'src="(/Stats/MvcReportViewer\.aspx[^"]+)"', shell)
    if not m:
        raise SystemExit(f"{code}: report viewer frame not found")
    viewer = s.get(BASE + m.group(1).replace("&amp;", "&"), timeout=120).text
    m = re.search(r'ExportUrlBase":"([^"]+)"', viewer)
    if not m:
        raise SystemExit(f"{code}: export URL not found")
    url = BASE + m.group(1).replace("\\u0026", "&") + "CSV"
    r = s.get(url, timeout=120)
    r.raise_for_status()
    return r.content


def main() -> None:
    refresh = "--refresh" in sys.argv[1:]
    RAW.mkdir(parents=True, exist_ok=True)
    codes = sorted(p["code"] for p in json.loads((ROOT / "config/parks.json").read_text()))
    ours: dict[tuple[str, int], tuple[int, int]] = {}
    with open(ROOT / "data/processed/visits_annual.csv") as f:
        for row in csv.DictReader(f):
            ours[(row["code"], int(row["year"]))] = (int(row["recreation_visits"]),
                                                     int(row["months_reported"]))
    diffs, compared, missing = [], 0, []
    for code in codes:
        path = RAW / f"{code}.csv"
        if refresh or not path.exists():
            path.write_bytes(download(code))
            time.sleep(0.5)
        text = path.read_bytes().decode("utf-8-sig")
        lines = text.splitlines()
        start = next(i for i, l in enumerate(lines) if l.startswith("Year,"))
        published = {}
        for row in csv.DictReader(io.StringIO("\n".join(lines[start:]))):
            if row["Year"] and row["Year"].isdigit():
                published[int(row["Year"])] = int(row["RecreationVisitors"].replace(",", ""))
        last = max(published)
        years = sorted({y for (c, y) in ours if c == code and y <= last}
                       | {y for y in published if y >= 1979})
        for y in years:
            a, b = ours.get((code, y)), published.get(y)
            if a is None or b is None:
                missing.append(f"{code} {y}: ours={a} report={b}")
                continue
            compared += 1
            if a[0] != b:
                diffs.append(f"{code} {y}: ours={a[0]} ({a[1]} months) report={b} diff={a[0]-b}")
    print(f"compared {compared} park-years; {len(diffs)} differ; {len(missing)} present on one side only")
    for d in diffs + missing:
        print("  " + d)


if __name__ == "__main__":
    main()
