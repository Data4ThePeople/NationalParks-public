"""Shaded relief for the map, from the same source and blend as the RiverLevels map:
Natural Earth's 1:50m shaded relief (SR_50M, version 2.0.0, public domain), reprojected
into this map's drawing space and saved as viz/relief.jpg. The page draws it over the
land with a hard-light blend: mid-gray leaves the land as it is, darker shades it,
lighter lights it.

Each output pixel is traced back through the projection of the box it sits in (the
lower 48, or one of the Alaska, Hawaii, Virgin Islands and American Samoa insets),
using the fitted projections that scripts/build_geo.py writes into data/build/geo.json,
so the relief lines up with the state outlines exactly.

Source file: https://naciscdn.org/naturalearth/50m/raster/SR_50M.zip, unzipped into
data/raw/naturalearth_relief/ (the copy in the RiverLevels project).
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/raw/naturalearth_relief/SR_50M.tif"
GEO = ROOT / "data/build/geo.json"
OUT = ROOT / "viz/relief.jpg"
SCALE = 5  # output pixels per drawing unit (975 x 610 units)
CELLS = 30  # SR_50M: 1/30 degree cells, first cell centered at 179.983W, 89.983N


def inverse(proj, x, y):
    """Raw projected coordinates (y pointing down) back to lon, lat."""
    if proj[0] == "equirect":
        return x / np.cos(np.radians(proj[1])), -y
    _, p1, p2, p0, l0 = proj
    p1, p2, p0 = np.radians([p1, p2, p0])
    n = (np.sin(p1) + np.sin(p2)) / 2
    c = np.cos(p1) ** 2 + 2 * n * np.sin(p1)
    rho0 = np.sqrt(c - 2 * n * np.sin(p0)) / n
    yn = -y  # north-up
    rho = np.sqrt(x ** 2 + (rho0 - yn) ** 2)
    th = np.arctan2(x, rho0 - yn)
    lat = np.degrees(np.arcsin(np.clip((c - (rho * n) ** 2) / (2 * n), -1, 1)))
    lon = l0 + np.degrees(th / n)
    return lon, lat


def main():
    Image.MAX_IMAGE_PIXELS = None
    geo = json.loads(GEO.read_text())
    src = np.asarray(Image.open(SRC).convert("L"), dtype=np.float32)
    sh, sw = src.shape
    w, h = geo["w"] * SCALE, geo["h"] * SCALE
    ux = (np.arange(w) + 0.5) / SCALE
    uy = (np.arange(h) + 0.5) / SCALE
    UX, UY = np.meshgrid(ux, uy)
    lon = np.full(UX.shape, np.nan)
    lat = np.full(UX.shape, np.nan)
    # the lower 48 fills the frame; each inset box then takes its own pixels
    for region in ["L48"] + [r for r in geo["fit"] if r != "L48"]:
        f = geo["fit"][region]
        bx, by, bw, bh = f["box"]
        m = np.ones(UX.shape, bool) if region == "L48" else (UX >= bx) & (UX < bx + bw) & (UY >= by) & (UY < by + bh)
        rx, ry = (UX[m] - f["ox"]) / f["k"], (UY[m] - f["oy"]) / f["k"]
        lo, la = inverse(f["proj"], rx, ry)
        lon[m], lat[m] = lo, la
    lon = (lon + 180) % 360 - 180
    # bilinear between the four nearest source cells, so the relief has no stair-steps when zoomed in
    fx = (lon + 180) * CELLS - 0.5
    fy = (90 - lat) * CELLS - 0.5
    x0 = np.floor(fx).astype(int); y0 = np.floor(fy).astype(int)
    ax = fx - x0; ay = fy - y0
    x0c, x1c = np.clip(x0, 0, sw - 1), np.clip(x0 + 1, 0, sw - 1)
    y0c, y1c = np.clip(y0, 0, sh - 1), np.clip(y0 + 1, 0, sh - 1)
    out = ((1 - ay) * ((1 - ax) * src[y0c, x0c] + ax * src[y0c, x1c])
           + ay * ((1 - ax) * src[y1c, x0c] + ax * src[y1c, x1c]))
    flat = float(np.bincount(src.astype(np.uint8).ravel()).argmax())  # the tone of level ground
    # same tone curve as RiverLevels: 128 leaves the land as it is, darker shades it, lighter lights it
    d = out - flat
    g = 128 + np.where(d < 0, np.maximum(-85, 1.6 * d), np.minimum(90, 2.2 * d))
    Image.fromarray(np.round(g).astype(np.uint8), "L").save(OUT, quality=85, optimize=True, progressive=True)
    print(f"wrote {OUT.relative_to(ROOT)} {w}x{h}, {OUT.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
