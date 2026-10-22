# Availability: NPS visitor use statistics

All checks on 2026-10-22 unless noted.

## 1. Current-year (2026) months in the IRMA REST service: not available

**What it is.** Monthly recreation and non-recreation visits for January 2026
onward from the IRMA v3 REST service,
`https://irmaservices.nps.gov/v3/rest/stats/visitation`.

**Where it is absent now.**
`https://irmaservices.nps.gov/v3/rest/stats/visitation?unitCodes=YELL&startMonth=1&startYear=2026&endMonth=12&endYear=2026&format=json`
returns `[]`. The same holds for GRSM, ZION and ACAD, and for the
system-wide `https://irmaservices.nps.gov/v3/rest/stats/total/2026?format=json`.
A request for 1979 to 2026 returns data through December 2025 for all 63
parks and nothing after.

**Where the months are published.** The IRMA Stats SSRS report "Monthly
Public Use"
(`https://irma.nps.gov/Stats/SSRSReports/Park%20Specific%20Reports/Monthly%20Public%20Use?Park=YELL&RptDate=1/1/2026`)
offers report months from January 2026 through September 2026 in its date
list and returns values for each. For Yellowstone, September 2026 shows
868,450 recreation visits. The national report "Current Year Monthly and
Annual Summary Report (1979 - Present)" shows "Total Recreation Visits for Sep
2026" for every reporting park. The report for October 2026 does not render. Each park's date list
shows only the months it has posted. On 2026-10-22, 46 parks list September
2026 as the latest month, 10 list August, 3 list July (CRLA, NPSA, OLYM), 1
lists March (DENA), and 3 list no 2026 month (CHIS, KATM, LACL).
The IRMA Stats home page (https://irma.nps.gov/Stats/) states: "Current
calendar year (2026) data are preliminary and subject to change. Data will be
finalized by the end of the first quarter of next calendar year (2027)." The
NPS data page states: "Current year data are preliminary and must be
thoroughly reviewed by the Social Science Program prior to being considered
final. For that reason, most data are available only through last calendar
year" (https://www.nps.gov/subjects/socialscience/visitor-use-statistics-dashboard.htm,
last updated 2026-03-26).

**Evidence that it was published before.** None found. The Wayback Machine
CDX index (queries `url=irmaservices.nps.gov/v3/rest/Stats*` and
`.../stats*`, run 2026-10-22) has captures of the service help page only,
from 2014-11-07 to 2026-05-01, and no capture of any data request. Wayback
has captures of IRMA SSRS report pages in 2026, but these are page shells; the
numbers load later inside a frame and are not in the captures. We could not
check whether the REST service ever returned current-year months.

**What we did.** `scripts/fetch/irma_visits.py` takes January through
September 2026 (as each park has posted them) from "Monthly Public Use" and marks them as preliminary in the
docs. `--final-only` leaves them out.

## 2. IRMA v2 unit service: no longer published

**What it is.** The IRMA v2 unit REST service, `https://irmaservices.nps.gov/v2/rest/unit/`,
which listed NPS units with code, name, full name and designation.

**Last published.** Wayback capture of 2025-05-06 returns unit data
(`ArrayOfUnitProfile` XML starting with ABLI, Abraham Lincoln Birthplace):
https://web.archive.org/web/20250506045445/https://irmaservices.nps.gov/v2/rest/unit/.
Earlier captures with HTTP 200 go back to 2014-11-08. The service help page
was captured with its list of operations on 2025-07-08:
https://web.archive.org/web/20250708101048/https://irmaservices.nps.gov/v2/rest/unit/help.

**Absent now.** On 2026-10-22, `https://irmaservices.nps.gov/v2/rest/unit/`
returns HTTP 503 with the text "This IRMA application is nolonger available,
We apologize for the inconvenience." Recorded as a retired API version.

## 3. Months missing inside a park's IRMA history: not available

**What it is.** Monthly visits for Katmai (KATM) January to December 1996,
National Park of American Samoa (NPSA) January 2004 to December 2005, and
Channel Islands (CHIS) December 2005.

**Absent now.** Not returned by the REST service. The published "Annual Park
Recreation Visitation (1904 - Last Calendar Year)" report has no KATM 1996
row and no NPSA 2004 or 2005 row, and its CHIS 2005 total equals the sum of
the 11 months returned.

**Evidence of earlier publication.** None found. Labeled "not available."

## 4. Monthly data before 1979: not available

**What it is.** Monthly visits before January 1979.

**Statement.** The NPS data page says annual recreation visits are available
from 1904 and monthly values "for the 11 official statistics" from 1979, "the
year in which every park unit began reporting monthly data for all 11
statistics. Prior to that time, only annual recreation visits are consistently
available."
(https://www.nps.gov/subjects/socialscience/visitor-use-statistics-dashboard.htm)

## 5. Park inputs and intermediate calculations: not available in reports

**What it is.** The counts and adjustments that feed each park's monthly
totals (for example raw traffic counts and multipliers applied).

**Statement.** The FAQ says inputs and intermediate calculations "are
available from the early 1990s to present, but usually are not available in
summary reports and must be requested separately"
(https://www.nps.gov/subjects/socialscience/statistics-faq.htm, last updated
2026-03-26).

## Published on the usual schedule (for the record)

- 2025 annual totals: NPS news release dated 2026-03-13,
  https://www.nps.gov/orgs/1207/03-13-26-2025-visitation-statsitics.htm
  (323,014,305 recreation visits). The NPS says annual statistics "are
  released during the first quarter of the following calendar year."
- "NPS Visitor Use Statistics Data Package, 2025" (1979 to 2025), issued
  2026-03-26:
  https://catalog.data.gov/dataset/nps-visitor-use-statistics-data-package-2025.
- Statistical Abstract 2025, date of issue June 2026 in the IRMA list
  (https://irma.nps.gov/Stats/Reports/AbstractsAndForecasts), PDF at
  https://irma.nps.gov/DataStore/DownloadFile/759491. On 2026-10-22 the NPS
  data page still links the 2024 Abstract as the one to download.
