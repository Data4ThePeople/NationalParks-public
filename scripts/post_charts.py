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


def tick_label(v, unit, prefix=""):
    """'1.2M', '600K', '$7M': one decimal only when it is needed."""
    if v == 0:
        return prefix + "0"
    if v >= 1e6:
        x = rnd(v / 1e6, 1)
        return f"{prefix}{x.normalize() if x == x.to_integral() else x}M".replace("E+0", "")
    return f"{prefix}{rnd(v / 1e3, 0)}K"


def visits_budget(out, code, name, fname, vmax=6e6, bmax=60e6, vbelow=()):
    """Two stacked panels on shared years: one series each, each on its own zero-based scale."""
    import json
    b, base = real_budget(code)
    v = visits(code)
    majors = [m["year"] for m in json.loads((ROOT / "config/visit_method_changes.json").read_text()).get(code, [])
              if m["note"].startswith(("Major", "Overhaul")) and 2008 <= m["year"] <= int(v.index.max())]
    last, first = int(b.index.max()), int(b.index.min())
    v = v[(v.index >= first) & (v.index <= base)]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8.2), sharex=True)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.80, bottom=0.11, hspace=0.42)
    titleblock(fig, f"{name}: more visits, a smaller budget",
               f"Recreation visits by calendar year, 2008 to {int(v.index.max())}, and the park's base operating budget\n"
               f"by fiscal year, FY{first} to FY{last}, in FY{base} dollars. Each panel has its own scale.")
    for ax in (ax1, ax2):
        grid_y(ax)
    ax2.axvspan(last + 0.5, base + 0.5, color=SHADE, zorder=0)  # only the budget stops; visits are published
    # top: visits
    for y in majors:  # the park changed how it counts visits that year, as the tool marks it
        ax1.axvline(y, color=MUTED, linewidth=1, linestyle=(0, (3, 3)), zorder=2)
        ax1.text(y + 0.15, vmax * 0.06, f"{y}: counting\nmethod changed", color=INK_DIM, fontsize=9, va="bottom",
                 linespacing=1.3)
    ax1.plot(v.index, v.values, color=LINE, linewidth=2.4, solid_capstyle="round", zorder=3)
    ax1.set_ylim(0, vmax)
    step = vmax / 3
    ax1.set_yticks([step * i for i in range(4)])
    ax1.set_yticklabels([tick_label(step * i, "") for i in range(4)])
    ax1.set_title("Recreation visits", loc="left", color=INK, fontsize=12, fontweight="bold", pad=8)
    for y in (2012, int(v.index.max())):
        val = v[y]
        ax1.scatter([y], [val], s=36, color=LINE, zorder=4, edgecolor=SURFACE, linewidth=1.5)
        below = y in vbelow  # put the label on the side away from the line
        ax1.text(y - 0.1, val - vmax * 0.06 if below else val + vmax * 0.06, f"{y}: {rnd(val / 1e6)} million",
                 color=INK, fontsize=10.5, ha="right", va="top" if below else "bottom")
    # bottom: budget
    ax2.plot(b.index, b.values, color=LINE, linewidth=2.4, solid_capstyle="round", zorder=3)
    ax2.set_ylim(0, bmax)
    bs = bmax / 3
    ax2.set_yticks([bs * i for i in range(4)])
    ax2.set_yticklabels([tick_label(bs * i, "", "$") for i in range(4)])
    ax2.set_title(f"Base budget, in FY{base} dollars", loc="left", color=INK, fontsize=12, fontweight="bold", pad=8)
    ax2.text(base + 0.4, bmax * 0.07, f"No park-by-park\ntable after FY{last}", color=INK_DIM, fontsize=10,
             ha="right", va="bottom", linespacing=1.35)
    for fy in (2012, last):
        val = b[fy]
        ax2.scatter([fy], [val], s=36, color=LINE, zorder=4, edgecolor=SURFACE, linewidth=1.5)
        ax2.text(fy - 0.1, val - bmax * 0.06, f"FY{fy}: ${rnd(val / 1e6)} million", color=INK, fontsize=10.5,
                 ha="right", va="top")
    ax2.set_xlim(first - 0.5, base + 0.5)
    ax2.set_xticks(range(2008, base + 1, 2))
    ax2.set_xticklabels([str(y) for y in range(2008, base + 1, 2)])
    credit(fig, "Source: NPS Visitor Use Statistics (IRMA); National Park Service budget justifications, FY2010 to "
                "FY2025 books;\nBLS CPI-U, fiscal-year averages. Inflation adjustment is our calculation. "
                "Fiscal years start Oct. 1.")
    path = out / fname
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}: visits 2012 {v[2012]:,} -> {int(v.index.max())} {v.iloc[-1]:,} "
          f"({rnd((v.iloc[-1] / v[2012] - 1) * 100, 0)}%)")


def per_visit(out, code, name, fname, ymax, step=1, above=()):
    """Base budget per recreation visit (our calculation), FY2008 to FY2023, in FY-latest dollars."""
    b, base = real_budget(code)
    v = visits(code)
    q = (b / v.reindex(b.index)).dropna()
    first, last = int(q.index.min()), int(q.index.max())
    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.78, bottom=0.14)
    titleblock(fig, f"{name}: base budget per visit",
               f"The park's base budget for each fiscal year divided by its recreation visits that calendar year, "
               f"FY{first} to FY{last},\nin FY{base} dollars. Our calculation.")
    ax.axvspan(last + 0.5, base + 0.5, color=SHADE, zorder=0)
    ax.text(base + 0.4, ymax * 0.07, f"No park-by-park\ntable after FY{last}", color=INK_DIM, fontsize=10,
            ha="right", va="bottom", linespacing=1.35)
    ax.plot(q.index, q.values, color=LINE, linewidth=2.4, solid_capstyle="round", zorder=3)
    for fy in (2012, last):
        val = q[fy]
        ax.scatter([fy], [val], s=36, color=LINE, zorder=4, edgecolor=SURFACE, linewidth=1.5)
        up = fy in above  # the side away from the line
        ax.text(fy - 0.1, val + ymax * 0.05 if up else val - ymax * 0.05, f"FY{fy}: ${rnd(val, 2)}", color=INK,
                fontsize=10.5, ha="right", va="bottom" if up else "top")
    ax.set_xlim(first - 0.5, base + 0.5)
    ax.set_ylim(0, ymax)
    ax.set_yticks(range(0, int(ymax) + 1, step))  # whole-dollar ticks, so every label is exact
    ax.set_yticklabels([f"${v}" for v in range(0, int(ymax) + 1, step)])
    ax.set_xticks(range(2008, base + 1, 2))
    ax.set_xticklabels([f"FY{y}" for y in range(2008, base + 1, 2)])
    grid_y(ax)
    credit(fig, "Source: NPS Visitor Use Statistics (IRMA); National Park Service budget justifications, FY2010 to "
                "FY2025 books; BLS CPI-U,\nfiscal-year averages. Inflation adjustment and the per-visit figure are our "
                "calculation. Fiscal years start Oct. 1.")
    path = out / fname
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}: FY2012 ${rnd(q[2012], 2)}, FY{last} ${rnd(q[last], 2)} ({rnd((q[last] / q[2012] - 1) * 100, 0)}%)")


def staff_per_visits(out):
    """Total FTE per 100,000 recreation visits, summed over the budget lines whose parks we have visits for
    (each park's own line plus Sequoia and Kings Canyon; Katmai's and North Cascades' lines also fund other units)."""
    import json
    cfg = ROOT / "config"
    page = json.loads((cfg / "page.json").read_text())
    parks = [p["code"] for p in json.loads((cfg / "parks.json").read_text())]
    units = json.loads((cfg / "budget_units.json").read_text())
    lines = [u for u in budget_lines(parks, page.get("no_budget", {}), units) if set(units.get(u, [u])) <= set(parks)]
    members = [c for u in lines for c in units.get(u, [u])]
    bud = pd.read_csv(PROC / "budget.csv")
    b = bud[bud.budget_unit.isin(lines)]
    if b.groupby("fy").budget_unit.nunique().min() != len(lines):
        raise SystemExit("a budget line is missing a year")
    va = pd.read_csv(PROC / "visits_annual.csv")
    va = va[(va.months_reported == 12) & va.code.isin(members)]
    if va.groupby("year").code.nunique().loc[2008:2023].min() != len(members):
        raise SystemExit("a park is missing visits in a year")
    r = b.groupby("fy").total_fte.sum() / va.groupby("year").recreation_visits.sum() * 1e5
    r = r.dropna()
    first, last = int(r.index.min()), int(r.index.max())
    y0 = int(page["budget_compare_from"])
    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.78, bottom=0.14)
    titleblock(fig, "Staff per 100,000 visits",
               f"Total full-time equivalent staff for each fiscal year per 100,000 recreation visits that calendar "
               f"year, across\n{len(lines)} budget lines ({len(members)} parks), FY{first} to FY{last}. Our calculation.")
    ax.axvspan(last + 0.5, 2025.5, color=SHADE, zorder=0)
    ax.text(2025.4, 0.9, f"No park-by-park\ntable after FY{last}", color=INK_DIM, fontsize=10, ha="right",
            va="bottom", linespacing=1.35)
    ax.plot(r.index, r.values, color=LINE, linewidth=2.4, solid_capstyle="round", zorder=3)
    for fy in (y0, last):
        v = r[fy]
        ax.scatter([fy], [v], s=36, color=LINE, zorder=4, edgecolor=SURFACE, linewidth=1.5)
        ax.text(fy - 0.1, v - 0.6, f"FY{fy}: {rnd(v, 1)}", color=INK, fontsize=10.5, ha="right", va="top")
    ax.set_xlim(first - 0.5, 2025.5)
    ax.set_ylim(0, 12)
    ax.set_yticks(range(0, 13, 3))
    ax.set_xticks(range(2008, 2026, 2))
    ax.set_xticklabels([f"FY{y}" for y in range(2008, 2026, 2)])
    grid_y(ax)
    credit(fig, "Sources: NPS Visitor Use Statistics (IRMA); National Park Service budget justifications, FY2010 to "
                "FY2025 books.\nLeaves out Kobuk Valley and the Katmai and North Cascades lines, which also fund "
                "other park units. Fiscal years start Oct. 1.")
    path = out / "05-staff-per-visits.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}: FY{y0} {rnd(r[y0], 2)}, FY{last} {rnd(r[last], 2)} ({rnd((r[last] / r[y0] - 1) * 100, 0)}%)")


# what each of the six parks' own pages show today, from research/availability/budget_elsewhere.md and its figures file;
# numbers shown are read from the figures file, the wording follows the park pages
PARK_PAGES = [
    ("Grand Canyon", "FY2025 only. Its FY2024 figure was\nreplaced; we found it in the Internet Archive.",
     "FY2021 to FY2025, counted the same way", "Yes, for staff"),
    ("Yellowstone", "FY2024 only", "2024 only (summer)", "No"),
    ("Great Smoky Mountains", "FY2024 only", "No year given", "No"),
    ("Yosemite", "2025 only. Its 2024 figure was\nreplaced; we found it in the Internet Archive.",
     "2025 only (summer and winter). Its 2024\ncounts were replaced; we found them in\nthe Internet Archive.", "Only with the\narchived copy"),
    ("Glacier Bay", "FY2024 only", "No year given", "No"),
    ("Kenai Fjords", "FY2025 only", "No year given", "No"),
]


def park_reports_table(out):
    """What the six parks that post newer figures show on their own pages today, and whether any two years compare."""
    import re
    f = pd.read_csv(ROOT / "research/availability/budget_elsewhere_figures.csv")
    f = f[f.source_type == "official"]

    def fill(text):
        def one(m):
            code, year, measure = m.group(1).split("|")
            hit = f[(f.code == code) & (f.fiscal_year == year) & (f.measure == measure)]
            if len(hit) != 1:
                raise SystemExit(f"{m.group(1)}: {len(hit)} rows in the figures file")
            return f"{int(hit.value.iloc[0]):,}"
        return re.sub(r"\{([^}]+)\}", one, text)

    rows = [(n, fill(b), fill(st), c) for n, b, st, c in PARK_PAGES]
    fig = plt.figure(figsize=(10, 9.2))
    titleblock(fig, "Even the parks that post newer numbers are spotty",
               "What the six parks with budget or staff figures after FY2023 show on their own pages today. Each uses "
               "its own\nyears, measures and seasons, so the parks cannot be compared with each other.", y=0.975)
    top, rowh = 0.82, 0.118
    xs = (0.03, 0.25, 0.53, 0.83)
    for x, h in zip(xs, ("Park", "Budget years shown", "Staff years shown", "Two years to\ncompare?")):
        fig.text(x, top + 0.012, h, color=INK_DIM, fontsize=10.5, fontweight="bold", va="bottom", linespacing=1.3)
    fig.add_artist(plt.Line2D([0.03, 0.97], [top + 0.006] * 2, color=GRID, linewidth=1, transform=fig.transFigure))
    for k, (name, b, st, c) in enumerate(rows):
        y = top - k * rowh - 0.014
        fig.text(xs[0], y, name, color=INK, fontsize=11.5, fontweight="bold", va="top", wrap=True)
        fig.text(xs[1], y, b, color=INK, fontsize=10, va="top", linespacing=1.35)
        fig.text(xs[2], y, st, color=INK, fontsize=10, va="top", linespacing=1.35)
        fig.text(xs[3], y, c, color=LINE if c.startswith("Yes") else INK_DIM, fontsize=10.5,
                 fontweight="bold" if c.startswith("Yes") else "normal", va="top", linespacing=1.35)
        fig.add_artist(plt.Line2D([0.03, 0.97], [top - (k + 1) * rowh + 0.004] * 2, color=GRID, linewidth=0.6,
                                  transform=fig.transFigure))
    credit(fig, "Sources: each park's page on nps.gov, checked Oct. 22, 2026 (Kenai Fjords: its 2026 fact sheet); "
                "archived copies from the Internet Archive.\nThe 57 other national parks post no dated budget or staff "
                "figures for FY2024 or later that we could find.")
    path = out / "06-park-reported-figures.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}")
    for r_ in rows:
        print("  ", " | ".join(x.replace("\n", " ") for x in r_))


def budget_lines(page_codes, no_budget, units):
    """The 61 budget lines the post counts, with short labels."""
    member_of = {c: u for u, ms in units.items() for c in ms}
    return sorted({member_of.get(c, c) for c in page_codes if c not in no_budget})


LINE_LABEL = {"SEKI": "Sequoia and Kings Canyon", "KATM_ANIA_ALAG": "Katmai line", "NOCA_LACH_ROLA": "North Cascades line"}


def short_name(name):
    if name == "National Park of American Samoa":
        return "American Samoa"
    return name.replace(" National Park and Preserve", "").replace(" National Park", "")


def budget_change_by_line(out):
    """One bar per budget line: change in real base budget, FY2012 to FY2023. Declines point left."""
    import json
    cfg = ROOT / "config"
    page = json.loads((cfg / "page.json").read_text())
    parks = json.loads((cfg / "parks.json").read_text())
    units = json.loads((cfg / "budget_units.json").read_text())
    names = {p["code"]: short_name(p["name"]) for p in parks}
    lines = budget_lines([p["code"] for p in parks], page.get("no_budget", {}), units)
    y0 = int(page["budget_compare_from"])
    chg = {}
    for u in lines:
        s, base = real_budget(u)
        chg[u] = (s[int(s.index.max())] / s[y0] - 1) * 100
        last = int(s.index.max())
    order = sorted(chg, key=lambda u: chg[u])
    fig, ax = plt.subplots(figsize=(10, 15.5))
    fig.subplots_adjust(left=0.30, right=0.93, top=0.895, bottom=0.075)
    down = sum(1 for v in chg.values() if v < 0)
    titleblock(fig, f"Base budgets fell after inflation on {down} of {len(chg)} lines",
               f"Change in each park's base budget, FY{y0} to FY{last}, after adjusting for inflation.\n"
               "Sequoia and Kings Canyon share one budget line. Katmai's and North Cascades' lines also fund nearby units.",
               y=0.985)
    ys = range(len(order))
    vals = [chg[u] for u in order]
    # red gradient by size of the decline (deeper red = bigger drop); the one gain stays blue
    from matplotlib.colors import LinearSegmentedColormap
    reds = LinearSegmentedColormap.from_list("decline", ["#f2b8b5", "#e66767", "#b3261e"])
    worst = -25.0  # color scale tops out at a 25% drop, so the shades spread across where most parks fall
    colors = [LINE if v > 0 else reds(min(1.0, v / worst)) for v in vals]
    ax.barh(list(ys), vals, height=0.68, color=colors, zorder=3)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([LINE_LABEL.get(u, names.get(u, u)) for u in order], fontsize=9.5)
    ax.invert_yaxis()
    ax.axvline(0, color=INK_DIM, linewidth=0.8, zorder=4)
    for y, v in zip(ys, vals):
        r0 = rnd(v, 0)  # a change that rounds to zero carries no sign, as on the page
        ax.text(v - 0.6 if v < 0 else v + 0.6, y, f"{'−' if r0 < 0 else '+' if r0 > 0 else ''}{abs(r0)}%", va="center",
                ha="right" if v < 0 else "left", fontsize=8.5, color=INK_DIM)
    ax.set_xlim(-45, 10)
    ax.set_xticks(range(-40, 11, 10))
    ax.set_xticklabels([f"{'−' if x < 0 else '+' if x > 0 else ''}{abs(x)}%" for x in range(-40, 11, 10)])
    ax.xaxis.set_ticks_position("top")  # axis labels at the top, away from the source line
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    credit(fig, "Source: National Park Service budget justifications, FY2014 and FY2025 books; BLS CPI-U, "
                "fiscal-year averages.\nInflation adjustment is our calculation. Kobuk Valley is left out because its "
                "shared line changed in FY2020.")
    path = out / "03-budget-change-by-line.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}: {down} of {len(chg)} down; median {rnd(sorted(vals)[len(vals) // 2], 0)}%")


def staff_total(out):
    """Total FTE summed over the 61 lines (an editorial sum), FY2008 to FY2023."""
    import json
    cfg = ROOT / "config"
    page = json.loads((cfg / "page.json").read_text())
    parks = json.loads((cfg / "parks.json").read_text())
    units = json.loads((cfg / "budget_units.json").read_text())
    lines = budget_lines([p["code"] for p in parks], page.get("no_budget", {}), units)
    bud = pd.read_csv(PROC / "budget.csv")
    b = bud[bud.budget_unit.isin(lines)]
    if b.groupby("fy").budget_unit.nunique().min() != len(lines):
        raise SystemExit("a budget line is missing a year")
    tot = b.groupby("fy").total_fte.sum()
    first, last = int(tot.index.min()), int(tot.index.max())
    y0 = int(page["budget_compare_from"])
    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.78, bottom=0.14)
    titleblock(fig, "Staff at the national parks, FY2008 to FY2023",
               f"Total full-time equivalent staff across {len(lines)} budget lines, by fiscal year. Our sum of the "
               "park figures.\nThe Park Service has published no park-by-park staff table for any year after FY2023.")
    ax.axvspan(last + 0.5, 2025.5, color=SHADE, zorder=0)
    ax.text(2025.4, 600, f"No park-by-park\ntable after FY{last}", color=INK_DIM, fontsize=10, ha="right",
            va="bottom", linespacing=1.35)
    ax.plot(tot.index, tot.values, color=LINE, linewidth=2.4, solid_capstyle="round", zorder=3)
    for fy in (y0, last):
        v = tot[fy]
        ax.scatter([fy], [v], s=36, color=LINE, zorder=4, edgecolor=SURFACE, linewidth=1.5)
        ax.text(fy - 0.1, v - 350, f"FY{fy}: {int(v):,}", color=INK, fontsize=10.5, ha="right", va="top")
    ax.set_xlim(first - 0.5, 2025.5)
    ax.set_ylim(0, 9000)
    ax.set_yticks(range(0, 9001, 3000))
    ax.set_yticklabels([f"{v:,}" for v in range(0, 9001, 3000)])
    ax.set_xticks(range(2008, 2026, 2))
    ax.set_xticklabels([f"FY{y}" for y in range(2008, 2026, 2)])
    grid_y(ax)
    credit(fig, "Source: National Park Service budget justifications, FY2010 to FY2025 books. "
                "Kobuk Valley is left out; Sequoia and Kings Canyon share one line.")
    path = out / "04-staff-total.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}: FY{y0} {int(tot[y0]):,}, FY{last} {int(tot[last]):,} ({rnd((tot[last] / tot[y0] - 1) * 100, 0)}%)")


def budget_total_nominal_real(out):
    """Total base budget over the 61 lines, as published and in FY-latest dollars, FY2008 to FY2023."""
    import json
    cfg = ROOT / "config"
    page = json.loads((cfg / "page.json").read_text())
    parks = json.loads((cfg / "parks.json").read_text())
    units = json.loads((cfg / "budget_units.json").read_text())
    lines = budget_lines([p["code"] for p in parks], page.get("no_budget", {}), units)
    bud = pd.read_csv(PROC / "budget.csv")
    b = bud[bud.budget_unit.isin(lines)].copy()
    if b.groupby("fy").budget_unit.nunique().min() != len(lines):
        raise SystemExit("a budget line is missing a year")
    cpi = pd.read_csv(PROC / "cpi.csv")
    cf = cpi[cpi.basis == "fiscal"].set_index("year").cpi
    base = int(cf.index.max())
    b["nominal"] = b.park_base_k * 1000
    b["real"] = b.nominal * cf[base] / b.fy.map(cf)
    nom, real = b.groupby("fy").nominal.sum(), b.groupby("fy").real.sum()
    first, last = int(nom.index.min()), int(nom.index.max())
    y0 = int(page["budget_compare_from"])
    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.78, bottom=0.14)
    titleblock(fig, "More dollars, less buying power",
               f"Total base budget across {len(lines)} budget lines, FY{first} to FY{last}: as published, and "
               f"adjusted for inflation to FY{base} dollars.")
    ax.axvspan(last + 0.5, 2025.5, color=SHADE, zorder=0)
    ax.text(2025.4, 30e6, f"No park-by-park\ntable after FY{last}", color=INK_DIM, fontsize=10, ha="right",
            va="bottom", linespacing=1.35)
    ax.plot(nom.index, nom.values, color=INK_DIM, linewidth=2.4, solid_capstyle="round", zorder=3)
    ax.plot(real.index, real.values, color=LINE, linewidth=2.4, solid_capstyle="round", zorder=3)
    for s, color, dy, va in ((real, LINE, 25e6, "bottom"), (nom, INK_DIM, -25e6, "top")):
        for fy in (y0, last):
            ax.scatter([fy], [s[fy]], s=36, color=color, zorder=4, edgecolor=SURFACE, linewidth=1.5)
            ax.text(fy, s[fy] + dy, f"${rnd(s[fy] / 1e6, 0)}M", color=INK, fontsize=10.5, ha="center", va=va)
    ax.text(2016, real[2016] + 30e6, f"Adjusted for inflation (FY{base} dollars)", color=LINE, fontsize=10.5,
            fontweight="bold", ha="center", va="bottom")
    ax.text(2016, nom[2016] - 30e6, "As published", color=INK_DIM, fontsize=10.5, fontweight="bold", ha="center",
            va="top")
    ax.set_xlim(first - 0.5, 2025.5)
    ax.set_ylim(0, 800e6)
    ax.set_yticks(range(0, 800_000_001, 200_000_000))
    ax.set_yticklabels([f"${v // 1_000_000}M" for v in range(0, 800_000_001, 200_000_000)])
    ax.set_xticks(range(2008, 2026, 2))
    ax.set_xticklabels([f"FY{y}" for y in range(2008, 2026, 2)])
    grid_y(ax)
    credit(fig, "Sources: National Park Service budget justifications, FY2010 to FY2025 books; BLS CPI-U, fiscal-year "
                "averages.\nInflation adjustment is our calculation. Kobuk Valley is left out; Sequoia and Kings "
                "Canyon share one line.")
    path = out / "03a-budget-total-nominal-real.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}: nominal FY{y0} {rnd(nom[y0] / 1e6, 0)}M -> FY{last} {rnd(nom[last] / 1e6, 0)}M "
          f"({rnd((nom[last] / nom[y0] - 1) * 100, 0)}%); real {rnd(real[y0] / 1e6, 0)}M -> {rnd(real[last] / 1e6, 0)}M "
          f"({rnd((real[last] / real[y0] - 1) * 100, 0)}%)")


def staff_by_job(out):
    """Park Service people on board in September 2025 by job group (OPM Federal Workforce Data)."""
    j = pd.read_csv(PROC / "nps_staff_by_job.csv", dtype={"snapshot": str})
    j = j[j.snapshot == "202509"].set_index("job_group").people
    other = j.pop("Other")
    j = j.sort_values(ascending=False)
    total = int(j.sum() + other)
    fig, ax = plt.subplots(figsize=(10, 6.8))
    fig.subplots_adjust(left=0.34, right=0.95, top=0.80, bottom=0.13)
    titleblock(fig, "Who works for the Park Service",
               f"People on board on Sept. 30, 2025, by kind of job: {total:,} in all, including seasonal staff. "
               "Headcounts, not\nfull-time equivalents. Agency-wide, not only the 63 national parks. Groups are our "
               "own, built from OPM job codes.")
    ys = range(len(j))
    ax.barh(list(ys), j.values, height=0.68, color=LINE, zorder=3)
    ax.set_yticks(list(ys))
    ax.set_yticklabels(j.index, fontsize=10.5)
    ax.invert_yaxis()
    for y, v in zip(ys, j.values):
        ax.text(v + 60, y, f"{int(v):,} ({rnd(v / total * 100, 0)}%)", va="center", ha="left", fontsize=9.5,
                color=INK_DIM)
    ax.set_xlim(0, 6500)
    ax.set_xticks(range(0, 6001, 2000))
    ax.set_xticklabels([f"{v:,}" for v in range(0, 6001, 2000)])
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.spines["left"].set_visible(False)
    credit(fig, f"Source: U.S. Office of Personnel Management, Federal Workforce Data, September 2025 employment file. "
                f"Our grouping of\nOPM occupational series. Not shown: {int(other):,} people in other jobs.")
    path = out / "05a-staff-by-job.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}: total {total:,}; " + "; ".join(f"{k} {int(v):,}" for k, v in j.items()))


MIN_JOB_GROUP = 500  # job groups shown in the job charts: at least this many people in Sept. 2012


def staff_by_job_change(out, a="201209", b="202309"):
    """Change in Park Service people on board by job group, September 2012 to September 2023 (OPM)."""
    from matplotlib.colors import LinearSegmentedColormap
    j = pd.read_csv(PROC / "nps_staff_by_job.csv", dtype={"snapshot": str})
    p = j.pivot(index="job_group", columns="snapshot", values="people")
    tot_a, tot_b = p[a].sum(), p[b].sum()
    p = p.drop(index="Other")
    p = p[p[a] >= MIN_JOB_GROUP]  # small groups swing on a handful of hires
    chg = ((p[b] / p[a] - 1) * 100).sort_values()
    fig, ax = plt.subplots(figsize=(10, 6.8))
    fig.subplots_adjust(left=0.34, right=0.95, top=0.80, bottom=0.16)
    titleblock(fig, "Every major kind of Park Service job shrank",
               f"Change in people on board by kind of job, Sept. 30, {a[:4]}, to Sept. 30, {b[:4]}, the last year of "
               f"the park budget table.\nAll staff: {int(tot_a):,} to {int(tot_b):,} "
               f"({'−' if tot_b < tot_a else '+'}{abs(rnd((tot_b / tot_a - 1) * 100, 0))}%). Headcounts, including "
               "seasonal staff. Agency-wide, not only the 63 national parks.")
    reds = LinearSegmentedColormap.from_list("decline", ["#f2b8b5", "#e66767", "#b3261e"])
    ys = range(len(chg))
    vals = list(chg.values)
    ax.barh(list(ys), vals, height=0.68, color=[LINE if v > 0 else reds(min(1.0, v / -25.0)) for v in vals], zorder=3)
    ax.set_yticks(list(ys))
    ax.set_yticklabels(chg.index, fontsize=10.5)
    ax.invert_yaxis()
    ax.axvline(0, color=INK_DIM, linewidth=0.8, zorder=4)
    for y, g in zip(ys, chg.index):
        v, r0 = chg[g], rnd(chg[g], 0)
        label = f"{'−' if r0 < 0 else '+'}{abs(r0)}%  ({int(p.loc[g, a]):,} to {int(p.loc[g, b]):,})"
        ax.text(v - 1 if v < 0 else v + 1, y, label, va="center", ha="right" if v < 0 else "left", fontsize=9.5,
                color=INK_DIM)
    ax.set_xlim(-50, 3)
    ax.set_xticks(range(-40, 1, 10))
    ax.set_xticklabels([f"{'−' if x < 0 else ''}{abs(x)}%" for x in range(-40, 1, 10)])
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.spines["left"].set_visible(False)
    credit(fig, f"Source: U.S. Office of Personnel Management, Federal Workforce Data, September {a[:4]} and {b[:4]} "
                "employment files. Our grouping of OPM\noccupational series. Some jobs moved between job codes over "
                "these years; a move inside one group does not change it.\nShows job groups with at least "
                f"{MIN_JOB_GROUP} people in {a[:4]}.")
    path = out / "05b-staff-by-job-change.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}: total {int(tot_a):,} -> {int(tot_b):,}; " + "; ".join(f"{g} {rnd(v, 0)}%" for g, v in chg.items()))


def staff_by_job_per_visit(out, a="201209", b="202309"):
    """People on board per million recreation visits, by job group, Sept. 2012 and Sept. 2023. Agency-wide OPM
    headcounts over system-wide IRMA visits for the same calendar year, so both cover every Park Service unit."""
    j = pd.read_csv(PROC / "nps_staff_by_job.csv", dtype={"snapshot": str})
    p = j.pivot(index="job_group", columns="snapshot", values="people").drop(index="Other")
    p = p[p[a] >= MIN_JOB_GROUP]
    v = pd.read_csv(PROC / "visits_system.csv").set_index("year").recreation_visits
    ya, yb = int(a[:4]), int(b[:4])
    ra, rb = p[a] / v[ya] * 1e6, p[b] / v[yb] * 1e6
    order = ra.sort_values(ascending=False).index
    fig, ax = plt.subplots(figsize=(10, 7.2))
    fig.subplots_adjust(left=0.34, right=0.95, top=0.78, bottom=0.16)
    titleblock(fig, "Fewer Park Service workers for every million visits",
               f"People on board in September for every million recreation visits that year, by kind of job, {ya} and "
               f"{yb}.\nVisits rose {rnd((v[yb] / v[ya] - 1) * 100, 0)}%, from {rnd(v[ya] / 1e6, 1)} million to "
               f"{rnd(v[yb] / 1e6, 1)} million. Staff and visits both cover every Park Service unit, not only the 63 "
               "national parks.")
    for y, g in enumerate(order):
        ax.plot([ra[g], rb[g]], [y, y], color=GRID, linewidth=2.4, zorder=2, solid_capstyle="round")
        ax.scatter([ra[g]], [y], s=70, color=INK_DIM, zorder=3, edgecolor=SURFACE, linewidth=1.5)
        ax.scatter([rb[g]], [y], s=70, color=LINE, zorder=4, edgecolor=SURFACE, linewidth=1.5)
        lo, hi = sorted([ra[g], rb[g]])
        ch = rnd((rb[g] / ra[g] - 1) * 100, 0)
        ax.text(hi + 0.6, y, f"{rnd(ra[g], 2 if ra[g] < 1 else 1)} to {rnd(rb[g], 2 if rb[g] < 1 else 1)}  ({'−' if ch < 0 else '+'}{abs(ch)}%)",
                va="center", ha="left", fontsize=9.5, color=INK_DIM)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order, fontsize=10.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 32)
    ax.set_xticks(range(0, 31, 5))
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.spines["left"].set_visible(False)
    fig.text(0.34, 0.805, f"● {ya}", color=INK_DIM, fontsize=11, fontweight="bold")
    fig.text(0.42, 0.805, f"● {yb}", color=LINE, fontsize=11, fontweight="bold")
    credit(fig, f"Sources: U.S. Office of Personnel Management, Federal Workforce Data, September {ya} and {yb}; NPS "
                "Visitor Use Statistics, system-wide totals.\nHeadcounts, including seasonal staff. Our grouping of "
                "OPM occupational series and our calculation.\nShows job groups with at least "
                f"{MIN_JOB_GROUP} people in {ya}.")
    path = out / "05c-staff-by-job-per-visit.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}: visits {v[ya]:,} -> {v[yb]:,}; " +
          "; ".join(f"{g} {rnd(ra[g], 2)} -> {rnd(rb[g], 2)} ({rnd((rb[g] / ra[g] - 1) * 100, 0)}%)" for g in order))


# what was published, by the fiscal or calendar year the figures cover; every cell is sourced in research/availability/
# states: "online" published and still online; "archive" published, now found only in the Internet Archive; None not found
AVAIL_ROWS = [
    ("Visits by park", {y: "online" for y in range(2008, 2026)}),
    ("Budget and staff by park", {**{y: "online" for y in range(2008, 2024)}, 2024: None, 2025: None}),
    ("Repair backlog by park", {**{y: None for y in range(2008, 2014)}, **{y: "archive" for y in range(2014, 2019)},
                                2019: None, 2020: None, 2021: None, 2022: "online", 2023: None, 2024: "archive",
                                2025: "online"}),
]
AVAIL_NOTE = {("Repair backlog by park", 2024): "25 parks"}


def availability_grid(out):
    from matplotlib.patches import Rectangle
    years = list(range(2008, 2026))
    fig, ax = plt.subplots(figsize=(10, 4.6))
    fig.subplots_adjust(left=0.25, right=0.97, top=0.62, bottom=0.24)
    titleblock(fig, "What the Park Service publishes for each park",
               "One cell per year of data. Visits are calendar years; budget, staff and repair backlog are fiscal years.")
    colors = {"online": LINE, "archive": "#e08a1e"}
    for row, (label, cells) in enumerate(AVAIL_ROWS):
        for x, y in enumerate(years):
            st = cells.get(y)
            ax.add_patch(Rectangle((x + 0.06, row + 0.12), 0.88, 0.76, facecolor=colors.get(st, SURFACE),
                                   edgecolor=GRID if st is None else colors[st], linewidth=1.0))
            note = AVAIL_NOTE.get((label, y))
            if note:
                ax.text(x + 0.5, row + 0.5, note.replace(" ", "\n"), ha="center", va="center", fontsize=7,
                        color=SURFACE, linespacing=1.1)
    ax.set_xlim(0, len(years))
    ax.set_ylim(len(AVAIL_ROWS), 0)
    ax.set_yticks([r + 0.5 for r in range(len(AVAIL_ROWS))])
    ax.set_yticklabels([r[0] for r in AVAIL_ROWS], fontsize=11, color=INK)
    ax.set_xticks([i + 0.5 for i, y in enumerate(years) if y % 2 == 0])
    ax.set_xticklabels([str(y) for y in years if y % 2 == 0])
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    # legend as colored words
    fig.text(0.25, 0.70, "Published and online", color=LINE, fontsize=10.5, fontweight="bold")
    fig.text(0.47, 0.70, "Published, now found only in the Internet Archive", color="#e08a1e", fontsize=10.5,
             fontweight="bold")
    fig.text(0.85, 0.70, "Not found", color=INK_DIM, fontsize=10.5, fontweight="bold")
    credit(fig, "Sources: NPS Visitor Use Statistics; NPS budget justifications, FY2010 to FY2027 books; NPS deferred "
                "maintenance reports and fact sheets,\ncurrent and archived. Checked Oct. 22, 2026. Budget and staff after "
                "FY2023: six parks post their own figures on their websites,\nbut no park-by-park table covers all parks. "
                "Evidence for each cell: research/availability/ in the NationalParks-public repo.")
    path = out / "07-what-is-published.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "posts/national-parks-data-gap/images")
    out = ap.parse_args().out
    yellowstone_budget(ROOT / "data/build/charts")  # kept, not used in the post
    visits_budget(ROOT / "data/build/charts", "YELL", "Yellowstone", "01-yellowstone-visits-budget.png")  # kept, not used
    visits_budget(out, "MORA", "Mount Rainier", "01-mount-rainier-visits-budget.png", vmax=1.8e6, bmax=21e6,
                  vbelow=(2012,))
    per_visit(out, "MORA", "Mount Rainier", "02-mount-rainier-budget-per-visit.png", ymax=21, step=3, above=(2012,))
    budget_total_nominal_real(out)
    budget_change_by_line(out)
    staff_total(out)
    staff_per_visits(out)
    staff_by_job(ROOT / "data/build/charts")  # kept, not used in the post
    staff_by_job_change(out)
    staff_by_job_per_visit(out)
    park_reports_table(out)
    availability_grid(out)
