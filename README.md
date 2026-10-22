# National Parks Over Time

A free interactive map of the 63 U.S. national parks. Click a park to see its recreation visits, base budget and staff by year, from the National Park Service's own published figures. The page also lists park-level records that the Park Service no longer publishes.

- **Map:** https://data4thepeople.github.io/NationalParks-public/
- **Built by:** [Data 4 The People](https://www.data4thepeople.com)

## What the map shows

- **Recreation visits** for each park by calendar year, 1979 to 2025. The chart opens at 2008, and a switch shows the full record.
- **Base budget** by fiscal year, FY2008 to FY2023, adjusted for inflation to FY2025 dollars.
- **Staff** by fiscal year, FY2008 to FY2023, as total full-time equivalents.
- **Budget per visit**, our own calculation, shown only where a budget line covers parks we have visit counts for.
- **Map colors.** These show the percent change for each park: visits from 2012 to 2025, and budget, staff and budget per visit from FY2012 to FY2023.
- **A short history of each park:** when it was established, earlier names and its size.
- **A "What is missing" box.** It lists records that stopped or were taken down, with links to the evidence:
  - the park-by-park budget table
  - the FY2026 budget book
  - park-by-park repair backlog reports

Budget and staff figures stop at FY2023. That is the last year in the Park Service's park-by-park budget table. The Park Service did not release a budget book for FY2026, and its FY2027 book does not include the table.

## What's in this repo

| Path | What it is |
|---|---|
| `dist/` | The built page (`index.html`) and its shaded relief image. GitHub Pages serves this folder. |
| `viz/template.html` | The page template. Every number is computed in the browser from the data embedded at build time. |
| `scripts/fetch/` | One script per source. Each downloads and caches the raw data, then writes `data/processed/`. |
| `scripts/build_geo.py`, `scripts/relief.py` | Map outlines, park boundaries and shaded relief, projected for the lower 48 with Alaska, Hawaii, Virgin Islands and American Samoa insets. |
| `scripts/build_viz.py` | Joins the processed data and writes `dist/index.html`. |
| `scripts/tieout.py` | Recomputes every number the page shows and compares it with what headless Chrome renders. |
| `data/processed/` | Cleaned data: visits, budget and staff, CPI and deferred maintenance. |
| `config/` | Park list, shared budget lines, designation dates, park histories and page text. |
| `research/datasets/` | One file per source. `DATASETS.md` combines them. |
| `research/availability/` | Evidence for each record that is missing or no longer published. |
| `research/tieout.md`, `research/tieout_words.md` | Results of the number and wording checks. |

## Data sources

All are U.S. government or public domain sources.

- **National Park Service Visitor Use Statistics (IRMA):** recreation visits by park and month.
- **National Park Service budget justifications**, FY2010 to FY2025 books: each park's base budget and staff. They are linked from https://www.nps.gov/aboutus/budget.htm.
- **Bureau of Labor Statistics, Consumer Price Index (CPI-U):** used to adjust for inflation.
- **NPS Land Resources Division:** park boundaries, locations and acreage.
- **NPS National Park Index 2012-2016 and the "Recent Changes" page:** park designation dates.
- **NPS and Interior deferred maintenance reports**, current and archived copies.
- **U.S. Census Bureau cartographic boundaries:** state outlines.
- **Natural Earth:** 1:50m shaded relief.

## How to rebuild

The build needs Python 3.12 or later and [uv](https://docs.astral.sh/uv/).

```
uv sync
uv run python -I scripts/fetch/parks.py
uv run python -I scripts/fetch/irma_visits.py
uv run python -I scripts/fetch/irma_method_changes.py
uv run python -I scripts/fetch/greenbooks.py
uv run python -I scripts/fetch/cpi.py          # needs a free BLS API key in BLS_API_KEY
uv run python -I scripts/fetch/deferred_maintenance.py
uv run python -I scripts/fetch/park_history.py
uv run python -I scripts/build_geo.py
uv run python -I scripts/relief.py             # needs Natural Earth SR_50M in data/raw/naturalearth_relief/
uv run python -I scripts/build_viz.py
uv run python -I scripts/tieout.py             # needs Google Chrome
```

The raw downloads are not in this repo. The fetch scripts download them again.

## Key method notes

The full method is in [DATASETS.md](DATASETS.md).

- **What a visit is.** A recreation visit is one person entering a park for recreation on one day. Parks sometimes change how they count visits, and the charts mark major changes with dashed lines.
- **What the base budget covers.** It is a park's share of the Park Service's main operating account. It leaves out construction, entrance fees, donations and other accounts.
- **Inflation.** Budgets are converted to FY2025 dollars with CPI-U averaged over each federal fiscal year, which runs from October to September.
- **Shared budget lines.**
  - Sequoia and Kings Canyon share one budget line.
  - Katmai's and North Cascades' lines also fund nearby units.
  - Kobuk Valley's line changed in FY2020, so it has no budget figures.
- **Bryce Canyon.** The Park Service says its visits for 2000 through 2024 were about 18% to 19% too high. They are shown as published, and Bryce is left out of changes that compare those years with 2025.
- **Rules.** Gaps stay gaps. Nothing is filled in or typed by hand. A duplicate or unparseable value stops the build.
