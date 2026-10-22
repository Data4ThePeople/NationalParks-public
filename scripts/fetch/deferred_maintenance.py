"""Build data/processed/deferred_maintenance.csv: NPS deferred maintenance and
repairs (DM&R) dollars for the 63 national parks, for every fiscal year that
official sources let us recover.

Run:
    UV_PROJECT_ENVIRONMENT=.uvenv uv run python -I scripts/fetch/deferred_maintenance.py [--refresh]

Sources, oldest to newest (method notes in research/datasets/30_deferred_maintenance.md):

  FY2014-FY2018  "Deferred Maintenance by State and Park" PDFs that NPS posted on
                 nps.gov and later removed. Read from Wayback Machine captures.
                 Every distinct capture (by Wayback digest) is downloaded and
                 parsed; state subtotals and the national total are checked.
  FY2022         NPS "DM&R Park Fact Sheets" sortable dataset (exact dollars),
                 every archived version of its JSON/CSV. The earlier FY2022 Q1
                 version of the same dataset is a mid-year snapshot, not a
                 year-end figure, so it is parsed for the record but not written.
  FY2023         CRS Report R48136 (July 25, 2024), Table 4, which lists the 20
                 park units with the highest FY2023 DM&R "using data from NPS".
                 NPS did not post park-level FY2023 numbers that we could find.
  FY2024         NPS park fact sheet PDFs (".../<Park-Name>-Deferred-Maintenance-
                 and-Repairs-Factsheet.pdf"), Wayback captures whose text says
                 "end of Fiscal Year (FY) 2024". Dollars are rounded as printed.
  FY2025         DOI unit-level DM&R workbook (exact dollars, FRPP as of
                 2025-09-30), plus the live NPS fact sheets (rounded) as a second
                 copy.

Overlap rule (research/CONTRACT.md): when two copies give a value for the same
(code, fy), keep the most recent copy (latest capture date; on a tie, the more
precise copy) and list every disagreement in research/dm_overlap.md. A rounded
copy only "disagrees" when the exact value falls outside its rounding range.

Combined units: NPS reports Sequoia and Kings Canyon as one unit (SEKI) and
Kobuk Valley inside Western Arctic National Parklands (WEAR). The unit figure is
written on each member park's row and flagged in method_note ("do not sum").

Downloaded files are untrusted: they are parsed, never executed.
"""
import csv
import gzip
import html
import io
import json
import re
import sys
import time
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from datetime import date
from pathlib import Path

import pypdf
import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/dm"
OUT = ROOT / "data/processed/deferred_maintenance.csv"
OVERLAP_MD = ROOT / "research/dm_overlap.md"
REFRESH = "--refresh" in sys.argv
TODAY = date.today().isoformat()
UA = {"User-Agent": "Data4ThePeople research (connect@data4thepeople.com)"}
WB_SLEEP = 3  # seconds between Wayback Machine requests

PARKS = {p["code"]: p["name"] for p in json.loads((ROOT / "config/parks.json").read_text())}
if len(PARKS) != 63:
    raise SystemExit(f"config/parks.json has {len(PARKS)} parks, expected 63")

# Unit codes used by NPS reports that cover more than one of our parks.
COMBINED = {"SEKI": ["SEQU", "KICA"], "WEAR": ["KOVA"]}
COMBINED_NOTE = {
    "SEKI": "unit SEKI (Sequoia and Kings Canyon) reported as one figure; same value on SEQU and KICA rows; do not sum",
    "WEAR": "unit WEAR (Western Arctic National Parklands: Kobuk Valley, Cape Krusenstern, Noatak) reported as one figure; covers more than Kobuk Valley",
}
PARK_AND_PRESERVE = {"DENA", "GAAR", "GLBA", "GRSA", "KATM", "LACL", "WRST", "NERI"}
PP_NOTE = "figure covers the whole park and preserve unit"

# Names used by NPS park lists and DOI workbooks, where they differ from config/parks.json.
NPS_LIST_NAME = {
    "DENA": "Denali National Park and Preserve",
    "GAAR": "Gates of the Arctic National Park and Preserve",
    "GLBA": "Glacier Bay National Park and Preserve",
    "GRSA": "Great Sand Dunes National Park and Preserve",
    "KATM": "Katmai National Park and Preserve",
    "LACL": "Lake Clark National Park and Preserve",
    "WRST": "Wrangell-St. Elias National Park and Preserve",
    "SEKI": "Sequoia and Kings Canyon National Parks",
    "WEAR": "Western Arctic National Parklands",
}
DOI_NAME = {
    "DENA": "Denali National Park and Preserve",
    "GAAR": "Gates of the Arctic National Park and Preserve",
    "GLBA": "Glacier Bay National Park and Preserve",
    "GRSA": "Great Sand Dunes National Monument and Preserve",
    "KATM": "Katmai National Park and Preserve",
    "LACL": "Lake Clark National Park and Preserve",
    "WRST": "Wrangell St Elias National Park",
    "NERI": "New River Gorge National River",
    "HAVO": "Hawaii Volcanoes National Park",
    "HALE": "Haleakal? National Park",
    "SEKI": "Sequoia and Kings Canyon National Park",
    "WEAR": "Western Artic National Parklands",
}
# CRS Table 4 names.
CRS_NAME = {"SEKI": "Sequoia and Kings Canyon National Park"}


def report_units():
    """Unit codes as NPS reports them: our parks, with SEKI and WEAR replacing members."""
    units = [c for c in PARKS if c not in ("SEQU", "KICA", "KOVA")]
    return units + ["SEKI", "WEAR"]


def unit_name(code, table):
    return table.get(code) or NPS_LIST_NAME.get(code) or PARKS[code]


def norm(name):
    """Match key for park names: no accents, apostrophes, punctuation or case."""
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = s.replace("&", "and").replace("?", "a")  # DOI prints Haleakala as "Haleakal?"
    return re.sub(r"[^a-z0-9]", "", s.lower())


# --------------------------------------------------------------------------- fetching
_last_wb = [0.0]


def _get(url, wayback):
    for attempt in range(6):
        if wayback:
            wait = WB_SLEEP - (time.time() - _last_wb[0])
            if wait > 0:
                time.sleep(wait)
        try:
            r = requests.get(url, headers=UA, timeout=180)
        except requests.RequestException as e:
            print(f"  retry ({e.__class__.__name__}) {url}")
            time.sleep(15 * (attempt + 1))
            continue
        finally:
            if wayback:
                _last_wb[0] = time.time()
        offline = b"Temporarily Offline" in r.content[:4000]
        if r.status_code == 200 and not offline:
            return r.content
        if r.status_code == 404 and not wayback:
            return None
        print(f"  retry (HTTP {r.status_code}{' offline' if offline else ''}) {url}")
        time.sleep(15 * (attempt + 1))
    raise SystemExit(f"could not fetch {url}")


def cached(path, url, wayback=False, allow_404=False):
    """Return bytes from cache, downloading if missing or --refresh (live files only)."""
    path = RAW / path
    gone = path.with_name(path.name + ".404")  # remembers a 404 so offline reruns work
    if not (REFRESH and not wayback):
        if path.exists():
            return path.read_bytes()
        if allow_404 and gone.exists():
            return None
    data = _get(url, wayback)
    if data is None:
        if allow_404:
            gone.parent.mkdir(parents=True, exist_ok=True)
            gone.write_text(f"404 on {TODAY}: {url}\n")
            return None
        raise SystemExit(f"404 for {url}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def wb_url(ts, orig, raw=True):
    return f"https://web.archive.org/web/{ts}{'id_' if raw else ''}/{orig}"


def wb_get(sub, ts, orig):
    name = re.sub(r"[^A-Za-z0-9._-]", "_", orig.split("?")[0].rstrip("/").split("/")[-1])
    return cached(f"{sub}/{ts}_{name}", wb_url(ts, orig), wayback=True)


def cdx(name, **params):
    """Wayback CDX query, cached as data/raw/dm/cdx/<name>.txt. Returns list of rows."""
    q = {"output": "text", "fl": "timestamp,original,statuscode,mimetype,digest"}
    q.update(params)
    url = "https://web.archive.org/cdx/search/cdx?" + "&".join(f"{k}={v}" for k, v in q.items())
    path = RAW / "cdx" / f"{name}.txt"
    if path.exists() and not REFRESH:
        text = path.read_text()
    else:
        text = ""
        for attempt in range(6):
            data = _get(url, wayback=True)
            text = data.decode("utf-8", "replace")
            if "<html" not in text[:200].lower():
                break
            time.sleep(20 * (attempt + 1))
        else:
            raise SystemExit(f"CDX failed: {url}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return [line.split() for line in text.splitlines() if line.strip()]


def distinct_captures(rows, mime=None):
    """One capture per distinct digest, status 200, oldest first."""
    seen, out = set(), []
    for ts, orig, status, mt, digest in sorted(rows):
        if status != "200" or (mime and mt != mime) or digest in seen:
            continue
        seen.add(digest)
        out.append((ts, orig))
    return out


def ts_date(ts):
    return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"


def decode(b):
    if b[:2] == b"\x1f\x8b":
        b = gzip.decompress(b)
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            pass


def pdf_text(b):
    return "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(io.BytesIO(b)).pages)


def money(s):
    s = s.replace("$", "").replace(",", "").strip()
    if s in ("-", ""):
        return 0
    if not re.fullmatch(r"\d+(\.\d+)?", s):
        raise SystemExit(f"unparseable number {s!r}")
    return round(float(s))


# --------------------------------------------------------------------------- records
records = []  # dicts: unit, fy, dollars, precision, source_url, captured, note, source


def add(unit, fy, dollars, precision, source_url, captured, note, source):
    records.append(dict(unit=unit, fy=fy, dollars=dollars, precision=precision,
                        source_url=source_url, captured=captured, note=note, source=source))


# --------------------------------------------------------------------------- FY2014-FY2018 PDFs
STATE_PARK = [
    (2014, "nps.gov/subjects/plandesignconstruct/upload/FY14-DM-by-State-and-Park_2015-03-13.pdf"),
    (2014, "nps.gov/subjects/plandesignconstruct/upload/FY14-DM-by-State-and-Park_2015-10-20.pdf"),
    (2015, "nps.gov/subjects/plandesignconstruct/upload/FY-2015-DM-by-State-and-Park.pdf"),
    (2015, "nps.gov/subjects/infrastructure/upload/FY-2015-DM-by-State-and-Park.pdf"),
    (2016, "nps.gov/subjects/infrastructure/upload/FY16-Deferred-Maintenance-by-State-and-Park.pdf"),
    (2017, "nps.gov/subjects/infrastructure/upload/FY17-NPS-Deferred-Maintenance-by-State-and-Park_508.pdf"),
    (2018, "nps.gov/subjects/infrastructure/upload/NPS-Deferred-Maintenance-FY18-State_and_Park_2018.pdf"),
]
AMT = r"(\$\s*-|-\$|\$\s*[\d,]+|[\d,]+\$)"
NOTE_1418 = "FMSS work orders at fiscal year end; construction cost only (no 35% project markup on non-transportation assets)"
national_totals = {}
doi_checks = {}  # totals used for the checks table in research/dm_overlap.md


def parse_state_park(text, label):
    m = re.search(r"Data as of September 30(?:th)?, (\d{4})", text)
    if not m:
        raise SystemExit(f"{label}: no 'Data as of' date")
    fy = int(m.group(1))
    t = re.sub(r"(\$[\d,]*,)\s*\n\s*(\d)", r"\1\2", text)  # numbers wrapped across lines
    t = re.sub(r"(\d,)\s*\n\s*(\d{3})", r"\1\2", t)
    token = re.compile(r"\(([A-Z]{4})\)\s*" + AMT + r"|Total\s*►\s*" + AMT)
    # Rows are printed in whole dollars, so a printed total can differ from the sum of
    # printed rows by up to about $1 per row. Allow that, nothing more.
    by_unit, state_sum, state_n, grand, grand_n, national = {}, 0, 0, 0, 0, None
    for m in token.finditer(t):
        if m.group(1):
            v = money(m.group(2))
            by_unit[m.group(1)] = by_unit.get(m.group(1), 0) + v
            state_sum += v
            state_n += 1
            grand += v
            grand_n += 1
        else:
            v = money(m.group(3))
            if state_n and abs(v - state_sum) <= state_n:
                state_sum, state_n = 0, 0
            elif state_n == 0 and national is None:
                # The national line. It is recorded, not enforced: the FY2016 PDF's own
                # state totals sum to $347,942 less than its printed national total.
                national = v
            else:
                raise SystemExit(f"{label}: total {v:,} matches neither state sum {state_sum:,} nor grand {grand:,}")
    if state_n:
        raise SystemExit(f"{label}: {state_sum:,} left after last state total")
    return fy, by_unit, national, grand


def fetch_state_park():
    for fy_expected, orig in STATE_PARK:
        name = re.sub(r"\W", "_", orig.split("/")[-1])
        rows = cdx(f"sp_{name}", url=orig, collapse="digest")
        caps = distinct_captures(rows, "application/pdf")
        if not caps:  # e.g. only "revisit" records that point at an identical file elsewhere
            print(f"  no distinct PDF capture for {orig}; skipped")
            continue
        for ts, o in caps:
            b = wb_get("state_park", ts, o)
            fy, by_unit, national, grand = parse_state_park(pdf_text(b), f"{ts} {o}")
            if fy != fy_expected:
                raise SystemExit(f"{o}: says FY{fy}, expected FY{fy_expected}")
            national_totals[(fy, ts, o)] = (national, grand)
            for unit in report_units():
                if unit not in by_unit:
                    raise SystemExit(f"{o} ({ts}): unit {unit} not found")
                add(unit, fy, by_unit[unit], 1, wb_url(ts, o, raw=False), ts_date(ts), NOTE_1418, "nps_state_park_pdf")


# --------------------------------------------------------------------------- FY2022 park dataset
DS_PARKS = "nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/*"
NOTE_22 = ("FMSS; 35% project markup on non-transportation assets (from FY2021); "
           "parametric condition assessment rollout began FY2022")
q1_snapshot = {}


def fetch_fy2022():
    rows = cdx("sortable_9143F3CC", url=DS_PARKS, collapse="digest")
    caps = [(ts, o) for ts, o in distinct_captures(rows) if re.search(r"\.(json|csv)", o)]
    code_by_name = {}
    versions = []
    for ts, o in caps:
        t = decode(wb_get("sortable", ts, o))
        if o.split("?")[0].endswith(".json"):
            d = json.loads(t)
            header, data = [h.strip() for h in d["COLUMNS"]], d["DATA"]
        else:
            r = list(csv.reader(io.StringIO(t)))
            header, data = [h.strip() for h in r[0]], r[1:]
        if "DM&R" not in header:
            continue
        i_dm, i_name = header.index("DM&R"), header.index("Park Name")
        links = " ".join(" ".join(map(str, x)) for x in data)
        is_q1 = "FY22Q1" in links
        table = {}
        for x in data:
            name = norm(x[i_name])
            if name in table:
                raise SystemExit(f"{o}: duplicate park {name}")
            table[name] = money(x[i_dm])
            m = re.search(r"/upload/([A-Z]{4})-(?:FY-2022|Park-Fact-Sheet)", " ".join(map(str, x)))
            if m:
                code_by_name.setdefault(name, m.group(1))
        versions.append((ts, o, is_q1, table))
    for ts, o, is_q1, table in versions:
        doi_checks.setdefault("dataset_sums", []).append((ts, is_q1, sum(table.values())))
        for unit in report_units():
            name = norm(unit_name(unit, NPS_LIST_NAME))
            if name not in table:
                raise SystemExit(f"{o} ({ts}): {unit_name(unit, NPS_LIST_NAME)} missing")
            if code_by_name.get(name, unit) != unit:
                raise SystemExit(f"{name}: link code {code_by_name[name]} != {unit}")
            if is_q1:
                q1_snapshot[unit] = (table[name], ts, o)
            else:
                add(unit, 2022, table[name], 1, wb_url(ts, o, raw=False),
                    ts_date(ts), NOTE_22, "nps_park_dataset")


# --------------------------------------------------------------------------- FY2023 CRS
CRS_2024 = "https://www.everycrsreport.com/files/2024-07-25_R48136_b8f735eff6a455e0ad5cff787c7348b59f659b10.html"
NOTE_23 = ("FRPP-aligned asset portfolio (from FY2023); FHWA road model update (from FY2023); "
           "CRS Table 4 top-20 units only, rounded to $1 million")


def fetch_fy2023():
    t = decode(cached("docs/crs_R48136_2024-07-25.html", CRS_2024))
    t = re.sub(r"<img[^>]*>|<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    s = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
    i = s.index("Table 4. NPS Units with the Highest Deferred Maintenance, FY2023 ($ in billions)")
    j = s.index("Source: CRS", i)
    block = s[i:j]
    for unit in report_units():
        name = unit_name(unit, CRS_NAME)
        m = re.search(re.escape(name) + r" [A-Z]{2}(?:, [A-Z]{2})* (\d\.\d{3})", block)
        if m:
            add(unit, 2023, round(float(m.group(1)) * 1e9), 1e6, CRS_2024, TODAY, NOTE_23, "crs_r48136_table4")


# --------------------------------------------------------------------------- FY2024/FY2025 NPS fact sheets
FS_LIST = ("https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/"
           "200BB9B9-04DB-1CE3-39B1E0967C744AE5/nri-DMParkFactSheettoConverttoaCSV2026v2.csv")
FS_LIST_FY24 = "nps.gov/common/uploads/sortable_dataset/infrastructure/D0740EDE-A5ED-7B62-F191A6D4B49F326E/nri-DMParkFactSheettoConverttoaCSVFY2420250317.csv"
NOTE_2425 = "FRPP portfolio; parametric condition assessment; fact sheet figure rounded as printed"
UNIT = {"K": 1e3, "M": 1e6, "B": 1e9}


def parse_factsheet(text, label):
    fy = re.search(r"as of the end of\s+Fiscal\s+Year\s+\(FY\)\s+(\d{4})", text)
    dm = re.search(r"estimated \$([\d,.]+)\s*([KMB])\s+in\s+Deferred\s+Maintenance", text)
    if not fy or not dm:
        raise SystemExit(f"{label}: could not find FY or DM&R")
    num = dm.group(1).replace(",", "")
    if not re.fullmatch(r"\d+(\.\d+)?", num):
        raise SystemExit(f"{label}: unparseable {dm.group(1)!r}")
    # precision = one unit in the last printed digit
    dec = len(num.split(".")[1]) if "." in num else 0
    prec = UNIT[dm.group(2)] / 10 ** dec
    return int(fy.group(1)), round(float(num) * UNIT[dm.group(2)]), prec, f"${dm.group(1)} {dm.group(2)}"


def fs_url_for(unit, lists):
    name = norm(unit_name(unit, NPS_LIST_NAME))
    for rows in lists:
        for r in rows:
            if norm(r[0]) == name:
                m = re.search(r'href="([^"]+\.pdf)"', r[2])
                if m:
                    return m.group(1)
    raise SystemExit(f"no fact sheet link for {unit} ({name})")


def fetch_factsheets():
    live_rows = list(csv.reader(io.StringIO(decode(cached("factsheet_list_2026v2.csv", FS_LIST)))))[1:]
    rows = cdx("fslist_fy24", url=FS_LIST_FY24, collapse="digest")
    ts, o = distinct_captures(rows)[0]
    fy24_rows = list(csv.reader(io.StringIO(decode(wb_get("sortable", ts, o)))))[1:]
    for unit in report_units():
        url = fs_url_for(unit, [live_rows, fy24_rows])
        fname = url.split("/")[-1]
        # live copy (current fiscal year)
        b = cached(f"factsheets/live/{fname}", url, allow_404=True)
        if not b:
            print(f"  live fact sheet returns 404: {url}")
        else:
            fy, v, prec, shown = parse_factsheet(pdf_text(b), url)
            add(unit, fy, v, prec, url, TODAY, f"{NOTE_2425} ({shown})", "nps_factsheet")
        # archived copies
        crow = cdx(f"fs_{unit}", url=url.replace("https://www.", ""), collapse="digest")
        for ts, o in distinct_captures(crow, "application/pdf"):
            fy, v, prec, shown = parse_factsheet(pdf_text(wb_get("factsheets", ts, o)), f"{ts} {o}")
            add(unit, fy, v, prec, wb_url(ts, o, raw=False), ts_date(ts), f"{NOTE_2425} ({shown})", "nps_factsheet")


# --------------------------------------------------------------------------- FY2025 DOI workbook
DOI_XLSX = "https://www.doi.gov/sites/default/files/documents/2026-07/gaoa-pmofy25-categorized-unit-level-dm-r.xlsx"
NOTE_25D = "FRPP portfolio as of 2025-09-30 (DOI unit-level workbook); parametric condition assessment"
_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
       "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def xlsx_sheet(b, sheet):
    z = zipfile.ZipFile(io.BytesIO(b))
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", _NS):
            ss.append("".join(t.text or "" for t in si.iter(f"{{{_NS['m']}}}t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rel = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    for s in wb.find("m:sheets", _NS):
        if s.get("name") != sheet:
            continue
        tgt = rel[s.get(f"{{{_NS['r']}}}id")].lstrip("/")
        tgt = tgt if tgt.startswith("xl/") else "xl/" + tgt
        out = []
        for row in ET.fromstring(z.read(tgt)).iter(f"{{{_NS['m']}}}row"):
            r = {}
            for c in row.findall("m:c", _NS):
                col = re.match(r"[A-Z]+", c.get("r")).group(0)
                v = c.find("m:v", _NS)
                r[col] = ss[int(v.text)] if c.get("t") == "s" and v is not None else (v.text if v is not None else None)
            out.append(r)
        return out
    raise SystemExit(f"sheet {sheet} not found")


def fetch_doi_fy2025():
    rows = xlsx_sheet(cached("doi/live_gaoa-pmofy25-categorized-unit-level-dm-r.xlsx", DOI_XLSX), "DM&R Table")
    if [rows[0].get(k) for k in "ABCD"] != ["State / Territory", "Bureau", "Installation Name", "Grand Total"]:
        raise SystemExit(f"DOI workbook header changed: {rows[0]}")
    by_name, nps_total, ak_total = {}, 0.0, 0.0
    seen = set()
    for r in rows[1:]:
        if r.get("B") != "NATIONAL PARK SERVICE":
            continue
        key = (r["A"], r["C"])
        if key in seen:
            raise SystemExit(f"DOI duplicate row {key}")
        seen.add(key)
        v = float(r["D"])
        by_name[norm(r["C"])] = by_name.get(norm(r["C"]), 0.0) + v
        nps_total += v
        ak_total += v if r["A"] == "ALASKA" else 0
    doi_checks.update(nps_total=nps_total, ak_total=ak_total)
    for unit in report_units():
        name = norm(unit_name(unit, DOI_NAME))
        if name not in by_name:
            raise SystemExit(f"DOI workbook: {unit_name(unit, DOI_NAME)} missing")
        add(unit, 2025, round(by_name[name]), 1, DOI_XLSX, TODAY, NOTE_25D, "doi_unit_xlsx")


# --------------------------------------------------------------------------- resolve and write
def within(a, b):
    """True if the two copies agree within the coarser copy's rounding."""
    tol = max(a["precision"], b["precision"]) / 2
    return abs(a["dollars"] - b["dollars"]) <= tol + 0.5


def resolve():
    groups = {}
    for r in records:
        groups.setdefault((r["unit"], r["fy"]), []).append(r)
    keep, diffs = {}, []
    for key, rs in sorted(groups.items()):
        rs.sort(key=lambda r: (r["captured"], -r["precision"]))
        best = rs[-1]
        keep[key] = best
        for r in rs[:-1]:
            if not within(r, best):
                diffs.append((key, r, best))
    return groups, keep, diffs


def expand(keep):
    rows = []
    for (unit, fy), r in keep.items():
        members = COMBINED.get(unit, [unit])
        for code in members:
            if code not in PARKS:
                raise SystemExit(f"unknown park {code}")
            notes = [r["note"]]
            if unit in COMBINED:
                notes.append(COMBINED_NOTE[unit])
            if code in PARK_AND_PRESERVE:
                notes.append(PP_NOTE)
            rows.append(dict(code=code, fy=fy, dmr_dollars=r["dollars"], locations="",
                             source_url=r["source_url"], captured=r["captured"], method_note="; ".join(notes)))
    rows.sort(key=lambda x: (x["code"], x["fy"]))
    keys = [(x["code"], x["fy"]) for x in rows]
    if len(keys) != len(set(keys)):
        raise SystemExit("duplicate (code, fy) in output")
    return rows


def write_overlap(groups, diffs):
    lines = ["# Deferred maintenance: overlapping copies", "",
             f"Written by `scripts/fetch/deferred_maintenance.py` on {TODAY}.", "",
             "Rule: when two copies give a value for the same unit and fiscal year, the build keeps the most",
             "recent copy (latest capture date; on a tie, the more precise copy). A rounded copy, such as a",
             "fact sheet that prints \"$138 M\", counts as a disagreement only when the other value falls",
             "outside its rounding range.", ""]
    lines += ["## Copies compared", "", "| Fiscal year | Source | Copies | Units |", "|---|---|---|---|"]
    summary = {}
    for (unit, fy), rs in groups.items():
        for r in rs:
            s = summary.setdefault((fy, r["source"]), [set(), set()])
            s[0].add((r["source_url"], r["captured"]))
            s[1].add(unit)
    for (fy, src), (copies, units) in sorted(summary.items()):
        lines.append(f"| {fy} | {src} | {len(copies)} | {len(units)} |")
    lines += ["", "## Differences", ""]
    if not diffs:
        lines.append("None. Every overlapping copy agrees within rounding.")
    else:
        lines += ["| Unit | FY | Dropped copy (captured) | Dropped value | Kept copy (captured) | Kept value | Difference |",
                  "|---|---|---|---|---|---|---|"]
        for (unit, fy), r, best in diffs:
            lines.append(f"| {unit} | {fy} | {r['source_url']} ({r['captured']}) | {r['dollars']:,} | "
                         f"{best['source_url']} ({best['captured']}) | {best['dollars']:,} | {best['dollars'] - r['dollars']:+,} |")
    lines += ["", "## Not written: FY2022 Quarter 1 snapshot", "",
              "The first version of the NPS park dataset (captured 2022-06-12) holds a Fiscal Year 2022 Quarter 1",
              "snapshot (national total $21.8 billion). It is not a fiscal-year-end figure, so it is not written to",
              "the processed file. Values for our units, for the record:", "",
              "| Unit | FY2022 Q1 snapshot | Source |", "|---|---|---|"]
    for unit, (v, ts, o) in sorted(q1_snapshot.items()):
        lines.append(f"| {unit} | {v:,} | {wb_url(ts, o, raw=False)} |")
    lines += ["", "## Total checks", "", "| Check | Parsed | Published |", "|---|---|---|"]
    for (fy, ts, o), (national, grand) in sorted(national_totals.items()):
        lines.append(f"| FY{fy} state-and-park PDF, sum of all rows ({ts}) | {grand:,} | {national if national is None else f'{national:,}'} (national total line) |")
    for ts, is_q1, total in doi_checks.get("dataset_sums", []):
        label = "FY2022 Q1 park dataset" if is_q1 else "FY2022 park dataset"
        pub = "$21.8 billion (NPS news release, May 9, 2022)" if is_q1 else "$22.288 billion (CRS R48136, NPS-wide FY2022)"
        lines.append(f"| {label}, sum of all rows ({ts}) | {total:,} | {pub} |")
    if "nps_total" in doi_checks:
        lines.append(f"| FY2025 DOI workbook, all NPS installations | {doi_checks['nps_total']:,.0f} | $24,237M (nps.gov regional table, grand total) |")
        lines.append(f"| FY2025 DOI workbook, NPS installations in Alaska | {doi_checks['ak_total']:,.0f} | $289M (AKR, nps.gov regional table) |")
    OVERLAP_MD.write_text("\n".join(lines) + "\n")


def main():
    fetch_state_park()
    fetch_fy2022()
    fetch_fy2023()
    fetch_factsheets()
    fetch_doi_fy2025()
    groups, keep, diffs = resolve()
    rows = expand(keep)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["code", "fy", "dmr_dollars", "locations", "source_url", "captured", "method_note"])
        w.writeheader()
        w.writerows(rows)
    write_overlap(groups, diffs)
    years = sorted({r["fy"] for r in rows})
    print(f"wrote {OUT} ({len(rows)} rows; fiscal years {years}); {len(diffs)} overlap differences")


if __name__ == "__main__":
    main()
