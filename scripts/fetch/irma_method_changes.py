"""Build config/visit_method_changes.json from the IRMA report
"Park Visitor Use and Count Procedure Changes", one report per park.

The report lists, for each set of Visitor Use Counting and Reporting
Instructions a park has used, the level of change the NPS assigns
(Overhaul, Major, Minor, Non-material) and a one-line description of each
change. Rows with level "N/A" (the first set of instructions on record, and a
few placeholders) are left out.

Output: {code: [{"year": first year the instructions apply, "note": level
and descriptions as published, "source": report URL}]}. The year is the first
year in the report's period label, for example 2013 for "2013 - 2023".

Raw CSV exports are cached in data/raw/irma_changes/<CODE>.csv.
Run: UV_PROJECT_ENVIRONMENT=.uvenv uv run python -I scripts/fetch/irma_method_changes.py [--refresh]
"""
import csv
import io
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/irma_changes"
BASE = "https://irma.nps.gov"
REPORT = "Park Specific Reports/Park Visitor Use and Count Procedure Changes"
LEVELS = ["Overhaul", "Major", "Minor", "Non-material"]


def report_url(code: str) -> str:
    return f"{BASE}/Stats/SSRSReports/{quote(REPORT)}?Park={code}"


def download(code: str) -> bytes:
    s = requests.Session()
    shell = s.get(report_url(code), timeout=180).text
    m = re.search(r'src="(/Stats/MvcReportViewer\.aspx[^"]+)"', shell)
    if not m:
        raise SystemExit(f"{code}: report viewer frame not found")
    viewer = s.get(BASE + m.group(1).replace("&amp;", "&"), timeout=180).text
    m = re.search(r'ExportUrlBase":"([^"]+)"', viewer)
    if not m:
        raise SystemExit(f"{code}: export URL not found")
    r = s.get(BASE + m.group(1).replace("\\u0026", "&") + "CSV", timeout=180)
    r.raise_for_status()
    return r.content


def main() -> None:
    refresh = "--refresh" in sys.argv[1:]
    RAW.mkdir(parents=True, exist_ok=True)
    codes = sorted(p["code"] for p in json.loads((ROOT / "config/parks.json").read_text()))
    out = {}
    for code in codes:
        path = RAW / f"{code}.csv"
        if refresh or not path.exists():
            path.write_bytes(download(code))
            time.sleep(0.5)
        lines = path.read_bytes().decode("utf-8-sig").splitlines()
        if f"- {code}" not in "\n".join(lines[:3]):
            raise SystemExit(f"{code}: report title does not name the park")
        start = next(i for i, l in enumerate(lines) if l.startswith("Title1,"))
        by_year: dict[int, dict[str, list[str]]] = {}
        for row in csv.DictReader(io.StringIO("\n".join(lines[start:]))):
            level, detail = row["UpdateLevel1"].strip(), " ".join(row["UpdateDetail"].split())
            if level == "N/A":
                continue
            if level not in LEVELS:
                raise SystemExit(f"{code}: unknown change level {level!r}")
            m = re.search(r":\s*(\d{4})\s*-\s*(\d{4}|Present)?\s*$", row["Title1"])
            if not m:
                raise SystemExit(f"{code}: cannot read period from {row['Title1']!r}")
            by_year.setdefault(int(m.group(1)), {}).setdefault(level, []).append(detail)
        entries = []
        for year in sorted(by_year):
            parts = [f"{lvl}: " + "; ".join(by_year[year][lvl])
                     for lvl in LEVELS if lvl in by_year[year]]
            entries.append({"year": year, "note": " | ".join(parts), "source": report_url(code)})
        if entries:
            out[code] = entries
    dest = ROOT / "config/visit_method_changes.json"
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    n = sum(len(v) for v in out.values())
    print(f"wrote {dest} ({n} park-years with changes, {len(out)} parks)")
    since = {c: [e["year"] for e in v if e["year"] >= 2015] for c, v in out.items()}
    print("change years since 2015:", {c: y for c, y in since.items() if y})


if __name__ == "__main__":
    main()
