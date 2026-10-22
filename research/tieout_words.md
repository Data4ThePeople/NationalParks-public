# Tie-out: words

Checked 2026-10-22 against dist/index.html as built from viz/template.html and
config/page.json. Each label, threshold, note and sourced claim on the page,
with its source and a verdict: supported, partly supported, not supported, or
could not check. Items marked "fixed" were changed in this pass. The numbers
are checked in `research/tieout.md`.

| # | Where on the page | Claim | Source | Verdict |
|---|---|---|---|---|
| 1 | Intro | Park figures come from the National Park Service and the Interior Department | research/datasets/10_visitation.md, 20_budget.md, 30_deferred_maintenance.md | Supported (fixed: said "All figures", but CPI is BLS and map layers are Census and Natural Earth) |
| 2 | Intro | Budget figures are base operating budgets, adjusted for inflation unless the chart says otherwise | build: budget charts use CPI-U fiscal-year averages; "as published" marked where not adjusted | Supported |
| 3 | Availability 1 | FY2027 book has no park table and no visitation and acreage section; the park table was in every book FY2010 to FY2025; FY2025 had the visitation section | research/availability/budget.md item 3; 20_budget.md layout table | Supported (fixed: said "both were in every book", but the visitation section is verified only in FY2025) |
| 4 | Availability 2 | NPS did not release a FY2026 budget book, per CRS; last published park budget is FY2023 | CRS R42757 footnote 5; research/availability/budget.md items 1 and 2 | Supported (fixed: now says "for every park" and notes that a few parks post newer figures; Congress and elsewhere searches found no park-by-park table for FY2024 or later) |
| 5 | Availability 3 | FY2014 to FY2018 park backlog reports return "page not found"; FY2024 fact sheets replaced by FY2025; copies only in the Internet Archive; no NPS park figures for FY2019 to FY2021 or FY2023 | research/availability/deferred_maintenance.md | Supported. Note: FY2024 copies survive for 25 parks only |
| 6 | Visits subtitle | One visit is one person entering the park for recreation on one day | NPS definitions page and FAQ, quoted in 10_visitation.md | Supported |
| 7 | Visits subtitle | Dashed lines mark years with a major change in how the park counts | IRMA "Park Visitor Use and Count Procedure Changes"; lines drawn for changes rated Overhaul or Major | Supported |
| 8 | Visits note | The park changed how it counts N times since 1979; jumps in those years may come from the change | config/visit_method_changes.json (from the IRMA report) | Supported (count is all rated changes from 1979 on; wording is hedged) |
| 9 | Bryce note | 2000 to 2024 visits "too high by approximately 18–19 percent each year" from a shuttle bus counting error; no corrected numbers published | 2025 Statistical Abstract endnote; IRMA still shows old values (10_visitation.md, Revisions) | Supported |
| 10 | Designation notes | Each park's designation date and earlier name | config/designations.json quotes NPS Index 2012-2016 and "Recent Changes" page | Supported (five judgment calls listed in that file) |
| 11 | Budget subtitle | Park's share of the main operating account; leaves out construction, entrance fees, donations and Great American Outdoors Act projects | 20_budget.md "What is not in park base" (FY2025 book PDF pages 47 to 52) | Supported (fixed: said "money Congress gives the park" and "emergency funds", which the books do not say) |
| 12 | Budget, staff, per-visit charts | Label above the shaded area: "Shaded: no park-by-park table after FY2023" | Items 3 and 4; research/availability/budget_elsewhere.md | Supported (fixed: said "Not published", but six parks post FY2024 or FY2025 budget figures on their own pages) |
| 13 | Staff subtitle | Every job at the park, whatever money pays for it, as full-time equivalents; two half-time jobs count as one | Green Book footnote 2: "Total FTE shown for parks are by organization, irrespective of funding source"; 20_budget.md | Supported |
| 14 | Per-visit subtitle | Our calculation: fiscal-year base budget divided by calendar-year visits | build method | Supported (fixed: did not say fiscal and calendar years differ) |
| 15 | Shared line notes | Sequoia and Kings Canyon share one line; Katmai's line covers Aniakchak and Alagnak; North Cascades' covers Lake Chelan and Ross Lake | config/budget_units.json, from the line names in every book | Supported (fixed: Sequoia note said "one staff") |
| 16 | Kobuk Valley note | Shares a line with Cape Krusenstern and Noatak, and Bering Land Bridge until FY2019 | 20_budget.md; FY2022 book splits Bering Land Bridge out from the FY2020 amounts | Supported |
| 17 | Maintenance subtitle | Dollars as published, not adjusted; dots are separate reports; dashed lines mark method changes | 30_deferred_maintenance.md | Supported (fixed: "no park figure from the Park Service" became "that we could find", since FY2024 sheets existed for all parks) |
| 18 | Maintenance FY2022 note | Condition scoring replaced work orders; about 35% added for design and management between FY2019 and FY2021 to assets other than roads and bridges | CRS R48136; DOI OIG 2020-CR-066; NPS FAQ | Supported (fixed: said "most repairs") |
| 19 | Maintenance FY2023 note | Asset list changed; road cost model began to include recent inflation | CRS R48136 | Supported |
| 20 | Combined maintenance notes | NPS reports one figure for Sequoia and Kings Canyon, and one for Western Arctic (with Kobuk Valley) | 30_deferred_maintenance.md | Supported |
| 21 | Map legend | Five change bins, dot size by visits in the last full year | build method (thresholds are our choice, stated in the legend) | Supported |
| 22 | Footer | Alaska, Hawaii and the islands are not to scale | scripts/build_geo.py fits each inset to its own box | Supported |
| 23 | Sources list | Each source and what it supplies | research/datasets/*.md | Supported |
| 24 | Availability (Congress) | Senate Appropriations had not received the FY2026 NPS justification (July 2025); the FY2026 explanatory statement directs briefings every 60 days on staffing and visitor data by park; no public copy found | S. Rept. 119-46 p. 47; Congressional Record Jan. 8, 2026, H474 (both quotes checked word for word on govinfo, 2026-10-22); research/availability/budget_congress.md | Supported |

## Independent tie-out, 2026-10-22

A fresh agent rebuilt the numbers from the public sources: 18 parks in full, all 63 parks' visit histories, 768 budget-book values, FY2018 maintenance for all 63 parks. It found no differences in any number shown. Its report is in a separate working folder; the items it raised and what changed:

| Item | Finding | Change |
|---|---|---|
| State labels | Everglades showed "FL 6/" (NPS footnote marker), American Samoa "SAMOA", Gateway Arch "IL" unspelled | Fixed: markers stripped, names spelled out, unknown codes stop the build |
| Count of visit counting changes | Included rows NPS rates Non-material (label updates) | Fixed: Non-material rows not counted; rule added to DATASETS.md |
| FY2022 maintenance note | Linked CRS source dates the 35% markup to FY2021, not "FY2019 to FY2021"; CRS says transportation assets, not roads and bridges | Fixed: note gives CRS's FY2021 and the NPS FAQ's "through 2018", with both links |
| FY2023 maintenance wording | CRS lists 20 parks "using data from NPS"; page said none found | Fixed: subtitle says "in a Park Service or Interior file"; box names the CRS table |
| "Copies survive only in the Internet Archive" | Cannot be confirmed by searching | Fixed: "We found copies only in the Internet Archive" |
| Map bins vs table | Olympic per-visit −19.7% showed "−20%" in the table but colored "Down 5% to 20%" | Fixed: bins use the rounded value |
| Staff subtitle | "Every job" and "two half-time jobs count as one" had no source | Fixed: "Every position", FTE defined from OMB Circular A-11 |
| "Visitors" in intro, meta and JSON-LD | Page counts visits | Fixed: "visits" |
| JSON-LD | Called the books Interior Department justifications | Fixed: National Park Service budget justifications |
| Bryce Canyon | Per-visit chart still built on visits NPS calls too high | Fixed: no per-visit chart; note says so |
| CPI FY2008 stored average | 214.46275 stored as 214.4627 | Fixed: half away from zero, now 214.4628; no shown number changed |
| JSON-LD links | Pages site and repo return 404 | Expected before publishing; recheck at step 2e |

| 25 | Park notes (GRCA, YELL, GRSM, YOSE, GLBA, KEFJ) | Each park's own FY2024 or FY2025 budget and dated staff figures, quoted | research/availability/budget_elsewhere_figures.csv; GRCA checked live 2026-10-22 | Supported: all six checked live on 2026-10-22 against the park pages (Kenai Fjords against its 2026 fact sheet PDF) |
| 26 | Park summary under each name | Dates, names and acreage, one sentence per event | config/park_history.json: each event's text checked against the NPS Index 2012-2016 (or the Recent Changes page, or the Isle Royale Foundation Document) by scripts/fetch/park_history.py; acreage from the NPS Listing of Acreage as of Sept. 30, 2026 | Supported. Rules: boundary changes, transfers and leases are left out; an authorization after the unit exists is left out (Gateway Arch's 1954 entry is the arch); after a park becomes a national park only renamings and redesignations follow; a unit is named only where the source names it. Known source conflicts kept in notes: Saguaro (Oct. 4 vs. Oct. 14, 1994) and Great Sand Dunes (2000 vs. 2004); the Index dates are used |
