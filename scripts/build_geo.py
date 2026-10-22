"""Build screen-ready map geometry for the viz.

Inputs: Census cartographic boundary states (cb_2024_us_state_5m, public
domain), NPS Land Resources Division park boundaries (public domain), and
config/parks.json. Output: data/build/geo.json in a fixed 975 x 610 drawing
space, already projected, so the browser draws x/y as given.

Projection: Albers equal-area conic for the lower 48 (parallels 29.5 and 45.5),
Alaska (55, 65) and Hawaii (8, 18), each fitted into its own box, as in the
common "Albers USA" layout. American Samoa and the U.S. Virgin Islands are too
small for a conic and use an equirectangular inset with a cos(latitude) stretch.
Inset scales differ from the lower 48, which the page says in a note.
"""
import json
import math
import re
import sys
from pathlib import Path

import requests
import shapefile

ROOT = Path(__file__).resolve().parents[1]
SHP = ROOT / "data/raw/census/state5m/cb_2024_us_state_5m"
RAW_PARKS = ROOT / "data/raw/nps_boundaries.json"
OUT = ROOT / "data/build/geo.json"
W, H = 975, 610
TOL = 0.35  # simplification tolerance in drawing units

BOUNDARY_URL = ("https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/"
                "NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2/query")

# region: (projection, box x, y, w, h, label)
REGIONS = {
    "L48": (("albers", 29.5, 45.5, 37.5, -96.0), 0, 0, 975, 560, None),
    "AK": (("albers", 55.0, 65.0, 50.0, -154.0), 10, 465, 175, 135, "Alaska"),
    "HI": (("albers", 8.0, 18.0, 13.0, -157.0), 200, 510, 140, 90, "Hawaii"),
    "VI": (("equirect", 18.3),  865, 455, 100, 60, "U.S. Virgin Islands"),
    "AS": (("equirect", -14.25), 865, 535, 100, 60, "American Samoa"),
}
SKIP = {"GU", "MP", "PR"}
# only the islands near the parks, so the inset is not mostly ocean
INSET_CLIP = {"AS": (-171.2, -169.3, -14.45, -14.1), "VI": (-65.1, -64.55, 17.65, 18.45)}


def dp(points, tol):
    """Douglas-Peucker line simplification (iterative)."""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = points[a]
        bx, by = points[b]
        dx, dy = bx - ax, by - ay
        norm = (dx * dx + dy * dy) ** 0.5 or 1e-12
        best, idx = 0.0, None
        for i in range(a + 1, b):
            px, py = points[i]
            d = abs(dy * (px - ax) - dx * (py - ay)) / norm
            if d > best:
                best, idx = d, i
        if idx is not None and best > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(points, keep) if k]


def dp_ring(ring, tol):
    """Simplify a closed ring by splitting it in two, since its ends coincide."""
    h = len(ring) // 2
    return dp(ring[: h + 1], tol)[:-1] + dp(ring[h:], tol)


def project_raw(proj, lon, lat):
    if proj[0] == "equirect":
        return lon * math.cos(math.radians(proj[1])), -lat
    _, p1, p2, p0, l0 = proj
    p1, p2, p0 = map(math.radians, (p1, p2, p0))
    n = (math.sin(p1) + math.sin(p2)) / 2
    c = math.cos(p1) ** 2 + 2 * n * math.sin(p1)
    rho0 = math.sqrt(c - 2 * n * math.sin(p0)) / n
    if lon > 0:  # Aleutians west of 180
        lon -= 360
    rho = math.sqrt(c - 2 * n * math.sin(math.radians(lat))) / n
    th = n * math.radians(lon - l0)
    return rho * math.sin(th), -(rho0 - rho * math.cos(th))


def region_of(state):
    s = state.split(",")[0].strip()
    return s if s in ("AK", "HI", "VI", "AS") else "L48"


def inside_clip(region, ring):
    if region not in INSET_CLIP:
        return True
    x0, x1, y0, y1 = INSET_CLIP[region]
    return any(x0 <= lon <= x1 and y0 <= lat <= y1 for lon, lat in ring)


def load_states():
    out = {r: [] for r in REGIONS}
    rd = shapefile.Reader(str(SHP))
    for rec, shp in zip(rd.records(), rd.shapes()):
        st = rec["STUSPS"]
        if st in SKIP:
            continue
        reg = region_of(st)
        bounds = list(shp.parts) + [len(shp.points)]
        for a, b in zip(bounds, bounds[1:]):
            ring = shp.points[a:b]
            if inside_clip(reg, ring):
                out[reg].append((st, ring))
    return out


def load_boundaries(codes, refresh):
    if refresh or not RAW_PARKS.exists():
        feats = []
        codes = sorted(codes)
        for i in range(0, len(codes), 8):
            batch = ",".join(f"'{c}'" for c in codes[i:i + 8])
            r = requests.get(BOUNDARY_URL, params={
                "where": f"UNIT_CODE IN ({batch})", "outFields": "UNIT_CODE,STATE",
                "returnGeometry": "true", "outSR": "4326", "maxAllowableOffset": "0.005",
                "geometryPrecision": "4", "f": "json"}, timeout=120)
            r.raise_for_status()
            d = r.json()
            if "error" in d:
                raise SystemExit(f"boundary query failed: {d['error']}")
            feats += d["features"]
        RAW_PARKS.write_text(json.dumps(feats))
    rings, state = {}, {}
    for f in json.loads(RAW_PARKS.read_text()):
        a = f["attributes"]
        rings.setdefault(a["UNIT_CODE"], []).extend(f["geometry"]["rings"])
        if state.setdefault(a["UNIT_CODE"], a["STATE"]) != a["STATE"]:
            raise SystemExit(f"{a['UNIT_CODE']}: boundary parts disagree on state")
    return rings, state


def main():
    parks = json.loads((ROOT / "config/parks.json").read_text())
    states = load_states()
    bounds, park_state = load_boundaries([p["code"] for p in parks], "--refresh" in sys.argv)
    missing = {p["code"] for p in parks} - bounds.keys()
    if missing:
        raise SystemExit(f"no boundary for {sorted(missing)}")

    # fit each region's states into its box
    fit = {}
    for reg, (proj, bx, by, bw, bh, _) in REGIONS.items():
        pts = [project_raw(proj, *pt) for _, ring in states[reg] for pt in ring]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        k = min(bw / (max(xs) - min(xs)), bh / (max(ys) - min(ys)))
        ox = bx + (bw - k * (max(xs) - min(xs))) / 2 - k * min(xs)
        oy = by + (bh - k * (max(ys) - min(ys))) / 2 - k * min(ys)
        fit[reg] = (proj, k, ox, oy)

    def to_xy(reg, lon, lat):
        proj, k, ox, oy = fit[reg]
        x, y = project_raw(proj, lon, lat)
        return round(ox + k * x, 1), round(oy + k * y, 1)

    def ring_xy(reg, ring, tol=TOL):
        pts = dp_ring([to_xy(reg, *pt) for pt in ring], tol)
        return [c for p in pts for c in p] if len(pts) >= 3 else None

    out_states = []
    for reg in REGIONS:
        for st, ring in states[reg]:
            flat = ring_xy(reg, ring)
            if flat:
                out_states.append({"id": st, "ring": flat})

    out_parks = {}
    for p in parks:
        reg = region_of(p["state"])
        rings = [r for r in (ring_xy(reg, ring, TOL / 2) for ring in bounds[p["code"]]) if r]
        x, y = to_xy(reg, p["lon"], p["lat"])
        # NPS's own list, e.g. "ID-MT-WY"; strip footnote markers like "FL 6/" and spell out "SAMOA"
        sts = [{"SAMOA": "AS"}.get(s, s) for s in (re.sub(r"\s*\d+/$", "", x).strip() for x in park_state[p["code"]].split("-"))]
        if not all(re.fullmatch(r"[A-Z]{2}", s) for s in sts):
            raise SystemExit(f"{p['code']}: unexpected state field {park_state[p['code']]!r}")
        out_parks[p["code"]] = {"x": x, "y": y, "region": reg, "rings": rings, "states": sts}

    insets = [{"id": r, "label": v[5], "x": v[1], "y": v[2], "w": v[3], "h": v[4]}
              for r, v in REGIONS.items() if v[5]]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # the fitted projections, so scripts/relief.py can invert them pixel by pixel
    fits = {r: {"proj": list(f[0]), "k": f[1], "ox": f[2], "oy": f[3], "box": list(REGIONS[r][1:5])}
            for r, f in fit.items()}
    OUT.write_text(json.dumps({"w": W, "h": H, "states": out_states, "parks": out_parks,
                               "insets": insets, "fit": fits}, separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB, {len(out_states)} state rings, {len(out_parks)} parks)")


main()
