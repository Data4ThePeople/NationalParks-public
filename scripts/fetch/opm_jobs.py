"""Park Service staff by kind of job, from OPM's Federal Workforce Data (data.opm.gov).

Reads the person-level employment files for September 2012, 2023, 2024 and 2025
(the last month of FY2012, the last budget-table year FY2023, FY2024 and FY2025), keeps the National Park Service
(agency_subelement_code IN10) and groups people by occupational series into a
few plain job groups. Counts are people on board on the last day of the month,
not FTE, and include seasonal staff. Writes data/processed/nps_staff_by_job.csv
(one row per snapshot and job group) and nps_staff_by_series.csv (every series,
so each grouping choice can be checked).

Files are cached in data/raw/elsewhere/opm/ and downloaded only if missing.
"""
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/elsewhere/opm"
PROC = ROOT / "data/processed"
SNAPSHOTS = ["201209", "202309", "202409", "202509"]
API = "https://data.opm.gov/api/v1/files/employment"
UA = {"User-Agent": "Data 4 The People research (connect@data4thepeople.com)"}

# job groups, matched in order; each is (label, test on the 4-digit series code)
GROUPS = [
    ("Park rangers", lambda c: c == "0025"),
    ("Guides and education", lambda c: c in {"0090", "1701", "1702", "1712", "1750", "1084"}),
    ("Police, dispatch and safety", lambda c: c in {"0083", "0085", "0080", "1811", "2151", "0018", "0019", "0086"}),
    ("Firefighting", lambda c: c in {"0081", "0456", "0462"}),
    ("Custodians", lambda c: c == "3566"),
    ("Maintenance and trades", lambda c: c in {"1601", "1640", "1670"} or int(c) >= 2500),
    ("History, museums and archeology", lambda c: c in {"0170", "0193", "1010", "1015", "1016", "1420", "1421", "0102", "0190"}),
    ("Science and natural resources", lambda c: 400 <= int(c) <= 499 or 1300 <= int(c) <= 1399 or c == "0028"),
    ("Engineering, architecture and planning", lambda c: 800 <= int(c) <= 899 or c in {"0020", "0023"}),
    ("Office, finance and management", lambda c: 200 <= int(c) <= 399 or 500 <= int(c) <= 599 or 1100 <= int(c) <= 1199
     or 2000 <= int(c) <= 2299 or 900 <= int(c) <= 999 or 1000 <= int(c) <= 1099),
]


def group(code):
    if not code.isdigit():  # OPM marks a few records "*" / INVALID
        return "Other"
    for label, test in GROUPS:
        if test(code):
            return label
    return "Other"


def load(snap):
    path = RAW / f"emp_{snap}.parquet"
    if not path.exists():
        files = requests.get(API, params={"current": "true"}, headers=UA, timeout=60).json()
        f = next(f for f in files if f["year"] + f["month"] == snap)
        r = requests.get(f"{API}/{f['year']}/{f['month']}/{f['version']}/download", headers=UA, timeout=600)
        r.raise_for_status()
        path.write_bytes(r.content)
    t = pq.read_table(path, columns=["agency_subelement_code", "occupational_series_code", "occupational_series", "count"],
                      filters=[("agency_subelement_code", "=", "IN10")]).to_pandas()
    t["count"] = t["count"].astype(int)
    if t.occupational_series_code.isna().any() or (t["count"] != 1).any():
        raise SystemExit(f"{snap}: missing series code or a count other than 1")
    t["snapshot"] = snap
    return t


def main():
    t = pd.concat([load(s) for s in SNAPSHOTS])
    t["job_group"] = t.occupational_series_code.map(group)
    series = (t.groupby(["snapshot", "occupational_series_code", "occupational_series", "job_group"])["count"].sum()
              .rename("people").reset_index())
    series.to_csv(PROC / "nps_staff_by_series.csv", index=False)
    jobs = t.groupby(["snapshot", "job_group"])["count"].sum().rename("people").reset_index()
    jobs.to_csv(PROC / "nps_staff_by_job.csv", index=False)
    print(jobs.pivot(index="job_group", columns="snapshot", values="people").sort_values(SNAPSHOTS[-1], ascending=False))
    other = series[(series.job_group == "Other") & (series.snapshot == SNAPSHOTS[-1])]
    print("Other:", other[["occupational_series_code", "occupational_series", "people"]].to_string(index=False))


main()
