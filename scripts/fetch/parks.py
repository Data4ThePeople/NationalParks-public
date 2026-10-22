"""Build config/parks.json: the 63 national parks with unit code, name, state
and centroid, from the NPS Land Resources Division boundary centroids layer.

The layer types 62 units "National Park"; New River Gorge is typed "National
Preserve" because it is a park and preserve, so it is added by code.
"""
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
URL = ("https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/"
       "NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/0/query")
EXTRA = {"NERI"}
EXPECTED = 63

params = {"where": "UNIT_TYPE='National Park' OR UNIT_CODE IN ('NERI')",
          "outFields": "UNIT_CODE,UNIT_NAME,UNIT_TYPE,STATE",
          "returnGeometry": "true", "outSR": "4326", "f": "json"}
r = requests.get(URL, params=params, timeout=60)
r.raise_for_status()
raw = r.json()
(ROOT / "data/raw/nps_centroids.json").write_text(json.dumps(raw))

parks = {}
for f in raw["features"]:
    a = f["attributes"]
    code = a["UNIT_CODE"]
    if code in parks:
        raise SystemExit(f"duplicate unit code {code}")
    parks[code] = {"code": code, "name": a["UNIT_NAME"], "state": a["STATE"],
                   "lon": round(f["geometry"]["x"], 4), "lat": round(f["geometry"]["y"], 4)}
if len(parks) != EXPECTED or not EXTRA <= parks.keys():
    raise SystemExit(f"expected {EXPECTED} parks, got {len(parks)}")
out = ROOT / "config/parks.json"
out.write_text(json.dumps(sorted(parks.values(), key=lambda p: p["name"]), indent=1))
print(f"wrote {out} ({len(parks)} parks)")
