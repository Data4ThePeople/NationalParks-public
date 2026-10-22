# Visitation

## NPS Visitor Use Statistics (National Park Service, IRMA)

**What it is.** The National Park Service (NPS) count of visits to each park,
reported every month by the park and compiled by the NPS Social Science
Program in its IRMA system. Each row in `data/processed/visits_monthly.csv` is
one park-month: recreation visits and non-recreation visits as IRMA publishes
them. `visits_annual.csv` sums the monthly recreation visits by calendar year.

- A **recreation visit** is "The entry of a person onto lands or waters
  administered by the NPS except for non-reportable and non-recreation
  visits." The rule is one entrance per person per day, so one person who
  enters on three days counts as three visits. A visit is not the same as a
  visitor.
  ([definitions](https://www.nps.gov/subjects/socialscience/nps-visitor-use-statistics-definitions.htm),
  [FAQ](https://www.nps.gov/subjects/socialscience/statistics-faq.htm))
- A **non-recreation visit** is a visit "for their own convenience or as a part
  of their occupation": commuters and through traffic on park roads, people
  going to and from private land inside the park, tradespeople, guides,
  government workers other than NPS staff, and outside researchers.
- **Non-reportable** entries are left out of both: NPS staff and their
  families, concession and contractor staff, volunteers, and brief passing
  traffic. ([Statistical Abstract 2025, Definitions, pp. ix to xi](https://irma.nps.gov/DataStore/DownloadFile/759491))

**Where it comes from.** Three IRMA outlets, no login needed.

1. REST service, XML or JSON:
   `https://irmaservices.nps.gov/v3/rest/stats/visitation?unitCodes=YELL&startMonth=1&startYear=1979&endMonth=12&endYear=2026`.
   It accepts comma-separated codes (`unitCodes=YELL,ZION`) and a full
   1979 to 2026 range in one call. It returns XML by default and JSON with
   `format=json` or an `Accept: application/json` header. Fields: Month,
   NonRecreationVisitors, RecreationVisitors, UnitCode, UnitName, Year. A
   second operation, `total/{year}`, returns system-wide monthly totals. An
   unknown code returns an empty array with HTTP 200, not an error. We fetch
   one park per call and cache it in `data/raw/irma/<CODE>.xml` (63 files,
   about 120 KB each).
2. The IRMA Stats portal, https://irma.nps.gov/Stats/, which serves SQL Server
   Reporting Services reports. Each report has a CSV export. We use
   "Monthly Public Use" (one park and one month per export, parameters
   `Park=<CODE>&RptDate=<M>/1/<YYYY>`) for current-year months, cached in
   `data/raw/irma/prelim/`. We use "Annual Park Recreation Visitation (1904 -
   Last Calendar Year)" only to check our sums (`scripts/check_irma_annual.py`,
   cache in `data/raw/irma_annual_report/`).
3. The "NPS Visitor Use Statistics Data Package, 2025" on data.gov
   (https://catalog.data.gov/dataset/nps-visitor-use-statistics-data-package-2025),
   issued 2026-03-26, covering 1979-01-01 to 2025-12-31, as two CSV files and
   an XML metadata file on the NPS DataStore (reference 2317666). We did not
   use it; it ends at 2025.

Scripts: `scripts/fetch/irma_visits.py` (visits) and
`scripts/fetch/irma_method_changes.py` (count procedure changes). Both take
`--refresh`; `irma_visits.py` also takes `--final-only` to skip the
current-year months.

**Version and vintage.** Pulled 2026-10-22. Parks enter preliminary data every
month, and "most data are available by the 15th of the following month." The
preliminary data "may be edited by the park until the entire calendar year is
finalized and moved to permanent tables in the first quarter of the following
year" ([FAQ](https://www.nps.gov/subjects/socialscience/statistics-faq.htm)).
The IRMA Stats home page on 2026-10-22 said: "Current calendar year (2026) data
are preliminary and subject to change. Data will be finalized by the end of the
first quarter of next calendar year (2027)." The 2025 totals were announced on
2026-03-13 ([NPS news release](https://www.nps.gov/orgs/1207/03-13-26-2025-visitation-statsitics.htm)),
and the 2025 Statistical Abstract has an issue date of June 2026 in the
[IRMA abstracts list](https://irma.nps.gov/Stats/Reports/AbstractsAndForecasts).

As of 2026-10-22 the REST service returns nothing for 2026 (empty array for
every park we tried, and for `total/2026`). Its last month is December 2025
for all 63 parks. The "Monthly Public Use" report does return January through
September 2026 for each park. Our monthly file therefore holds:

- 1979 through 2025: final values from the REST service.
- January through September 2026: preliminary values from "Monthly Public
  Use" (518 park-months). These will change. Parks post on their own
  schedule, so the count differs by park: 46 parks have January through
  September, and the rest stop earlier (Denali through March; Crater Lake,
  American Samoa and Olympic through July; 10 parks through August).
  Channel Islands, Katmai and Lake Clark have no 2026 month posted as of
  2026-10-22. The report's own date list for each park shows which months are
  posted, and the script reads only those. `visits_annual.csv` gives each
  park's 2026 row with its `months_reported`. Run with `--final-only` to leave
  2026 out.

**Coverage.** 63 national parks, January 1979 through September 2026 (2026 is
preliminary). Monthly data begin in 1979 for every park whose history in IRMA
reaches back that far. Eight parks start later in IRMA:

| Park | First month in IRMA |
|---|---|
| GAAR, KEFJ, KOVA, LACL, WRST | January 1982 |
| NERI | January 1984 |
| CONG | January 1985 |
| NPSA | January 2002 |

Many of these units existed under other names or types before they became
national parks (see `config/designations.json`). IRMA files the history under
the current code, so a series can include years before the unit was a
national park. For example, Gateway Arch (JEFF) data from 1979 are for the
Jefferson National Expansion Memorial.

All values are estimates built from counts. The FAQ says "Counts can be
automated, such as with traffic counters, door counters, or trail counters,
or they can be done manually by hand counting." In parks with roads, "often
just the number of vehicles is counted. Vehicle counts are combined with
person-per-vehicle multipliers to estimate the number of visits." The
multipliers "can vary by park, by location within a park, by time of year,
and by type of vehicle." Counts from one area can be used to estimate visits
to remote areas "where needed and appropriate." The per-park "Visitor Use
Counting and Reporting Instructions" spell this out: which counter, how the
count is divided (often by 2 for entering and leaving), how many staff
vehicles are taken off each month, and the persons-per-vehicle multiplier.
For example, Arches multiplies its adjusted traffic count by "2.4 persons per
vehicle September through January or 2.9 persons per vehicle February through
August" (instructions dated January 2024). Many instructions also say how to
fill days when a counter is broken: under 14 days out, use the month's own
average daily traffic; 14 or more days out, use a historic monthly value from
a table in the instructions (Arches, Great Smoky Mountains, Hawaiʻi
Volcanoes).

The publisher does not report what share of each value comes from a direct
count, a multiplier, or a fill-in. Park comments (see Missing data) show that
fill-ins are common: 5-year averages, last year's numbers, or a share of
another counter.

**Changes over time.** Each park works under its own instructions. The NPS
says they "are applicable beginning January 1 of the year of issue (except for
newly added parks) and remain in effect until and unless they are changed by
agreement between the park's superintendent and the Social Science Program"
([program page](https://www.nps.gov/subjects/socialscience/visitor-use-statistics.htm)).
The NPS warns that a change "can result in trend shift in the years following
a change" ([data page](https://www.nps.gov/subjects/socialscience/visitor-use-statistics-dashboard.htm)).

Changes are flagged per park and per year in two places:

- The IRMA report "Park Visitor Use and Count Procedure Changes" lists, for
  each set of instructions, a level (Overhaul, Major, Minor, Non-material) and
  one line per change. `config/visit_method_changes.json` is built from it by
  script: 301 park-years with at least one listed change, across 61 parks.
  Big Bend and American Samoa list no described change. The PDF of every set
  of instructions is also on the park's IRMA page ("Visitor Use Counting
  Instructions"); we downloaded all 362 PDFs for the 63 parks. Each is dated
  on its first page, mostly "January <year>".
- The Statistical Abstract endnotes list each year's count procedure changes
  and closures by park, and an "Errors in previous years" list.

The change years and the document periods mostly agree. Exceptions: the
change report lists Rocky Mountain 2021 and Mount Rainier 1995 and 1996, which
are not start years in the document list; Yellowstone has a "2022 - Present"
row with no details; and the Katmai "2024 - Present" PDF is dated January 2021
on its first page. 32 parks have early document periods (mostly before 2000)
with no described change.

Count procedure changes since 2015 that fall in a year when a park's
recreation visits changed by 20 percent or more from the year before (from
our annual file). This shows timing only. Many of these years also had
closures, fires, or the pandemic, and the data do not say how much of each
change comes from the new method.

| Park | Year | Change in rec. visits | Listed change (short) |
|---|---|---|---|
| ACAD | 2021 | +52% | Major: missing-day method and historic traffic values at Sand Beach |
| BISC | 2019 | +51% | Major: manual visitor center counts replaced by a traffic counter |
| BRCA | 2015 | +22% | Minor: fixed estimate for non-recreation vehicles on Utah 12 |
| DENA | 2021 | +318% | Minor: removed winter/summer split; corrected length of stay |
| DEVA | 2018 | +30% | Major: added Daylight Pass Road and Saline Valley Road visits |
| DRTO | 2019, 2021 | +39%, +73% | Minor: changed length of stay; added private boat estimate from online passes |
| EVER | 2018 to 2021 | -41%, +87%, -37%, +34% | Major/Overhaul each year: entrance counting moved from manual to traffic counter, counter moved, divisor changed |
| GRTE | 2022 | -28% | Major: campground and roadside camping changes |
| HAVO | 2022 | +25% | Major: new entrance counter and monthly adjustments |
| INDU | 2017 | +27% | Minor: count description and non-reportable changes |
| ISRO | 2016 | +34% | Major: boat and visitor center counting changes |
| JEFF | 2020, 2023 | -76%, +50% | Overhaul: counted at security instead of ramps; Major: grounds multiplier 0.25 to 1.1 |
| KATM | 2021 | -52% | Major: simplified method using visitor access categories |
| KEFJ | 2021 | +255% | Overhaul: traffic classifier and vehicle-class multipliers at Exit Glacier |
| KOVA | 2025 | -55% | Overhaul: new estimate from base visits plus guided clients |
| LACL | 2021 | +269% | Major: estimate from guide and concession reports |
| MACA | 2020, 2021 | -47%, +78% | Major/Minor: private canoe and kayak estimate changed |
| NERI | 2021 | +60% | Major: added traffic counters at Kaymoor and Long Point |
| PEFO | 2020 | -40% | Major: updated persons-per-vehicle multipliers |
| REDW | 2021, 2025 | +64%, +93% | Major: new counter technology; Overhaul: new four-counter system |
| ROMO | 2021 | +34% | Minor: removed Grand Lake snowmobile estimate |
| SAGU | 2021 | +42% | Major: trail registers replaced by trail counters |
| SEQU | 2024 | +34% | Minor: built-in estimates replace two traffic counts |
| VIIS | 2022 | -39% | Minor: removed Trunk Bay lifeguard counts and other counts |
| WHSA | 2020 | -32% | Major: calculations moved into IRMA |

Six parks have new instructions dated 2026 (ARCH, CANY, GAAR, HAVO, VIIS,
YOSE), so their preliminary 2026 months use a different method from 2025.

Unit names and types also change: 26 of the 63 units became national parks in
1978 or later, and some were renamed (Lafayette to Acadia, Mt. McKinley to
Denali, General Grant to Kings Canyon). The REST service returns only the
current name for every year. `config/designations.json` has the year each
unit became a national park, with sources.

**Suppressed, censored or masked values.** None documented. Values are whole
numbers with no suppression codes.

**Missing data.** The REST service has no missing-value code. A month with no
report is simply absent. Inside each park's range we found:

- Katmai (KATM): all of 1996 absent.
- American Samoa (NPSA): all of 2004 and 2005 absent.
- Channel Islands (CHIS): December 2005 absent, so 2005 has 11 months.

The published annual report shows the same gaps (no KATM 1996 row, no NPSA
2004 or 2005 row). We leave these gaps as gaps.

A zero is a published value, not a missing one. 409 park-months from 1979 to
2025 have zero recreation visits, mostly in Alaska parks in winter (Katmai 97,
Gates of the Arctic 83) and Isle Royale (68). In 2020, 46
park-months are zero, mostly April and May.

Closures and shutdowns are reported by each park in its own way. The
publisher does not apply one rule. The optional "Monthly Visitation Comments
By Park" report (comments start in 2003 or 2004 for most parks) shows what
parks did:

- October 1 to 16, 2013: many parks closed. Comments say visits were low or
  zero during the closure (Yellowstone: "between Oct 1-16 there were no
  recreational visitor entries"). Sequoia used 3-year averages "multiplied by
  .50 to represent shutdown."
- December 22, 2018 to January 25, 2019: many parks stayed partly open with no
  staff at entrances. Comments describe fill-ins: 5-year averages (Everglades,
  Theodore Roosevelt, Voyageurs), splitting a two-month count in half (Great
  Sand Dunes), and estimates from last year (Bryce Canyon, Wind Cave). Zion:
  "ALL THESE NUMBERS ARE NOT ACCURATE DUE TO GOVERNMENT SHUTDOWN FROM JANUARY
  1st - 27th." Joshua Tree: "Lapse in appropriation prevented the collection
  of accurate data."
- October 1 to November 12, 2025 (a 43-day lapse in appropriations, per the
  NPS release): the 2025 Abstract endnotes list parks "Closed" or "Partial
  closure October 1 through November 12 due to lapse in appropriations,"
  including Denali, Isle Royale, Katmai and Petrified Forest (partial or full)
  and American Samoa (closed). Park comments say bus, non-recreation and
  non-reportable inputs were estimated from 2024 data at Yellowstone and
  Arches, and Grand Canyon wrote: "Estimates made for first two weeks and
  added to official numbers."
- 2020: the 2020 Abstract says "methods for collecting and estimating visitor
  use statistics at many parks had to be altered for 2020, and that official
  statistics reported here may be more approximate than usual," and that "66
  parks in the National Park System were fully closed for two months or more."
  Its Appendix A lists pandemic closures by park.

A late value does fill in within the current year, since parks can edit
preliminary months until the year is finalized.

**Revisions.** The NPS says: "Once the calendar year is over and data for a
given year is finalized, no changes to the underlying values can be made.
Some parks' data may contain permanent errors. Errors are noted in the
Endnotes of the Annual Statistical Abstracts"
([data page](https://www.nps.gov/subjects/socialscience/visitor-use-statistics-dashboard.htm)).
So final years are not revised, even when an error is found later, and a
method change is not applied back to earlier years. Current-year months do
change until the year is final. We refresh the whole series on each run and
treat 2026 as preliminary.

Errors the Abstracts list that touch recreation visits at our 63 parks (from
the 2019 to 2025 Abstracts; hours-only and overnight-only errors left out):

- Bryce Canyon: "From 2000 through 2024, there was an error in the number of
  shuttle bus passengers entering the park from Bryce Canyon City—this caused
  reported recreation visits to be too high by approximately 18–19 percent
  each year" (2025 Abstract). IRMA still shows the uncorrected values: BRCA
  was 2,498,075 in 2024 and 1,967,367 in 2025.
- Haleakalā: "From 2007 through 2018, miscellaneous fee visits were
  incorrectly added to recreation visits" (2019 Abstract).
- Guadalupe Mountains: McKittrick Canyon traffic "should have been divided by
  two for entry and exit; unclear how long this error has existed, perhaps
  since 1992" (2019).
- Denali: Talkeetna counter "not operating correctly in summer 2017 resulting
  in a doubling of summer 2017 data at that location" (2019).
- Zion: bus passenger multipliers "switched between south entrance and east
  entrance / Kolob Canyons from 2013 through 2018" (2019).
- Lassen Volcanic: "From 2008 through 2018, non-reportable vehicles at
  southwest entrance were inadvertently omitted from calculations" (2019).
- Canyonlands: "Some bus passenger data in the past has been skewed down"
  (2019). Everglades: "Some data were missing or delayed in 2018 which
  resulted in under-reporting for the year" (2019).
- Congaree: Bannister Bridge count "should have been divided by 2 from 2012
  through 2021" (2022). New River Gorge: Sandstone Falls and Glade Creek
  "should have been divided by 2 for entry and exit, unclear how long this
  error has been occurring" (2021).
- Mount Rainier: September estimates at Mather Wye and Cayuse Pass were 100
  percent of the traffic count "from 1995 through 2022 – it should have been
  30%" (2023). Rocky Mountain: Beaver Meadows "reported too high by 12,982
  vehicles in July 2022" (2023).

Abstract PDFs: [2019](https://irma.nps.gov/DataStore/DownloadFile/637876),
[2021](https://irma.nps.gov/DataStore/DownloadFile/672277),
[2022](https://irma.nps.gov/DataStore/DownloadFile/689245),
[2023](https://irma.nps.gov/DataStore/DownloadFile/704975),
[2025](https://irma.nps.gov/DataStore/DownloadFile/759491).

**Units and rounding.** Visits (count of entries), whole numbers. The data
page notes that "data users may notice slight rounding discrepancies across
different reports." We did not find one in the final years: all 2,909
park-year sums match the annual report exactly. Preliminary months do move:
Yellowstone's January to September 2026 total was 4,360,296 in a "Monthly
Public Use" export at about 10:15 on 2026-10-22 and 4,360,300 in our run a few
hours later. Values are published to the single visit,
but they come from vehicle counts times multipliers such as 2.4, so the real
precision is much coarser than one visit.

**Known quirks.**

- Negative non-recreation values are published and kept: Capitol Reef July
  2011 (-788), Hawaiʻi Volcanoes October 2005 (-32,964), and six Mount Rainier
  months in 2002 and 2003 (-16 to -112). Recreation visits have no negatives.
- IRMA UnitName uses short forms ("Yellowstone NP") and writes "Hawaii
  Volcanoes NP" without the ʻokina. The script checks names after expanding
  the short forms and dropping apostrophes. All 63 match, and each code has
  one name across all years.
- The REST service gives HTTP 200 and an empty array for an unknown code or
  for a period with no final data, so an empty answer is not an error message.
- The current-year months come from a different report than the final years.
  The script checks that each report's "same month last year" value equals the
  REST value for that month, so the two outlets agree on 2025.
- Bryce Canyon 2000 to 2024 is too high by the publisher's own statement (see
  Revisions).
- Some monthly values are fill-ins after counter failures or shutdowns (see
  Missing data). There is no flag in the data for these months.

**Uncertainty.** The NPS gives no error bars or confidence ranges for any
park or year. Its statements about accuracy are qualitative:

- Parks "must sometimes rely on estimated data due to equipment failures,
  staffing limitations, and unforeseeable circumstances such as the COVID-19
  pandemic and natural disasters," and updating counting methods "can take a
  great deal of time and financial resources," which makes it "challenging to
  keep measurement systems completely current and accurate"
  ([data page](https://www.nps.gov/subjects/socialscience/visitor-use-statistics-dashboard.htm)).
- 2020 statistics "may be more approximate than usual" (2020 Abstract).
- Current-year data "may not be complete or controlled for quality."
- Abstracts from 2013 to 2020 say "Care has been taken to assure accuracy of
  raw data values, but a thorough analysis and interpretation of the data has
  not been completed."

**License and attribution.** NPS data are works of the U.S. federal government
and are in the public domain in the U.S. We may republish them. Credit:
"National Park Service Visitor Use Statistics (IRMA), https://irma.nps.gov/Stats/".

### Checks run

- Every one of 2,909 park-years from 1979 to 2025 in `visits_annual.csv` equals
  the published "Annual Park Recreation Visitation (1904 - Last Calendar Year)"
  report for that park (all 63 parks), with no year present on one side only
  (`scripts/check_irma_annual.py`).
- 2025 totals for the ten national parks in the NPS release of 2026-03-13
  (GRSM, ZION, YELL, GRCA, YOSE, ROMO, ACAD, GRTE, OLYM, GLAC) all match our
  annual file exactly.
- No duplicate (code, year, month). Every UnitName matches its code.
