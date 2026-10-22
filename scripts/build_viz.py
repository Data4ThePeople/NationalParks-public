"""Build dist/index.html from viz/template.html and the processed data.

Reads config/parks.json, config/designations.json, config/visit_method_changes.json,
config/budget_units.json, config/page.json and data/processed/*.csv (see
research/CONTRACT.md). Every number on the page is computed in the browser from
the series written here; nothing is precomputed except the joins.
"""
import base64
import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data/processed"
CFG = ROOT / "config"

PAGE_URL = "https://data4thepeople.github.io/NationalParks-public/"
POST_URL = "https://www.data4thepeople.com/p/national-parks-data-gap"
REPO_URL = "https://github.com/Data4ThePeople/NationalParks-public"

STATE_NAMES = {
    "AK": "Alaska", "AR": "Arkansas", "AS": "American Samoa", "AZ": "Arizona", "CA": "California",
    "CO": "Colorado", "FL": "Florida", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "KY": "Kentucky",
    "ME": "Maine", "MI": "Michigan", "MN": "Minnesota", "MO": "Missouri", "MT": "Montana", "NC": "North Carolina",
    "ND": "North Dakota", "NM": "New Mexico", "NV": "Nevada", "OH": "Ohio", "OR": "Oregon", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VA": "Virginia", "VI": "U.S. Virgin Islands",
    "WA": "Washington", "WV": "West Virginia", "WY": "Wyoming",
}


def short(name):
    if name == "National Park of American Samoa":
        return "American Samoa"
    return name.replace(" National Park and Preserve", "").replace(" National Park", "")


def series(df, key, col, start=None):
    """{y0, v:[...]} over a continuous year range, null where nothing was published."""
    s = df.set_index(key)[col].dropna()
    if s.empty:
        return None
    y0, y1 = int(s.index.min()), int(s.index.max())
    if start is not None:
        y0 = min(y0, start)
    vals = [None if y not in s.index else (int(s[y]) if float(s[y]).is_integer() else float(s[y]))
            for y in range(y0, y1 + 1)]
    return {"y0": y0, "v": vals}


AP_MONTHS = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]
VERB = {"established": "Established as {n}", "proclaimed": "Proclaimed {n}", "authorized": "Authorized as {n}",
        "redesignated": "Became {n}", "renamed": "Renamed {n}", "other": "Designated {n}"}
UNIT_TYPES = ["National Park", "National Monument", "National Recreation Area", "National Memorial Park",
              "National Memorial", "National Lakeshore", "National River", "National Preserve"]


def ap_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{AP_MONTHS[m - 1]} {d}, {y}"


def sig3(v):
    """Round to three significant figures, half away from zero, for 'about N acres'."""
    from decimal import Decimal, ROUND_HALF_UP
    q = Decimal(repr(float(v)))
    exp = q.adjusted() - 2
    return int(q.quantize(Decimal(1).scaleb(exp), rounding=ROUND_HALF_UP)) if exp >= 0 else int(
        q.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def history_text(h):
    """Two to five short sentences, each from one dated event in config/park_history.json, then the size.
    Boundary changes, transfers and leases are left out; a sentence names a unit only where the source does."""
    events = [e for e in h["events"] if e["kind"] in VERB and (e["kind"] != "other" or e["text"].lower().startswith("designated"))]
    # an authorization after the unit already exists is about something else (Gateway Arch's 1954 entry is the arch)
    events = [e for i, e in enumerate(events) if e["kind"] != "authorized" or i == 0]
    # once it is a national park, later monuments folded into it are not steps in its own history
    np_at = next((i for i, e in enumerate(events) if "National Park" in e["name"] and e.get("name_stated", True)
                  and e["kind"] in ("established", "redesignated", "renamed")), None)
    if np_at is not None:
        events = events[:np_at + 1] + [e for e in events[np_at + 1:] if e["kind"] in ("redesignated", "renamed", "established")]
    # two steps of the same kind under the same name (Great Smoky Mountains 1930 and 1934): keep the later one
    events = [e for i, e in enumerate(events)
              if not (i + 1 < len(events) and events[i + 1]["kind"] == e["kind"] and events[i + 1]["name"] == e["name"])]
    if len(events) > 4:
        events = events[:1] + events[-3:]
    out = []
    for e in events:
        date = ap_date(e["date"])
        if e.get("name_stated", True):
            out.append(VERB[e["kind"]].format(n=e["name"]) + f" on {date}.")
            continue
        unit = next((t for t in UNIT_TYPES if e["name"].endswith(t)), None)
        word = {"established": "Established", "proclaimed": "Proclaimed", "authorized": "Authorized",
                "redesignated": "Redesignated", "renamed": "Renamed", "other": "Designated"}[e["kind"]]
        if e["kind"] == "renamed" or unit is None:
            out.append(f"{word} on {date}.")
        else:
            article = "an" if unit[0] in "AEIOU" else "a"
            link = " " if e["kind"] == "proclaimed" else " as "  # "Proclaimed a national monument", "Established as a ..."
            out.append(f"{word}{link}{article} {unit.lower()} on {date}.")
    if h.get("acres_preserve"):
        out.append(f"The park covers about {sig3(h['acres']):,} acres, and the preserve about {sig3(h['acres_preserve']):,} acres.")
    elif h.get("acres"):
        out.append(f"Covers about {sig3(h['acres']):,} acres.")
    return " ".join(out)


def unique(df, cols, name):
    dup = df[df.duplicated(cols, keep=False)]
    if len(dup):
        raise SystemExit(f"{name}: duplicate keys\n{dup.head()}")


def json_ld(parks, page):
    author = {"@type": "Person", "name": "Eric Pachman", "url": "https://www.data4thepeople.com/authors/eric-pachman"}
    publisher = {"@type": "Organization", "name": "Data 4 The People", "url": "https://data4thepeople.com"}
    dataset = {
        "@type": "Dataset", "@id": PAGE_URL + "#dataset",
        "name": f"U.S. national parks over time: visits, base budget, staff and deferred maintenance for {len(parks)} parks",
        "description": page["jsonld_description"],
        "url": PAGE_URL, "sameAs": REPO_URL, "license": "https://www.data4thepeople.com/terms-of-use",
        "isAccessibleForFree": True, "creator": author, "publisher": publisher, "inLanguage": "en-US",
        "temporalCoverage": page["temporal"], "spatialCoverage": {"@type": "Place", "name": "United States national parks"},
        "variableMeasured": [{"@type": "PropertyValue", "name": v} for v in page["variables"]],
        "isBasedOn": [s["url"] for s in page["sources"]],
        "creditText": "Data 4 The People, from National Park Service and Department of the Interior records",
    }
    if POST_URL:
        dataset["subjectOf"] = {"@type": "WebPage", "url": POST_URL}
    app = {
        "@type": "WebApplication", "@id": PAGE_URL + "#tool", "name": "National Parks Over Time", "url": PAGE_URL,
        "applicationCategory": "ReferenceApplication", "operatingSystem": "Web browser",
        "browserRequirements": "Requires JavaScript", "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "about": {"@id": PAGE_URL + "#dataset"}, "creator": publisher,
        "description": "A free interactive map of the U.S. national parks. Click a park to see its visits, "
                       "base budget and staff by year.",
    }
    return json.dumps({"@context": "https://schema.org", "@graph": [dataset, app]},
                      ensure_ascii=False).replace("</", "<\\/")


def main():
    parks_cfg = json.loads((CFG / "parks.json").read_text())
    codes = {p["code"] for p in parks_cfg}
    desig = json.loads((CFG / "designations.json").read_text())
    methods = json.loads((CFG / "visit_method_changes.json").read_text())
    units = json.loads((CFG / "budget_units.json").read_text())
    page = json.loads((CFG / "page.json").read_text())
    hist = json.loads((CFG / "park_history.json").read_text())
    missing_hist = codes - hist.keys()
    if missing_hist:
        raise SystemExit(f"park_history.json has no entry for {sorted(missing_hist)}")
    geo = json.loads((ROOT / "data/build/geo.json").read_text())

    vm = pd.read_csv(PROC / "visits_monthly.csv")
    va = pd.read_csv(PROC / "visits_annual.csv")
    bud = pd.read_csv(PROC / "budget.csv")
    cpi = pd.read_csv(PROC / "cpi.csv")
    unique(vm, ["code", "year", "month"], "visits_monthly")
    unique(va, ["code", "year"], "visits_annual")
    unique(bud, ["budget_unit", "fy"], "budget")
    for name, df, col in (("visits", va, "code"), ("budget", bud, "budget_unit")):
        unknown = set(df[col]) - codes - set(units)
        if unknown:
            raise SystemExit(f"{name}: unknown units {sorted(unknown)}")

    # only full years count toward the annual series
    full = va[va.months_reported == 12]
    visits_last = int(full.year.max())
    member_of = {c: u for u, ms in units.items() for c in ms}
    budget_last = int(bud.fy.max())
    budget_first = int(page.get("budget_compare_from") or bud.fy.min())
    cpi_fy = cpi[cpi.basis == "fiscal"]
    cpi_base = int(cpi_fy.year.max())

    parks = []
    for p in parks_cfg:
        c = p["code"]
        v = full[full.code == c]
        unknown = {m["note"].split(":")[0] for m in methods.get(c, [])} - {"Overhaul", "Major", "Minor", "Non-material"}
        if unknown:
            raise SystemExit(f"{c}: unknown change rating {unknown}")
        bu = member_of.get(c, c)
        b = bud[bud.budget_unit == bu]
        members = units.get(bu, [c])
        budget = None
        if c in page.get("no_budget", {}):
            b = b.iloc[0:0]
        if len(b):
            budget = {"base_k": series(b, "fy", "park_base_k"), "park_base_fte": series(b, "fy", "park_base_fte"),
                      "total_fte": series(b, "fy", "total_fte")}
        states = geo["parks"][c]["states"]
        d = desig.get(c)
        parks.append({
            "code": c, "name": p["name"], "short": short(p["name"]),
            "state_names": ", ".join(STATE_NAMES.get(s, s) for s in states),
            "visits": series(v, "year", "recreation_visits"),
            # NPS rates each change Overhaul, Major, Minor or Non-material; Non-material rows are label
            # and wording updates, so they are not counted; Overhaul and Major changes are drawn on the chart
            "method_changes": [m | {"major": m["note"].split(":")[0] in ("Overhaul", "Major")}
                               for m in methods.get(c, []) if 1979 <= m["year"] <= visits_last
                               and m["note"].split(":")[0] != "Non-material"],
            # shown only when the visit record starts before the park was designated
            "designated": d if d and len(v) and d["year"] > int(v.year.min()) else None,
            "history": {"text": history_text(hist[c]),
                        "sources": sorted({e["source"] for e in hist[c]["events"]}), "acres_source": hist[c].get("acres_source")},
            "visit_note": page.get("visit_notes", {}).get(c),
            "park_report": page.get("park_reports", {}).get(c),  # newer figures the park posts itself
            "budget": budget, "budget_members": members,
            # per-visit math needs visits for every unit on the line, which we have only for the 63 parks
            "per_visit_ok": bool(budget) and set(members) <= codes,
            "budget_note": page.get("no_budget", {}).get(c) or page.get("shared_lines", {}).get(bu, ""),
        })

    payload = {
        "geo": geo, "parks": parks,
        "cpi": series(cpi_fy, "year", "cpi"), "cpi_base_fy": cpi_base,
        "compare": {"visits": [budget_first, visits_last], "budget": [budget_first, budget_last]},
        "series_start": int(bud.fy.min()),  # every time series opens at the first budget year
        "budget_last_fy": budget_last, "budget_axis_end": max(budget_last, cpi_base),
        "fte_key": page["fte_key"], "fte_label": page["fte_label"], "fte_desc": page["fte_desc"],
        "intro": page["intro"], "availability": page["availability"], "sources": page["sources"],
        "source_line": page["source_line"],
    }
    blob = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    html = (ROOT / "viz/template.html").read_text().replace("/*DATA*/", blob)
    for key, name in (("LOGO_DARK", "d4tp-text-dark.svg"), ("LOGO_LIGHT", "d4tp-text-light.svg")):
        svg = base64.b64encode((ROOT / "viz/logo" / name).read_bytes()).decode()
        html = html.replace(f"/*{key}*/", "data:image/svg+xml;base64," + svg)
    html = html.replace("/*JSONLD*/", json_ld(parks, page))
    out = ROOT / "dist/index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    shutil.copyfile(ROOT / "viz/relief.jpg", out.parent / "relief.jpg")
    nb = sum(1 for p in parks if p["budget"])
    print(f"wrote {out}: {out.stat().st_size / 1e3:.0f} KB, {len(parks)} parks, {nb} with budget;"
          f" visits through {visits_last}, budget FY{budget_first}-FY{budget_last}, dollars in FY{cpi_base}")


main()
