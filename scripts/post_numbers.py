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
    # staff per 100,000 visits, over lines whose parks we have visits for
    okl = [u for u in real.index if set(units.get(u, [u])) <= set(parks)]
    mem = [c for u in okl for c in units.get(u, [u])]
    spv = lambda fy: fte.loc[okl, fy].sum() / vis.loc[mem, fy].sum() * 1e5
    add("staff_per_100k_lines", f"{len(okl)} lines, {len(mem)} parks")
    add("staff_per_100k_y0", f"{r(spv(y0), 1)}")
    add("staff_per_100k_last", f"{r(spv(fy1), 1)}")
    add("staff_per_100k_change", f"{r(pct(spv(y0), spv(fy1)))}%")
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
    # Mount Rainier, the opening example (no visit counting changes of any kind, 2008 to 2025)
    mv = vis.loc["MORA"]
    add("mora_visits_y0", f"{r(mv[y0] / 1e6, 1)} million", f"{int(mv[y0]):,}")
    add("mora_visits_last", f"{r(mv[v1] / 1e6, 1)} million", f"{int(mv[v1]):,}")
    add("mora_visits_change", f"{r(pct(mv[y0], mv[v1]))}%")
    add("mora_budget_y0", f"${r(real.loc['MORA', y0] / 1e6, 1)} million")
    add("mora_budget_last", f"${r(real.loc['MORA', fy1] / 1e6, 1)} million")
    add("mora_budget_change", f"{r(pct(real.loc['MORA', y0], real.loc['MORA', fy1]))}%")
    mq0, mq1 = real.loc["MORA", y0] / mv[y0], real.loc["MORA", fy1] / mv[fy1]
    add("mora_per_visit_y0", f"${r(mq0, 2)}")
    add("mora_per_visit_last", f"${r(mq1, 2)}")
    add("mora_per_visit_change", f"{r(pct(mq0, mq1))}%")
    methods = json.loads((CFG / "visit_method_changes.json").read_text()).get("MORA", [])
    add("mora_counting_changes_2008_2025", len([m for m in methods if 2008 <= m["year"] <= v1]))
    # outside figures quoted in the post (sources in research/availability/)
    add("gao_nps_employees_2024", "18,096", "GAO-26-108557, Dec. 31, 2024")
    add("gao_nps_employees_2025", "15,156", "GAO-26-108557, Dec. 31, 2025")
    add("gao_change", f"{r(pct(18096, 15156))}%")
    add("grca_staff_fy24", 427, "nps.gov/grca statistics page")
    add("grca_staff_fy25", 369, "nps.gov/grca statistics page")
    add("grca_staff_change", f"{r(pct(427, 369))}%")
    add("mora_visits_change_to_fy1", f"{r(pct(mv[y0], mv[fy1]))}%", f"{y0} to {fy1}, the last budget year")
    # Park Service people on board by job group, OPM Federal Workforce Data (scripts/fetch/opm_jobs.py)
    jobs = pd.read_csv(PROC / "nps_staff_by_job.csv", dtype={"snapshot": str})
    j = jobs[jobs.snapshot == "202509"].set_index("job_group").people
    add("opm_nps_people_sep2025", f"{int(j.sum()):,}", "Sept. 2025, headcount incl. seasonal, agency-wide")
    for g, v in j.sort_values(ascending=False).items():
        add(f"opm_job_{g}", f"{int(v):,} ({r(v / j.sum() * 100)}%)")
    # change by job group, Sept. 2012 to Sept. 2023 (the last budget-table year)
    pj = jobs.pivot(index="job_group", columns="snapshot", values="people")
    add("opm_nps_people_sep2012", f"{int(pj["201209"].sum()):,}")
    add("opm_nps_people_sep2023", f"{int(pj["202309"].sum()):,}")
    add("opm_nps_people_change_2012_2023", f"{r(pct(pj["201209"].sum(), pj["202309"].sum()))}%")
    for g in pj.index:
        add(f"opm_job_change_2012_2023_{g}", f"{r(pct(pj.loc[g, "201209"], pj.loc[g, "202309"]))}%",
            f"{int(pj.loc[g, "201209"]):,} to {int(pj.loc[g, "202309"]):,}")
    # per million recreation visits, all Park Service units (IRMA system-wide totals)
    vs = pd.read_csv(PROC / "visits_system.csv").set_index("year").recreation_visits
    add("visits_system_2012", f"{r(vs[2012] / 1e6, 1)} million", f"{int(vs[2012]):,}")
    add("visits_system_2023", f"{r(vs[2023] / 1e6, 1)} million", f"{int(vs[2023]):,}")
    add("visits_system_change_2012_2023", f"{r(pct(vs[2012], vs[2023]))}%")
    pm = lambda s, y: pj[s].sum() / vs[y] * 1e6
    add("opm_people_per_million_visits_2012", f"{r(pm("201209", 2012))}")
    add("opm_people_per_million_visits_2023", f"{r(pm("202309", 2023))}")
    add("opm_people_per_million_visits_change", f"{r(pct(pm("201209", 2012), pm("202309", 2023)))}%")
    for g in pj.index:
        a, b = pj.loc[g, "201209"] / vs[2012] * 1e6, pj.loc[g, "202309"] / vs[2023] * 1e6
        add(f"opm_per_million_visits_{g}", f"{r(a, 1)} to {r(b, 1)}", f"{r(pct(a, b))}%")

    lines_md = [f"# Numbers used in the post", "",
                f"Computed by scripts/post_numbers.py from data/processed. Comparison FY{y0}/{y0} to FY{fy1}/{v1}; "
                f"dollars in FY{base}.", "", "| Key | Value | Note |", "|---|---|---|"]
    lines_md += [f"| {k} | {v} | {n} |" for k, v, n in out]
    (ROOT / "research/post_numbers.md").write_text("\n".join(lines_md) + "\n")
    print("\n".join(f"{k}: {v}" for k, v, _ in out))


main()
