# Deferred maintenance

## NPS deferred maintenance and repairs, by park (National Park Service; Department of the Interior)

**What it is.** Deferred maintenance and repairs (DM&R) is the National Park
Service (NPS) estimate of what it would cost to fix the park facilities that
need work that was put off. NPS says DM&R "is an estimate of how much it would
cost to repair and restore deteriorating facilities to an acceptable and safe
condition," and that it "is created when routine maintenance and repairs are
delayed because of limited resources"
([NPS FAQ](https://www.nps.gov/subjects/infrastructure/faqs.htm), last updated
May 9, 2022). The Department of the Interior (DOI) uses the federal accounting
definition: "a maintenance and repair activity that was not performed when it
should have been or was scheduled to be performed but was delayed to a future
period" ([DOI DM&R page](https://www.doi.gov/deferred-maintenance-and-repair)).

DM&R counts only the cost to correct existing problems. The FY2024 and FY2025
park fact sheets say it "does not include, for example, alterations for
improved accessibility, upgrades to meet current building codes, installation
of new fire suppression systems, expansion of capacity, or annual recurring
maintenance needs." It is a snapshot of the backlog at the end of a fiscal year
(September 30), not money spent.

Each row of `data/processed/deferred_maintenance.csv` is one park and one
fiscal year: the DM&R dollars NPS (or DOI, or the Congressional Research
Service quoting NPS) published for that park's reporting unit, with the URL and
capture date of the copy we read and a note on the method in use that year.

**Where it comes from.** No single file covers all years. The script
`scripts/fetch/deferred_maintenance.py` reads five official sources:

| Fiscal years | Source | Format | Precision | Where we read it |
|---|---|---|---|---|
| 2014-2018 | NPS "Deferred Maintenance by State and Park" reports | PDF, 7 to 12 pages, about 160-300 KB | whole dollars | Wayback Machine copies of files NPS removed from nps.gov (for example [FY2018](https://web.archive.org/web/20190309155240/https://www.nps.gov/subjects/infrastructure/upload/NPS-Deferred-Maintenance-FY18-State_and_Park_2018.pdf)) |
| 2022 | NPS "DM&R Park Fact Sheets" sortable dataset | JSON and CSV behind an nps.gov table | whole dollars | Wayback copies of every version, 2023-2026 |
| 2023 | CRS Report R48136, Table 4, top 20 units "using data from NPS" | HTML | $1 million | [everycrsreport.com copy, July 25, 2024](https://www.everycrsreport.com/files/2024-07-25_R48136_b8f735eff6a455e0ad5cff787c7348b59f659b10.html) |
| 2024 | NPS park "Infrastructure Fact Sheet" PDFs | PDF, 2 pages | 2 or 3 significant figures ("$161 M") | Wayback copies; NPS has since replaced each file with the FY2025 version at the same URL |
| 2025 | DOI unit-level DM&R workbook; NPS park fact sheets | XLSX (about 1,700 rows); PDF | cents (DOI); 2 or 3 significant figures (NPS) | [DOI workbook](https://www.doi.gov/sites/default/files/documents/2026-07/gaoa-pmofy25-categorized-unit-level-dm-r.xlsx), live NPS fact sheets |

No login is needed for any of them. The current NPS page,
[Infrastructure: By the Numbers](https://www.nps.gov/subjects/plandesignconstruct/defermain.htm)
(last updated May 22, 2026), gives DM&R and location counts by region for
FY2023-FY2025 and links the FY2025 park fact sheets.

**Version and vintage.** NPS reports DM&R once a year, as of September 30.
NPS wrote in 2019-2022 that "only final, year-end figures are reported to
ensure a consistent reference point" and that it "does not report 'live' data
or update reports on request"
([2019 capture](https://web.archive.org/web/20190309155227/https://www.nps.gov/subjects/infrastructure/identifying-reporting-deferred-maintenance.htm)).
Two exceptions matter here:

- In 2022 NPS posted a park dataset labeled Fiscal Year 2022 Quarter 1 (total
  $21.8 billion, used in a [May 9, 2022 news release](https://www.nps.gov/orgs/1207/05-09-2022-dm-r.htm)).
  It is a mid-year snapshot. The build caches it but does not write it, because
  it is not a year-end figure. The values for our parks are listed in
  `research/dm_overlap.md`.
- The FY2023 NPS-wide total was first posted as $23,263 million (captured
  2024-05-01) and now reads $23,258 million on the FY2023-FY2025 history table.
  The FY2023 location count went from 71,808 to 71,805, and the Intermountain
  Region from $5,087 million to $5,082 million.

Park fact sheets are replaced in place: the URL that held the FY2024 sheet now
holds the FY2025 sheet. Earlier years survive only in archived copies.

**Coverage.** FY2014-FY2018, FY2022 and FY2025 for all 63 parks. FY2024 for
25 parks: the Wayback Machine holds an FY2024 copy of the fact sheet for only
those parks: Acadia through Dry Tortugas in alphabetical order, plus Glacier,
Grand Teton, Great Smoky Mountains, Haleakala, Rocky Mountain, Sequoia and
Kings Canyon (two rows), and Yellowstone. FY2023 values for nine of our parks appear only in CRS's top-20 table (rounded to $1 million); the build leaves them out, so no FY2023 value is shown. We found no park-level figures for FY2019, FY2020 or FY2021 from
NPS, DOI, CRS or GAO. CRS lists NPS-wide totals for those years, from "CRS
communication with NPS Office of Legislative and Congressional Affairs, July
27, 2023" ([R48136, Oct. 15, 2026](https://www.everycrsreport.com/files/2026-10-15_R48136_27b01d0b7d1a8481d148a6971daf90361ed6820d.html)).

Every value is an estimate built from asset records, not a measurement. Park
staff record asset condition in NPS software, and the software turns condition
and deficiency records into dollar estimates. The share that comes from each
method changed over time (see the next section). The DOI Office of Inspector
General found in 2023 that the data in the NPS system were "inaccurate and
unreliable," which "cast[s] doubt on the NPS' deferred maintenance
estimates," possibly "underestimating the figures in some cases and
overestimating in others" (as quoted in CRS R48136, July 25, 2024; full report:
[DOI OIG 2020-CR-066](https://www.oversight.gov/sites/default/files/oig-reports/DOI/Final-Evaluation-ReportNPS-Deferred-MaintenancePublic.pdf)).

Reporting units are not always one park:

- Sequoia and Kings Canyon are one unit (SEKI) in every source. The same SEKI
  figure is written on both the SEQU and KICA rows, and `method_note` says not
  to sum them.
- Kobuk Valley is reported inside Western Arctic National Parklands (WEAR),
  with Cape Krusenstern National Monument and Noatak National Preserve. The
  WEAR figure is written on the KOVA row and flagged.
- Eight of our parks are park-and-preserve units (Denali, Gates of the Arctic,
  Glacier Bay, Great Sand Dunes, Katmai, Lake Clark, Wrangell-St. Elias, New
  River Gorge). Every source reports each as one unit code, so the figure
  covers the park and the preserve together. We found no source that splits
  them.
- North Cascades includes Lake Chelan and Ross Lake National Recreation Areas.
  Big Bend includes the Rio Grande Wild and Scenic River. Virgin Islands
  National Park includes Virgin Islands Coral Reef National Monument in the
  FY2022 dataset. These notes come from the PDFs' unit lists and the FY2022
  dataset's "Additional Park Units Included in Calculations" column.
- Parks that cross state lines appear once per state in the PDFs
  (Yellowstone, Great Smoky Mountains) and the DOI workbook (Yellowstone,
  Great Smoky Mountains, Theodore Roosevelt). The script adds the state rows
  together.

**Changes over time.** These changes break comparisons across years. NPS and
its overseers do not agree on one date for the first change, so both readings
are given.

| First fiscal year affected | What changed | Source |
|---|---|---|
| FY2015 | DOI agencies stopped reporting a range (-15% to +25%) for industry-standard assets and moved to a single estimate. | [CRS R43997, Aug. 8, 2023](https://www.everycrsreport.com/files/2023-08-08_R43997_bf07042620da63674d52cf9af63d872a27cbd0e5.html), citing DOI's FY2014 financial report |
| FY2019 or FY2021 | NPS began adding design, compliance, construction management and project management costs to non-transportation assets. NPS says "Through 2018" it counted only construction costs ([FAQ](https://www.nps.gov/subjects/infrastructure/faqs.htm); [news release, May 9, 2022](https://www.nps.gov/orgs/1207/05-09-2022-dm-r.htm)), and CRS R43997 reads this as starting in FY2019. The DOI OIG and CRS R48136 date the change to FY2021: a "blanket" 35% markup (5% compliance, 17% design, 8% construction management, 5% project management) added about $3.7 billion of the $8.8 billion rise from FY2020 to FY2021. Roads and bridges already carried a 35% markup from the Federal Highway Administration (FHWA). | DOI OIG 2020-CR-066 (Sept. 2023); CRS R48136 |
| FY2022 | NPS moved from open work-order cost estimates to "parametric condition assessments": staff score parts of each asset 0 to 9, and a scoring tool converts the scores and the asset's replacement value into DM&R. The OIG says NPS began using it in the second quarter of FY2022 and expected full use at the end of FY2024. Concession-occupied and non-industry-standard assets stayed on work orders; FHWA assessments still cover paved roads, parking, bridges and tunnels. | DOI OIG 2020-CR-066; CRS R48136 (citing the NPS FY2024 and FY2025 budget justifications) |
| FY2023 | NPS changed which assets it counts, aligning with the Federal Real Property Profile (FRPP) it reports to the General Services Administration. The portfolio went from about 75,000 to about 72,000 assets. | CRS R48136 |
| FY2023 | FHWA's "road model update" for transportation assets "cumulatively account[s] for general inflation from recent years," and NPS says it raised paved-road DM&R 36% from FY2022 to FY2023. | CRS R48136 |
| FY2023 | From FY2023 on, NPS's own DM&R totals match DOI's. Before that, NPS figures included some concessioner-owned and other non-NPS assets that DOI's financial reports left out. | CRS R48136 (July 2024 and Oct. 2026 editions) |
| FY2025 | Assets marked for disposal (907 of 70,687 in FY2025) carry no DM&R in the total. | CRS R48136, Oct. 2026, citing the NPS FY2027 budget justification |

The data source changed too: FY2014-FY2022 figures come from the NPS Facility
Management Software System (FMSS); the FY2024 and FY2025 fact sheets say "The
data is from FRPP." Because of these changes, a rise or fall between FY2018 and
FY2022, or between FY2022 and FY2023, can reflect method as well as condition.
CRS writes that the portion of the decade's change due to methods "remains
unclear."

**Suppressed, censored or masked values.** None are suppressed. Rounding is the
masking that matters: the FY2024 and FY2025 NPS fact sheets print figures such
as "$9.6 M" or "$161 M," and CRS prints billions to three decimals. Where the
only copy is rounded, the processed file stores the rounded value and
`method_note` repeats the printed figure, for example "($161 M)."

**Missing data.** FY2019, FY2020 and FY2021 are missing for every park. FY2023
is missing for 54 of the 63 parks and FY2024 for 38. A missing row means no official park-level
figure was found, not zero. A published "$ -" or "-$" in the PDFs is a real
zero and is written as 0. The `locations` column is empty: NPS publishes
location counts by region only, not by park.

**Revisions.** NPS does not post revisions of past park figures. The one
revision we saw is the FY2023 NPS-wide and Intermountain Region totals
described above. Within each fiscal year, every archived copy we compared
agrees within rounding except as listed in `research/dm_overlap.md`. The FY2014
report exists in two dated versions (March 13 and October 20, 2015); the build
keeps the later one. We pin to the copies listed by URL and capture date in the
processed file.

**Units and rounding.** Nominal (current) US dollars of each fiscal year; NPS
does not adjust for inflation. CRS adjusts the national totals with the Bureau
of Economic Analysis price index for nondefense structures; we do not. Whole
dollars in FY2014-FY2018 and FY2022, cents in the DOI FY2025 workbook (rounded
to whole dollars here), $1 million for the CRS FY2023 values, and 2 or 3
significant figures for the FY2024 fact sheets. The whole-dollar precision is
far finer than the real accuracy, given the OIG findings above.

**Known quirks.**

- The FY2016 PDF's printed national total ($11,331,597,849) is $347,942 more
  than the sum of its own state totals. The national line matches CRS
  ($11.332 billion); the park rows are kept as printed.
- State subtotals in the PDFs can differ by a dollar or two from the sum of
  their rows, from rounding.
- The FY2022 park dataset sums to $22.222 billion, about $66 million (0.3%)
  less than the NPS-wide FY2022 figure CRS reports ($22.288 billion). The
  dataset lists parks and sites; we did not find which units account for the
  rest.
- The FY2025 fact sheet link for the National Park of American Samoa returns
  404 (2026-10-22). Its FY2025 value comes from the DOI workbook.
- The FY2022 park dataset stayed on nps.gov, unchanged, through at least May
  2026, under page text saying FY2023 numbers were "coming soon." The fact
  sheet PDFs linked from it in 2024 and 2025 (file names ending
  "-Fact-Sheet.pdf") also hold FY2022 data, rounded. They are not a separate
  year.
- Names differ by source ("Haleakal? National Park" in the DOI workbook,
  "Wrangell St Elias," "Great Sand Dunes National Monument and Preserve," "New
  River Gorge National River"). The script matches on normalized names and a
  short alias list.
- DM&R is not the same as the money needed to fix a park. NPS lists other
  needs it leaves out: annual operating maintenance, life-cycle upkeep, and
  code and accessibility upgrades.

**Uncertainty.** NPS publishes no error bars. The DOI OIG (September 2023)
found work orders that were not entered, classified or closed consistently,
which "in some cases understated and in others overstated" the estimates, and
found that NPS lacked documentation for the size of the 35% markup. The OIG
did not test the new condition-assessment method. Through FY2014 DOI reported
industry-standard assets as a range of -15% to +25%, which is a rough guide to
the spread NPS itself expected then.

**How the Great American Outdoors Act (GAOA) relates.** GAOA (P.L. 116-152,
August 4, 2020) created the National Parks and Public Land Legacy Restoration
Fund. It received up to $1.9 billion a year for FY2021-FY2025, and NPS received
70%, or up to $1.33 billion a year (CRS R48136). The fund pays for projects
that address DM&R. It does not change how DM&R is measured. When a funded
project is finished, DOI says "the associated asset records are updated to
retire, or remove, the reported DM&R" (DOI DM&R page). Many projects take
several years, so funded work may not show in a park's DM&R until later. NPS
estimated in August 2025 that the FY2021-FY2025 projects would address $4.7
billion in DM&R once complete (CRS R48136, Oct. 2026). GAOA also required DOI
to publish project lists, which is one reason the park fact sheets and the DOI
DM&R page exist. The fiscal years of GAOA funding (FY2021 on) overlap the
method changes above, so year-to-year changes cannot be split between funding
and method from these data alone.

**License and attribution.** Works of the US federal government (NPS, DOI) and
CRS reports are in the public domain. Credit: "National Park Service and US
Department of the Interior, deferred maintenance and repairs data; FY2014-FY2018
and FY2024 from archived copies at the Internet Archive Wayback Machine; FY2023
from Congressional Research Service Report R48136."
