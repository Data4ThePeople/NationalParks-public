"""Static charts for the national parks post, drawn from data/processed only.

House style follows the Data 4 The People dark charts (as in RiverLevels'
post_charts.py): surface #181A1B, ink #BBBDC0, the page's dark-mode blue for the
series. Every chart has a title and one published series.

Output goes to data/build/charts/ until the post's slug is set at step 2a, then
to posts/<slug>/images/ (pass --out).
"""
import argparse
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data/processed"

SURFACE, INK, INK_DIM, MUTED, GRID = "#181A1B", "#BBBDC0", "#8A9098", "#6B7178", "#2A2D2F"
LINE, SHADE = "#3987e5", "#232628"
CREDIT = "Built by Data 4 The People"

mpl.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK_DIM, "ytick.color": INK_DIM,
    "axes.edgecolor": GRID, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.grid": False, "axes.spines.top": False, "axes.spines.right": False,
    "font.family": "sans-serif", "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 11, "text.parse_math": False, "figure.dpi": 160, "savefig.dpi": 160,
})


def rnd(v, d=1):
    return Decimal(repr(float(v))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)


def titleblock(fig, title, subtitle, y=0.965):
    fig.text(0.03, y, title, color=INK, fontsize=17, fontweight="bold", va="top", ha="left")
    fig.text(0.03, y - 0.36 / fig.get_figheight(), subtitle, color=INK_DIM, fontsize=11, va="top", ha="left",
             linespacing=1.45)


def credit(fig, source):
    fig.text(0.03, 0.02, source, color=MUTED, fontsize=8.5, ha="left", va="bottom", linespacing=1.4)
    fig.text(0.97, 0.02, CREDIT, color=MUTED, fontsize=8.5, ha="right", va="bottom")


def grid_y(ax):
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.spines["left"].set_visible(False)


def real_budget(unit):
    """Park base budget in FY-latest dollars (CPI-U fiscal-year averages), as the page computes it."""
    bud = pd.read_csv(PROC / "budget.csv")
    cpi = pd.read_csv(PROC / "cpi.csv")
    cf = cpi[cpi.basis == "fiscal"].set_index("year").cpi
    base = int(cf.index.max())
    b = bud[bud.budget_unit == unit].set_index("fy").sort_index()
    return b.park_base_k * 1000 * cf[base] / cf.loc[b.index], base


def yellowstone_budget(out):
    s, base = real_budget("YELL")
    last, first = int(s.index.max()), int(s.index.min())
    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.78, bottom=0.14)
    titleblock(fig, "Yellowstone's base budget, after inflation",
               f"The park's base operating budget, FY{first} to FY{last}, in FY{base} dollars.\n"
               f"The Park Service has published no park-by-park budget table for any year after FY{last}.")
    ax.axvspan(last + 0.5, base + 0.5, color=SHADE, zorder=0)
    ax.text(base + 0.4, 6e6, f"No park-by-park\ntable after FY{last}", color=INK_DIM, fontsize=10,
            ha="right", va="bottom", linespacing=1.35)
    ax.plot(s.index, s.values, color=LINE, linewidth=2.4, solid_capstyle="round", zorder=3)
    # label only real data points: the comparison year and the last published year
    # set below and left of each point, where the line sits higher, so no label touches it
    for fy in (2012, last):
        v = s[fy]
        ax.scatter([fy], [v], s=36, color=LINE, zorder=4, edgecolor=SURFACE, linewidth=1.5)
        ax.text(fy - 0.1, v - 2.2e6, f"FY{fy}: ${rnd(v / 1e6)} million", color=INK, fontsize=10.5,
                ha="right", va="top")
    ax.set_xlim(first - 0.5, base + 0.5)
    ax.set_ylim(0, 60e6)
    ax.set_yticks(range(0, 60_000_001, 10_000_000))
    ax.set_yticklabels(["$0"] + [f"${v}M" for v in range(10, 61, 10)])
    ax.set_xticks(range(2008, base + 1, 2))
    ax.set_xticklabels([f"FY{y}" for y in range(2008, base + 1, 2)])
    grid_y(ax)
    credit(fig, f"Source: National Park Service budget justifications, FY2010 to FY2025 books; BLS CPI-U, "
                f"fiscal-year averages.\nInflation adjustment is our calculation.")
    out.mkdir(parents=True, exist_ok=True)
    path = out / "01-yellowstone-budget.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}: FY2012 ${rnd(s[2012] / 1e6)}M, FY{last} ${rnd(s[last] / 1e6)}M "
          f"({rnd((s[last] / s[2012] - 1) * 100, 0)}%)")


def visits(code):
    va = pd.read_csv(PROC / "visits_annual.csv")
    v = va[(va.code == code) & (va.months_reported == 12)].set_index("year").recreation_visits.sort_index()
    return v


def yellowstone_visits_budget(out):
    """Two stacked panels on shared years: one series each, each on its own zero-based scale."""
    b, base = real_budget("YELL")
    v = visits("YELL")
    last, first = int(b.index.max()), int(b.index.min())
    v = v[(v.index >= first) & (v.index <= base)]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8.2), sharex=True)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.80, bottom=0.11, hspace=0.42)
    titleblock(fig, "Yellowstone: more visits, a smaller budget",
               f"Recreation visits by calendar year, 2008 to {int(v.index.max())}, and the park's base operating budget\n"
               f"by fiscal year, FY{first} to FY{last}, in FY{base} dollars. Each panel has its own scale.")
    for ax in (ax1, ax2):
        grid_y(ax)
    ax2.axvspan(last + 0.5, base + 0.5, color=SHADE, zorder=0)  # only the budget stops; visits are published
    # top: visits
    ax1.plot(v.index, v.values, color=LINE, linewidth=2.4, solid_capstyle="round", zorder=3)
    ax1.set_ylim(0, 6e6)
    ax1.set_yticks(range(0, 6_000_001, 2_000_000))
    ax1.set_yticklabels(["0"] + [f"{m}M" for m in (2, 4, 6)])
    ax1.set_title("Recreation visits", loc="left", color=INK, fontsize=12, fontweight="bold", pad=8)
    for y in (2012, int(v.index.max())):
        val = v[y]
        ax1.scatter([y], [val], s=36, color=LINE, zorder=4, edgecolor=SURFACE, linewidth=1.5)
        ax1.text(y - 0.1, val + 0.35e6, f"{y}: {rnd(val / 1e6)} million", color=INK, fontsize=10.5,
                 ha="right", va="bottom")
    # bottom: budget
    ax2.plot(b.index, b.values, color=LINE, linewidth=2.4, solid_capstyle="round", zorder=3)
    ax2.set_ylim(0, 60e6)
    ax2.set_yticks(range(0, 60_000_001, 20_000_000))
    ax2.set_yticklabels(["$0"] + [f"${m}M" for m in (20, 40, 60)])
    ax2.set_title(f"Base budget, in FY{base} dollars", loc="left", color=INK, fontsize=12, fontweight="bold", pad=8)
    ax2.text(base + 0.4, 4e6, f"No park-by-park\ntable after FY{last}", color=INK_DIM, fontsize=10,
             ha="right", va="bottom", linespacing=1.35)
    for fy in (2012, last):
        val = b[fy]
        ax2.scatter([fy], [val], s=36, color=LINE, zorder=4, edgecolor=SURFACE, linewidth=1.5)
        ax2.text(fy - 0.1, val - 3.5e6, f"FY{fy}: ${rnd(val / 1e6)} million", color=INK, fontsize=10.5,
                 ha="right", va="top")
    ax2.set_xlim(first - 0.5, base + 0.5)
    ax2.set_xticks(range(2008, base + 1, 2))
    ax2.set_xticklabels([str(y) for y in range(2008, base + 1, 2)])
    credit(fig, "Source: NPS Visitor Use Statistics (IRMA); National Park Service budget justifications, FY2010 to "
                "FY2025 books;\nBLS CPI-U, fiscal-year averages. Inflation adjustment is our calculation. "
                "Fiscal years start Oct. 1.")
    path = out / "01-yellowstone-visits-budget.png"
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}: visits 2012 {v[2012]:,} -> {int(v.index.max())} {v.iloc[-1]:,} "
          f"({rnd((v.iloc[-1] / v[2012] - 1) * 100, 0)}%)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "posts/national-parks-data-gap/images")
    out = ap.parse_args().out
    yellowstone_budget(ROOT / "data/build/charts")  # kept, not used in the post
    yellowstone_visits_budget(out)
