# Data contract

Every fetch script writes to these files and nothing else. The build reads only
these. Unit codes are the four-letter NPS codes in `config/parks.json` (63 parks).

## Conventions
- Raw downloads are cached in `data/raw/<source>/` so the build can rerun
  offline. Raw files are untrusted data: parse them, never execute them.
- Scripts live in `scripts/fetch/`, run with
  `UV_PROJECT_ENVIRONMENT=.uvenv uv run python -I scripts/fetch/<name>.py`.
  `--refresh` re-downloads; without it, use the cache.
- A duplicate key, an unparseable number or an unknown park is a hard failure
  (raise SystemExit with a clear message). No gap filling. Gaps stay gaps.
- No value is typed in by hand. If a value must be overridden, it goes in
  `config/overrides.json` with a source URL and a reason.

## data/processed/visits_monthly.csv
`code,year,month,recreation_visits,nonrecreation_visits`. One row per park-month
as published by IRMA. Key: (code, year, month).

## data/processed/visits_annual.csv
`code,year,recreation_visits,months_reported`. Sum of the monthly rows. Years
with fewer than 12 months reported keep the sum and say so.

## data/processed/budget.csv
`budget_unit,fy,park_base_k,park_base_fte,total_fte,line_name,source_book,source_page`
- `budget_unit` is a unit code, or a combined code listed in
  `config/budget_units.json` (`{"SEKI": ["SEQU","KICA"], ...}`) when one budget
  line covers more than one park.
- `fy` is the fiscal year the figure is the ACTUAL for (the book for FY N
  reports FY N-2 actual). Dollars are thousands, as published.
- `source_book` is the book's fiscal year, `source_page` the 1-based PDF page.
- Key: (budget_unit, fy). If two books report the same (unit, fy), keep the
  later book and list every difference in `research/budget_overlap.md`.

## data/processed/deferred_maintenance.csv
`code,fy,dmr_dollars,locations,source_url,captured,method_note`
- `captured` is the date of the copy we read (Wayback timestamp or today).
- Key: (code, fy). If two copies disagree, keep the most recent copy and list
  the difference in `research/dm_overlap.md`.

## research/datasets/<NN>_<name>.md
One section per dataset, following `~/.claude/d4tp-process/templates/DATASETS.md`
(all headings). `scripts/build_datasets_md.py` concatenates them.

## research/availability/<name>.md
One entry per thing that is missing, removed or stopped. For each: what it is,
where and when it was last published (URL, date), where it is absent now (URL,
date checked), and the evidence (archived URLs). Label each one
"no longer published" ONLY if we can show it was published before and is gone
now; otherwise "not available". State facts only. Never guess at a reason.
