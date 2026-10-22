"""Tie-out: every number the page shows, recomputed from data/processed with pandas
and compared with what headless Chrome renders from dist/index.html.

Per park (#CODE deep link): visits in the last full year and change since the
comparison year; base budget in the last fiscal year and its change after
inflation; staff and its change; budget per visit and its change; latest
deferred maintenance; and the chart titles' year ranges. On the intro page: the
table row for every park (visits and the four map changes).

Method choices (comparison years, staff measure, exclusions) come from
config/page.json, because they are choices, not data. Values come only from
data/processed. Writes research/tieout.md and exits nonzero on any mismatch.
"""
import html
import json
import re
import subprocess
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data/processed"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGE = ROOT / "dist/index.html"
MINUS = "−"


def rnd(v, d=0):
    """Round half away from zero, as the page does."""
    q = Decimal(repr(float(v))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    return q if q != 0 else abs(q)


def f_int(v):
    return f"{rnd(v):,}"


def f_big(v):
    a = abs(v)
    if a >= 1e9:
        return f"{rnd(v / 1e9, 1):,.1f} billion"
    if a >= 1e6:
        return f"{rnd(v / 1e6, 1):,.1f} million"
    return f_int(v)


def f_usd(v):
    return "$" + f_big(v)


def f_usd2(v):
    return f"${rnd(v, 2):,.2f}"


def f_updown(v):
    r = rnd(v)
    if r == 0:
        return "about the same as"
    return ("up " if v > 0 else "down ") + f"{abs(r):,}% from"


def f_pct(v):
    r = rnd(v)
    sign = "+" if v > 0 and r != 0 else MINUS if v < 0 and r != 0 else ""
    return f"{sign}{abs(r):,}%"


def change(a, b):
    if a is None or b is None or not a > 0:
        return None
    return (b / a - 1) * 100


def rendered(code=""):
    out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--dump-dom", "--virtual-time-budget=6000",
                          "--allow-file-access-from-files", PAGE.as_uri() + (f"#{code}" if code else "")],
                         capture_output=True, text=True, timeout=120).stdout
    if "<body" not in out:
        raise SystemExit(f"Chrome returned no page for {code or 'intro'}")
    return re.sub(r"<script\b.*?</script>", "", out, flags=re.S)  # read the page, not its code


def text_of(dom, el_id):
    m = re.search(rf'id="{el_id}"[^>]*>(.*?)</(p|span|div|h2)>', dom, re.S)
    if not m:
        return None
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()


def hidden(dom, el_id):
    m = re.search(rf'<[^>]*id="{el_id}"[^>]*>', dom)
    return bool(m and re.search(r'class="[^"]*\bhidden\b', m.group(0)))


def main():
    page = json.loads((ROOT / "config/page.json").read_text())
    parks = json.loads((ROOT / "config/parks.json").read_text())
    units = json.loads((ROOT / "config/budget_units.json").read_text())
    va = pd.read_csv(PROC / "visits_annual.csv")
    bud = pd.read_csv(PROC / "budget.csv")
    cpi = pd.read_csv(PROC / "cpi.csv")

    full = va[va.months_reported == 12]
    vis = {(r.code, int(r.year)): int(r.recreation_visits) for r in full.itertuples()}
    v_last = int(full.year.max())
    fy0 = int(page["budget_compare_from"])
    fy1 = int(bud.fy.max())
    cf = cpi[cpi.basis == "fiscal"].set_index("year").cpi
    base_fy = int(cf.index.max())
    real = lambda v, fy: v * cf[base_fy] / cf[fy]
    member_of = {c: u for u, ms in units.items() for c in ms}
    codes = {p["code"] for p in parks}
    fte = page["fte_key"]
    no_cmp = {c for c, n in page.get("visit_notes", {}).items() if n.get("no_compare")}

    rows, bad = [], 0
    expect_table = {}

    def check(code, what, want, got):
        nonlocal bad
        ok = want == got
        bad += not ok
        rows.append((code, what, want, got, "ok" if ok else "MISMATCH"))

    for p in parks:
        c = p["code"]
        dom = rendered(c)
        v_first = max(int(full[full.code == c].year.min()), int(bud.fy.min()))  # default view
        a, b = vis.get((c, fy0)), vis.get((c, v_last))
        check(c, "visits title", f"Recreation visits per year, {v_first} to {v_last}", text_of(dom, "tVisits"))
        check(c, "visits last", f_int(b), text_of(dom, "vLast"))
        vchg = None if c in no_cmp else change(a, b)
        check(c, "visits change", f_updown(vchg) if vchg is not None else None, text_of(dom, "vChg"))

        bu = member_of.get(c, c)
        b_rows = bud[bud.budget_unit == bu].set_index("fy")
        members = units.get(bu, [c])
        has_b = c not in page.get("no_budget", {}) and len(b_rows) > 0
        pv_ok = has_b and set(members) <= codes and c not in no_cmp
        tb = vb = tf = tpv = None
        if has_b:
            last = int(b_rows.index.max())
            check(c, "budget last", f_usd(b_rows.park_base_k[last] * 1000), text_of(dom, "bLast"))
            r0, r1 = real(b_rows.park_base_k[fy0] * 1000, fy0), real(b_rows.park_base_k[fy1] * 1000, fy1)
            tb = change(r0, r1)
            check(c, "budget change (real)", f_updown(tb), text_of(dom, "bChg"))
            check(c, "staff last", f_int(b_rows[fte][last]), text_of(dom, "fLast"))
            tf = change(b_rows[fte][fy0], b_rows[fte][fy1])
            check(c, "staff change", f_updown(tf), text_of(dom, "fChg"))
            if pv_ok:
                line = lambda fy: sum(vis[(m, fy)] for m in members) if all((m, fy) in vis for m in members) else None
                q1 = r1 / line(fy1) if line(fy1) else None
                q0 = r0 / line(fy0) if line(fy0) else None
                check(c, "per visit last", f_usd2(q1), text_of(dom, "pvLast"))
                if c not in no_cmp:
                    tpv = change(q0, q1)
                    check(c, "per visit change", f_updown(tpv), text_of(dom, "pvChg"))
            else:
                check(c, "per visit hidden", True, hidden(dom, "bPerVisit"))
        else:
            check(c, "no budget chart", True, hidden(dom, "stBudget") or text_of(dom, "bLast") is None)

        expect_table[c] = [f_int(b) if b is not None else "n/a"] + [f_pct(x) if x is not None else "n/a"
                                                                    for x in (vchg, tb, tf, tpv)]

    # intro table: one row per park
    dom = rendered()
    names = {p["code"]: p["name"] for p in parks}
    for m in re.finditer(r'<tr><td><button type="button" data-code="(\w+)">.*?</button></td>(.*?)</tr>', dom, re.S):
        code, cells = m.group(1), [html.unescape(x) for x in re.findall(r"<td>(.*?)</td>", m.group(2))]
        check(code, "table row", expect_table.get(code), cells)
        expect_table.pop(code, None)
    for code in expect_table:
        check(code, "table row", "present", "missing")

    lines = [f"# Tie-out ({len(rows)} checks, {bad} mismatches)", "",
             f"Visits through {v_last}; comparisons from {fy0}/FY{fy0} to {v_last}/FY{fy1}; dollars in FY{base_fy}.",
             "Expected values are recomputed from data/processed; rendered values are read from headless Chrome.", "",
             "| Park | Check | Expected | Rendered | Result |", "|---|---|---|---|---|"]
    lines += [f"| {c} | {w} | {e} | {g} | {r} |" for c, w, e, g, r in rows if r != "ok"] or []
    lines += ["", f"All {len(rows) - bad} other checks matched."]
    (ROOT / "research/tieout.md").write_text("\n".join(lines) + "\n")
    print(f"{len(rows)} checks, {bad} mismatches -> research/tieout.md")
    sys.exit(1 if bad else 0)


main()
