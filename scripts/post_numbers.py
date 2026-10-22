"""Every number the post uses, computed from data/processed and written to
research/post_numbers.md. The post's numbers are copied from that file, never
typed by hand, and the tie-out rereads it.

Budget lines: the 63 parks map to 62 budget lines; Kobuk Valley is left out (its
shared line changed in FY2020) and Sequoia and Kings Canyon share one, so 61 lines.
Katmai's and North Cascades' lines also fund nearby units, and are counted as
published.
"""
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data/processed"
CFG = ROOT / "config"


def r(v, d=0):
    q = Decimal(repr(float(v))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    return q if q != 0 else abs(q)


def pct(a, b):
    return (b / a - 1) * 100


def main():
    page = json.loads((CFG / "page.json").read_text())
    parks = [p["code"] for p in json.loads((CFG / "parks.json").read_text())]
    units = json.loads((CFG / "budget_units.json").read_text())
    member_of = {c: u for u, ms in units.items() for c in ms}
    va = pd.read_csv(PROC / "visits_annual.csv")
    va = va[va.months_reported == 12]
    bud = pd.read_csv(PROC / "budget.csv")
    cpi = pd.read_csv(PROC / "cpi.csv")
    cf = cpi[cpi.basis == "fiscal"].set_index("year").cpi
    base = int(cf.index.max())
    y0 = int(page["budget_compare_from"])
    fy1 = int(bud.fy.max())
    v1 = int(va.year.max())

    vis = va.pivot(index="code", columns="year", values="recreation_visits").loc[parks]
    lines = sorted({member_of.get(c, c) for c in parks if c not in page.get("no_budget", {})})
    b = bud[bud.budget_unit.isin(lines)].copy()
    b["real"] = b.park_base_k * 1000 * cf[base] / b.fy.map(cf)
    real = b.pivot(index="budget_unit", columns="fy", values="real")
    nom = b.pivot(index="budget_unit", columns="fy", values="park_base_k")
    fte = b.pivot(index="budget_unit", columns="fy", values="total_fte")
    if len(real) != len(lines) or real[[y0, fy1]].isna().any().any():
        raise SystemExit("a budget line is missing a comparison year")

    out = []

    def add(key, value, note=""):
        out.append((key, value, note))

    # visits
    add("parks", len(parks))
    add("visits_total_y0", f"{r(vis[y0].sum() / 1e6, 1)} million", f"{int(vis[y0].sum()):,} in {y0}")
    add("visits_total_last", f"{r(vis[v1].sum() / 1e6, 1)} million", f"{int(vis[v1].sum()):,} in {v1}")
    add("visits_total_change", f"{r(pct(vis[y0].sum(), vis[v1].sum()))}%")
    nb = vis.drop(index="BRCA")
    add("visits_total_change_without_bryce", f"{r(pct(nb[y0].sum(), nb[v1].sum()))}%",
        "Bryce's 2012 count is one NPS says ran 18-19% too high")
    up = vis[v1] > vis[y0]
    add("parks_visits_up", f"{int(up.sum())} of {int(vis[[y0, v1]].notna().all(axis=1).sum())}")
    # budgets
    add("budget_lines", len(real))
    add("budget_real_total_y0", f"${r(real[y0].sum() / 1e6)} million", f"FY{y0}, FY{base} dollars")
    add("budget_real_total_last", f"${r(real[fy1].sum() / 1e6)} million", f"FY{fy1}, FY{base} dollars")
    add("budget_real_total_change", f"{r(pct(real[y0].sum(), real[fy1].sum()))}%")
    add("budget_nominal_total_change", f"{r(pct(nom[y0].sum(), nom[fy1].sum()))}%")
    add("cpi_change", f"{r(pct(cf[y0], cf[fy1]))}%", f"CPI-U, FY{y0} to FY{fy1} averages")
    ch = pct(real[y0], real[fy1])
    add("budget_lines_down_real", f"{int((ch < 0).sum())} of {len(ch)}")
    add("budget_median_line_change", f"{r(ch.median())}%")
    for code, v in ch[ch > 0].items():
        add(f"budget_up_{code}", f"{r(v)}%")
    for code, v in ch.sort_values().head(5).items():
        add(f"budget_drop_{code}", f"{r(v)}%")
    # staff
    add("fte_total_y0", f"{int(fte[y0].sum()):,}")
    add("fte_total_last", f"{int(fte[fy1].sum()):,}")
    add("fte_total_change", f"{r(pct(fte[y0].sum(), fte[fy1].sum()))}%")
    fch = pct(fte[y0], fte[fy1])
    add("fte_lines_down", f"{int((fch < 0).sum())} of {len(fch)}")
    # busier and leaner: parks on their own line
    own = [c for c in parks if c in real.index]
    both = [c for c in own if vis.loc[c, v1] > vis.loc[c, y0] and real.loc[c, fy1] < real.loc[c, y0]]
    add("own_line_visits_up_budget_down", f"{len(both)} of {len(own)}")
    # Yellowstone
    yv = vis.loc["YELL"]
    add("yell_visits_y0", f"{r(yv[y0] / 1e6, 1)} million", f"{int(yv[y0]):,}")
    add("yell_visits_last", f"{r(yv[v1] / 1e6, 1)} million", f"{int(yv[v1]):,}")
    add("yell_visits_change", f"{r(pct(yv[y0], yv[v1]))}%")
    add("yell_budget_y0", f"${r(real.loc['YELL', y0] / 1e6, 1)} million")
    add("yell_budget_last", f"${r(real.loc['YELL', fy1] / 1e6, 1)} million")
    add("yell_budget_change", f"{r(pct(real.loc['YELL', y0], real.loc['YELL', fy1]))}%")
    add("yell_staff_y0", int(fte.loc["YELL", y0]))
    add("yell_staff_last", int(fte.loc["YELL", fy1]))
    # outside figures quoted in the post (sources in research/availability/)
    add("gao_nps_employees_2024", "18,096", "GAO-26-108557, Dec. 31, 2024")
    add("gao_nps_employees_2025", "15,156", "GAO-26-108557, Dec. 31, 2025")
    add("gao_change", f"{r(pct(18096, 15156))}%")
    add("grca_staff_fy24", 427, "nps.gov/grca statistics page")
    add("grca_staff_fy25", 369, "nps.gov/grca statistics page")

    lines_md = [f"# Numbers used in the post", "",
                f"Computed by scripts/post_numbers.py from data/processed. Comparison FY{y0}/{y0} to FY{fy1}/{v1}; "
                f"dollars in FY{base}.", "", "| Key | Value | Note |", "|---|---|---|"]
    lines_md += [f"| {k} | {v} | {n} |" for k, v, n in out]
    (ROOT / "research/post_numbers.md").write_text("\n".join(lines_md) + "\n")
    print("\n".join(f"{k}: {v}" for k, v, _ in out))


main()
