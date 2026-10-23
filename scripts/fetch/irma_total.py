"""System-wide recreation visits (all Park Service units) by calendar year, from IRMA's total/{year}
operation. Used only to put agency-wide OPM staff counts on a per-visit basis. Writes
data/processed/visits_system.csv. Raw JSON is cached in data/raw/irma_total/.
"""
import json
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/irma_total"
YEARS = [2012, 2023, 2024, 2025]


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    rows = []
    for y in YEARS:
        path = RAW / f"{y}.json"
        if not path.exists():
            r = requests.get(f"https://irmaservices.nps.gov/v3/rest/stats/total/{y}",
                             headers={"Accept": "application/json"}, timeout=120)
            r.raise_for_status()
            path.write_text(r.text)
        months = json.loads(path.read_text())
        if sorted(m["Month"] for m in months) != list(range(1, 13)):
            raise SystemExit(f"{y}: not 12 months")
        rows.append({"year": y, "recreation_visits": sum(int(m["RecreationVisitors"]) for m in months)})
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "data/processed/visits_system.csv", index=False)
    print(out.to_string(index=False))


main()
