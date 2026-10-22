# Availability: park budget and staff figures outside the NPS budget books

Checked 2026-10-22. Facts only. We do not know why any item is missing, and
we make no guess. This file adds to `budget.md`, which covers the budget books.
Congress (committee reports, the joint explanatory statement, hearings) and GAO
are covered in a separate file and are left out here.

Labels:

- **No longer published**: shown to exist before, absent now, with evidence of
  both.
- **Not available**: no evidence it was ever published.

Downloads are in `data/raw/elsewhere/`. Park figures are in
`budget_elsewhere_figures.csv` (columns `code,fiscal_year,measure,value,unit,source_url,source_type,captured`).

## Short answer

1. **No full park-by-park table of base budget or staff for FY 2024, FY 2025
   or FY 2026 was found anywhere.** We found no FY 2026 NPS budget
   justification on doi.gov, nps.gov or the Wayback Machine, and no copy
   anywhere else. Label: not available.
2. **Some single parks post their own figures on their nps.gov pages.** Of the
   63 parks, 6 post a base budget for FY 2024 or later (Grand Canyon, Great
   Smoky Mountains, Yellowstone, Glacier Bay, Kenai Fjords, Yosemite). Grand
   Canyon is the only one that posts a FY 2025 base amount plus staff totals
   for FY 2024 and FY 2025. A few more post staff counts with no year.
3. **Federal workforce records by duty station are public for 2024 to 2026.**
   OPM replaced FedScope with a new site, Federal Workforce Data (FWD), at
   data.opm.gov. FedScope was retired on January 31, 2026. FWD has monthly,
   person-level files for NPS through August 2026, and most records name the
   duty station (city and county). Duty stations are not parks, but for many
   parks the duty station is the park itself (for example "YELLOWSTONE PARK,
   WY"). This is the only official source we found that covers FY 2024 to FY
   2026 for many parks at once.
4. **Removal.** In 36 park pages checked in the Wayback Machine, no page took
   down a FY 2024 or later budget or staff figure. Two narrower changes:
   Yellowstone's page dropped its "Full-time equivalent (FTE): 512" line when
   it was updated in April 2025, and Grand Canyon's page replaced its FY 2024
   funding section with FY 2025 in March 2026 (its normal yearly update). The
   one clear removal of a whole source is FedScope, which OPM retired on
   January 31, 2026 and replaced with FWD. See sections 2b and 4.

## 1. Was an FY 2026 NPS budget justification ever posted?

- **Wayback CDX, doi.gov upload folders.** We listed every archived file in
  each monthly folder `https://www.doi.gov/sites/default/files/documents/YYYY-MM/`
  from 2024-12 through 2026-06 (19 folders). Lists are in
  `data/raw/elsewhere/cdx/docs_*.txt`.
  - Found FY 2026 justifications for other bureaus, for example
    `2025-06/cupca-2026-greenbook508.pdf`, `2025-06/sol-2026-greenbook508.pdf`,
    `2025-07/boem-2026-greenbook508.pdf`, `2025-09/bor-2026-greenbook508.pdf`,
    `2025-11/blm-2026-greenbook508.pdf`, `2025-12/fws-2026-greenbook508.pdf`.
  - Found only two FY 2026 NPS budget files:
    `2025-06/fy26bibnps508.pdf` (the 6-page Budget in Brief chapter, first
    captured 20250604050841, already in `budget.md`) and
    `2025-05/fy21-fy25-nps-gaoa-lrf-pdss-` (a cut-off address, HTTP 404,
    captured 20260917191048).
  - No file name with "nps" plus "greenbook" or "justification" for FY 2026.
    The only NPS greenbook in these folders is the FY 2027 one
    (`2026-04/fy2027greenbooknps_0.pdf`, first captured 20260414053114).
- **Other paths.** Wildcard CDX queries on `doi.gov/sites/doi.gov/files/` and
  on `nps.gov/aboutus/upload/` returned no FY 2026 NPS budget file. (The broad
  doi.gov queries with a regex filter timed out with HTTP 504; the month-by-month
  folder lists above replace them.)
- **Copies elsewhere.** Web searches for the title "National Park Service
  Budget Justifications and Performance Information Fiscal Year 2026" and for
  copies on govinfo, Scribd and DocumentCloud found none. The search returned
  only other bureaus' FY 2026 books and NPS's FY 2027 book.
- **News of a draft or leak.** We found no report that an FY 2026 NPS
  justification was drafted, leaked or withheld.
- **Label: not available.**

## 2. Park websites

**Method.** For each of the 63 parks we fetched about 30 likely pages (for
example `learn/management/statistics.htm`, `planyourvisit/parkfacts.htm`,
`learn/park-facts.htm`, fact sheets), the park's `learn/management/index.htm`
and every linked page whose name suggests facts or statistics, plus matching
pages from the nps.gov sitemap. 260 pages returned HTTP 200. Log:
`data/raw/elsewhere/parkpages/crawl_log.tsv`. Pages we did not guess or that
are not linked from those places could be missed.

### 2a. Parks that post a base budget or staff figure (live, 2026-10-22)

| Park | Budget figure | Staff figure | Page "Last updated" |
|---|---|---|---|
| Grand Canyon (GRCA) | FY 2025: "ONPS Base Operating Appropriation: $23,670,800.00" | "Total National Park Service Staffing" (permanent, term and seasonal): FY-21 584, FY-22 407, FY-23 424, FY-24 427, FY-25 369 | July 28, 2026 |
| Yosemite (YOSE) | "2025 Operating Budget: Approximately $32 million" | "2025 NPS Employees at Yosemite: 674 summer and 499 winter" | October 19, 2026 |
| Kenai Fjords (KEFJ), fact sheet PDF | "2025 base appropriations $4.44 million" | 23 permanent, 28 seasonal (no year on the line; sheet "Updated January 2026") | January 2026 |
| Yellowstone (YELL) | "Fiscal Year 2024 (in millions)" "Operations and staff (base): $39.8" | "National Park Service (2024)": total during summer 748; permanent 392; term 4; seasonal 356 | April 18, 2025 |
| Great Smoky Mountains (GRSM) | "$21.56 million base budget in Fiscal Year 2024." | "Approximately 275 permanent employees and 140 seasonal employees." (no year) | June 2, 2025 |
| Glacier Bay (GLBA) | "Base Budget $5,752,744 (Fiscal Year 2024)" | Permanent 68; Seasonal and Term 53 (no year) | September 30, 2025 |
| Big Bend (BIBE) | none | "65 permanent employees", "13 seasonal employees" (no year) | January 1, 2026 |
| Denali (DENA) | base budget table, 2000 to 2023 only (2023: $16,603,000) | 129 permanent, 135 seasonal (no year) | April 14, 2025 |
| Redwood (REDW) | FY 2017 only ($9,601,000) | 88 permanent, 37 temporary (no year) | August 21, 2026 |
| White Sands (WHSA) | "$1,648,000 base budget in Fiscal Year 2019." | "approximately 17 permanent, 3 term, and about 10 seasonal" | June 17, 2024 |
| Channel Islands (CHIS) | FY 2001 to FY 2012 only | none | June 10, 2016 |
| Hot Springs (HOSP) | FY 2003 to FY 2006 only | none | May 5, 2020 |
| Great Basin (GRBA) | none | "approximately 30 employees. Another 30 seasonal" | October 8, 2021 |
| American Samoa (NPSA) | none | "25 employees (permanent, term, and seasonal)" | February 28, 2015 |
| Zion (ZION) | none | chart image of FTE since 2010; text: "has gone from 184 to 164" (chart file is named 2022) | January 12, 2026 |

Bryce Canyon (`brca/learn/management/statistics.htm`, updated February 28,
2023) and Mammoth Cave (`maca/learn/management/statistics.htm`, updated
December 5, 2022) have a "Budget" heading with only a general paragraph and no
figure.

**Count of FY 2024 or later park figures (official, live or archived):**

- Base budget, FY 2024 or later: 6 parks. FY 2024: GRCA (archived), GRSM, YELL,
  GLBA. FY 2025: GRCA, KEFJ. "2025 operating budget" (not called base): YOSE.
  None for FY 2026.
- Staff with a FY 2024 or later year: 3 parks. GRCA (FY 2024 and FY 2025), YELL
  (2024), YOSE (2024 in a 2025 capture, 2025 live).
- Staff with no year on a page updated 2025 or 2026: GRSM, GLBA, KEFJ, BIBE,
  DENA, REDW.

### 2b. Wayback history of these pages, 2024 to 2026

We pulled Wayback captures from January 2024 to October 2026 for 36 park
pages (the pages in 2a plus the statistics or fact pages of 21 other parks).
For each page we sampled up to 16 captures (Grand Canyon, Yellowstone, Great
Smoky Mountains) or up to 7 captures (the rest), spread across the period, and
compared every line that mentions budget, staff or fiscal year. Results are in
`data/raw/elsewhere/wayback_parks/`. Because we sampled, a short-lived version
between two samples could be missed.

**No page removed a FY 2024 or later budget or staff figure.** Every change we
saw was a newer figure replacing an older one, or a new section being added.
Details:

- **Grand Canyon.** Figures move forward one year at a time.
  - 20241203094600 ("Last updated: November 17, 2024"): "FY 2023 Funding",
    "ONPS Base Operating Appropriation: $24,626,151.00"; staffing list ends
    "(FY-23) 424".
  - 20250423031447 ("Last updated: March 17, 2025"): "FY 2024 Funding",
    "ONPS Base Operating Appropriation: $24,158,100.00", "ONPS Non-base Funding:
    $440,063.00"; staffing list ends "(FY-24) 427". Division lines for FY 2024
    sum to 427 (Superintendent's Office 21, Administration 33, Science and
    Resource Management 42, Commercial Services 14, Planning, Environment, and
    Projects 25, Facility Management 117, Interpretation 36, Visitor and
    Resource Protection 115, Fire and Aviation Management 24).
  - Still FY 2024 at 20260209213624 ("Last updated: January 6, 2026").
  - 20260328022455 ("Last updated: March 18, 2026"): "FY 2025 Funding",
    "ONPS Base Operating Appropriation: $23,670,800.00"; staffing list ends
    "(FY-25) 369". Same on the live page.
  - So the FY 2024 base amount ($24,158,100) is no longer on the live page,
    while the FY 2024 staff total (427) still is. This is the page's normal
    yearly update.
- **Yellowstone.** One line was dropped.
  - Before, at 20250219161312 ("Last updated: April 4, 2023"): "National Park
    Service (January 2023)", "Total during summer: 750", "Full-time equivalent
    (FTE): 512", "Permanent: 308", "Term (variable duration): 2", "Seasonal:
    202". Budget "Fiscal Year 2022 (in millions)", "Operations and staff (base):
    $37.9".
  - After, from 20250526112758 ("Last updated: April 18, 2025") to the live
    page: "National Park Service (2024)", "Total during summer: 748",
    "Permanent: 392", "Term (variable duration): 4", "Seasonal: 356". Budget
    "Fiscal Year 2024 (in millions)", "Operations and staff (base): $39.8".
  - The FTE line is in every sampled capture before the April 2025 update and
    in none after. **Label for the Yellowstone FTE line: no longer published.**
    The FY 2024 budget and the 2024 head counts were added at the same time.
- **Great Smoky Mountains.** "$22 million base budget in Fiscal Year 2023" and
  "Approximately 200 permanent employees and 140 seasonal employees" at
  20241221193329 ("Last updated: August 30, 2024"); "$21.56 million base budget
  in Fiscal Year 2024" and "Approximately 275 permanent employees and 140
  seasonal employees" from 20250417003005 ("Last updated: April 2, 2025") to the
  live page.
- **Yosemite.** "2021 Operating Budget: Approximately $30 million" and "2021
  NPS Employees at Yosemite: 741 summer and 451 winter" through 20250413120948.
  At 20251006104459 ("Last updated: August 14, 2025"): "2023 Operating Budget:
  Approximately $31 million" and "2024 NPS Employees at Yosemite: 758 summer
  and 506 winter". Live ("Last updated: October 19, 2026"): "2025 Operating
  Budget: Approximately $32 million" and "2025 NPS Employees at Yosemite: 674
  summer and 499 winter".
- **Big Bend.** "83 permanent employees" and "26 seasonal employees" through
  20250418000333 ("Last updated: February 4, 2025"); "65 permanent employees"
  and "13 seasonal employees" from 20260204001536 ("Last updated: January 1,
  2026"). Neither version gives a year.
- **Glacier Bay.** The fact sheet had no budget or staff lines in captures
  from 20240415190416 to 20250524032551. The lines "Base Budget $5,752,744
  (Fiscal Year 2024)" and "Permanent: 68", "Seasonal & Term: 53" first appear at
  20260906151942 ("Last updated: September 30, 2025").
- **No change in budget or staff lines, 2024 to 2026:** Denali (129 permanent,
  135 seasonal; base budget table ends 2023), Redwood (FY 2017 budget), White
  Sands (FY 2019 budget), Channel Islands (FY 2012 last), Hot Springs (FY 2006
  last), Great Basin, American Samoa, Zion (FTE chart from 2022), and the
  "Budget" headings with no figure at Bryce Canyon and Mammoth Cave.
- **No budget or staff lines in any capture, 2024 to 2026:** Acadia, Biscayne,
  Everglades, Gateway Arch, Glacier, Indiana Dunes, Isle Royale, Joshua Tree,
  Kenai Fjords index page (it links to the fact sheet), Lake Clark, Olympic,
  Rocky Mountain, Shenandoah, Theodore Roosevelt, Wrangell-St. Elias.
- **No usable captures since 2024:** Black Canyon, Hawaii Volcanoes, North
  Cascades and Pinnacles statistics pages (no HTTP 200 capture in the period),
  and Grand Teton (captures had no main text we could read).

## 3. Foundation documents, superintendent reports, park newspapers

- We did not review foundation documents park by park. A web search for
  foundation documents with "base budget" or "full-time equivalent" for 2024 or
  later found none.
- Superintendent annual reports: Denali's page
  (https://www.nps.gov/dena/learn/management/supts-reports.htm, last updated
  February 22, 2024) lists reports through "Supt-Annual-Report_2015-2017.pdf".
  Yosemite's "Annual Reports" page holds only water quality reports. We found no
  2024 or later superintendent annual report for any of the 63 parks with budget
  or staff figures.
- Park newspapers: not checked one by one. Not checked.

## 4. OPM workforce data

### FedScope was retired

- The OPM FedScope page, captured by the Wayback Machine at 20260131100059,
  says: "OPM has launched the Federal Workforce Data (FWD) website to replace
  FedScope. The new site, available at data.opm.gov, introduces predictable
  monthly data updates, interactive visualizations, downloadable datasets, and
  improved transparency around data quality. FedScope will be no longer be
  available as of January 31, 2026."
  (https://web.archive.org/web/20260131100059/https://www.fedscope.opm.gov/)
- The last Wayback capture of `https://www.fedscope.opm.gov/` with HTTP 200 is
  20260131100059. From February 2026 on, every capture is a 301 redirect. The
  capture at 20260215000608 redirects to `https://data.opm.gov/`.
- Live on 2026-10-22, `https://www.fedscope.opm.gov/` returned HTTP 403 to a
  plain request and showed the FWD home page through a browser-style request.
- News coverage (secondary): MeriTalk and FedScoop report FWD launched in
  January 2026 (https://www.meritalk.com/articles/opm-launches-federal-workforce-data-site-replacing-fedscope/,
  https://fedscoop.com/opm-federal-workforce-data-overhaul-fedscope/).

### What FWD has now

- Site: https://data.opm.gov/ ("Release 1.16.1 | Site last updated October 7,
  2026"). Home page: "August 2026 employment and accessions data now
  available."
- Downloads: monthly person-level "Employment", "Accessions" and "Separations"
  files in Parquet format, through an open API
  (`https://data.opm.gov/api/v1/files/employment?current=true`). The list has
  208 employment files: quarterly from March 2005, monthly from 2012, and
  monthly for all of 2024 and 2025 and for January to August 2026.
- The employment file has `agency_subelement_code` (NPS is `IN10`) and duty
  station fields: `duty_station_code`, `duty_station_city`,
  `duty_station_county`, `duty_station_state`. Each row is one person with
  `count` = 1.
- We downloaded six months: August 2024, September 2024, January 2025, August
  2025, September 2025 (all version 4, published October 3 to 4, 2026) and
  August 2026 (version 1, published October 4, 2026). Files are in
  `data/raw/elsewhere/opm/`; the NPS extract is `nps_ds.csv`.

| Snapshot | NPS people on board | Duty station shown as REDACTED | Career and career-conditional (tenure groups 1 and 2) |
|---|---|---|---|
| Aug 2024 | 22,339 | 533 | 16,364 |
| Sep 2024 | 21,866 | 532 | 16,411 |
| Jan 2025 | 17,904 | 533 | 16,105 |
| Aug 2025 | 19,990 | 525 | 14,187 |
| Sep 2025 | 19,315 | 525 | 14,126 |
| Aug 2026 | 19,006 | 806 | 12,521 |

These are headcounts on the last day of the month, not FTE. Seasonal staff are
in the "no tenure group" and tenure group 3 rows, so totals swing with the
season. August 2026 is version 1 and may be revised.

### Duty station is not the same as park

Many duty stations are inside a park and carry its name ("YELLOWSTONE PARK,
WY", "YOSEMITE NATL PARK, CA", "GRAND CANYON, AZ", "DENALI PARK, AK"). Others
are towns shared by more than one park or office (Moab, UT for Arches and
Canyonlands; Homestead, FL for Everglades and Biscayne; Washington, DC for
headquarters). We built a first-pass map for 51 of the 63 parks (49 parks on
their own plus Sequoia and Kings Canyon as one entry), using only duty stations that
are the park or its headquarters town. The map is in
`data/raw/elsewhere/opm/nps_dutystation_proxy.csv` and in the figures CSV with
measure names starting `opm_fwd_`. These are proxies, not park totals. Staff
who work at a park but are assigned elsewhere are missed, and some towns may
include non-park offices. We left out 12 parks: Arches, Canyonlands, Everglades,
Biscayne, Dry Tortugas, Black Canyon, New River Gorge, Saguaro, Gates of the
Arctic, Kobuk Valley, North Cascades and Guadalupe Mountains. Gateway Arch is
included with a caution, since Saint Louis, MO may hold other NPS offices.
Shenandoah uses a code with no city name (`510000139`, which matches Page
County, VA).

Examples (career and career-conditional only, people on board):

| Park | Duty stations used | Aug 2024 | Aug 2025 | Aug 2026 |
|---|---|---|---|---|
| Yellowstone | Yellowstone Park WY; Yellowstone National Pk MT | 401 | 393 | 341 |
| Yosemite | Yosemite Natl Park; El Portal CA | 395 | 369 | 317 |
| Grand Canyon | Grand Canyon; North Rim; Desert View AZ | 320 | 284 | 241 |
| Great Smoky Mountains | Gatlinburg; Townsend TN | 191 | 175 | 147 |
| Zion | Springdale UT | 134 | 116 | 101 |

**Label for this section:** FedScope: no longer published (shown live through
20260131100059; redirected from February 2026). Its replacement, FWD, is
available and covers 2024 to 2026 by duty station.

## 5. USAspending.gov and the OMB budget appendix

- **USAspending.** The API
  (`https://api.usaspending.gov/api/v2/agency/014/sub_agency/?fiscal_year=2025`)
  lists NPS awards by awarding office. The offices are mostly regional
  contracting offices (for example "IMR INTERMOUNTAIN REGION(1200)", "PWR
  SF/SEA MABO(85000)"); only two are parks ("SANTA MONICA MTNS NRA", "JOSHUA
  TREE NATIONAL PARK", each under $1 million). These are contract and grant
  obligations only. They are not base budget and not staff.
- **OMB budget appendix.** FY 2026 appendix
  (https://www.govinfo.gov/content/pkg/BUDGET-2026-APP/pdf/BUDGET-2026-APP.pdf)
  and FY 2027 Interior chapter
  (https://www.whitehouse.gov/wp-content/uploads/2026/04/int_fy2027.pdf). Both
  show "Operation of the National Park System" by program activity only: "Park
  management" (FY 2026 appendix: 2,676 for 2024, 2,676 for 2025, 1,779 for
  2026, in millions) and "External administrative costs." No park names appear
  in either NPS section. Account level only.

## 6. FOIA

- **NPS FOIA library** (https://www.nps.gov/aboutus/foia/foia-reading-room.htm,
  last updated April 24, 2024) has no budget or staffing tables.
- **NPS FOIA logs** are on the "Frequently Requested Documents" page
  (https://www.nps.gov/aboutus/foia/foia-frd.htm, last updated October 16,
  2026). The newest log is `NPS-FY-2023.csv`. `NPS-FY-2024.csv` returned HTTP
  404. The FY 2023 log shows requests for single-park budgets (for example
  DOI-NPS-2023-001438, "Mt Rainier National Park Budget for FY 2020, 2021, 2022
  and 2023 (planned) and an itemized list of all active employees", "Full
  Grant"), but the released records are not posted.
- **DOI FOIA logs page** (https://www.doi.gov/foia/department-interior-foia-logs)
  links logs for 2007 to 2011 and FY 2017 only. A November 2025 Office of the
  Secretary log exists at
  https://www.doi.gov/sites/default/files/documents/2026-03/11-nov-2025foia-logredacted.pdf
  (41 pages). We found no request in it for park budget or staffing tables.
- **DOI FOIA library** (https://www.doi.gov/document-library/foia) holds FOIA
  reports only.
- **MuckRock**: not accessible. The site and its API returned HTTP 403
  (Cloudflare) to our requests.
- We did not check the Wayback Machine for an FY 2024 or FY 2025 NPS FOIA log;
  those CDX requests timed out.

## 7. News and advocacy groups (secondary sources)

None of these published a park-by-park table. Figures as reported:

- **NPCA**, press release, July 3, 2025
  (https://www.npca.org/articles/9551-staffing-crisis-at-national-parks-reaches-breaking-point-new-data-shows-24):
  24% loss of permanent staff since January 2025, "Utilizing internal data from
  the Department of the Interior workforce database." Park examples: Black
  Canyon of the Gunnison "unable to fill 24 of the park's 74 positions"; Big
  Bend at "almost half" of full staffing; National Parks of Boston "over 50
  full-time vacancies" across three units. No table or data link.
- **NPCA**, August 27, 2025
  (https://www.npca.org/articles/10343-shuttered-visitor-centers-closed-campgrounds-slower-emergency-response):
  posted an internal NPS "operational status" spreadsheet from July 2025, "first
  reported by the New York Times." We downloaded it
  (`data/raw/elsewhere/npca/opstatus.xlsx`, 719 rows). It lists closures and
  service cuts by park. It has no staff counts or budgets.
- **Grand Teton**, Jackson Hole News&Guide, April 26, 2025: the park "has about
  180 permanent employees, which is nearly identical to 2024," per an NPS
  spokesperson statement; "about 150 seasonal employees, on par with 2024."
- **Yellowstone**, WyoFile, April 22, 2025 (read as republished at
  https://coyotegulch.blog/2025/04/25/despite-doge-at-interior-yellowstone-staffing-higher-than-last-year-angus-m-thuermer-jr-wyofile-com/):
  "Going into this year, we should have a total of 769 NPS employees," park
  spokeswoman Linda Veress said, up from 748.
- **ANPR**, January 9, 2026 (https://www.anpr.org/release/2026/0109) and
  **Roll Call**, December 31, 2025: NPCA estimate of 12,600 full-time
  employees, "down 24 percent." System level only.
- **Coalition to Protect America's National Parks**: briefs and a May 26, 2026
  memo on staffing (https://protectnps.org/2026/05/26/national-parks-face-a-strained-summer-as-staffing-shortages-deepen/);
  no park counts found.
- **PEER**: 2024 and January 2025 releases on ranger counts from FOIA, system
  and region level. Its site returned HTTP 403 to us.
- **Axios**, March 5, 2025: February 2025 firings by California park (Yosemite
  9, Joshua Tree 6). These are firings, not staff levels.
- **Washington Post, New York Times, E&E News, AP**: we found no park-by-park
  staffing table from them. We could not read paywalled articles.

## 8. data.gov

- The data.gov search (`https://catalog.data.gov/search`) for "national park
  service budget", "staffing", "employees", "FTE", "park base funding" and "park
  operating budget" returned no NPS budget or staffing dataset (only science
  datasets). `https://www.doi.gov/data.json` returned HTTP 404.
- With no dataset name, we could not test for a removed entry. **Label: not
  available.**

## 9. Other NPS and DOI reports

- **DOI Annual Performance Plan and Report.** The DOI page
  (https://www.doi.gov/performance/performance-reports) lists the "FY 2024
  Annual Performance Report" as newest
  (`/sites/default/files/documents/2025-01/2024-annual-performance-report.pdf`).
  It has no park names. No FY 2025 report is listed.
- **DOI Agency Financial Report FY 2025**
  (https://www.doi.gov/sites/default/files/documents/2026-01/fy-2025-agency-financial-report-final-508c.pdf,
  196 pages): park names appear only in photo captions and stories. No park
  budget or staff table.
- **NPS contingency plan, September 30, 2025**
  (https://www.doi.gov/sites/default/files/documents/2025-09/doi-nps-lapse-plan2025930508.pdf):
  no park-level staff counts.
- **DOI OIG "NPS Staffing Flash Report," August 2024**
  (https://www.oversight.gov/sites/default/files/documents/reports/2024-08/NPS-Staffing-Flash-Report.pdf):
  system figures through FY 2022 and early FY 2024; no park table.
- **NPS "budget allocation" documents**: we found none posted.

## What we could not access or check

- MuckRock and PEER (HTTP 403), CNN (HTTP 451), SFGate (page did not load), the
  WyoFile original page, and paywalled Washington Post, New York Times and E&E
  News articles.
- Wayback CDX was offline or timed out several times on 2026-10-22. Broad
  regex queries on doi.gov returned HTTP 504; we used month folders instead.
- Foundation documents and park newspapers were not reviewed one by one.
- Park pages outside the paths we tried may hold figures we missed.
