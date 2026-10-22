# Budget

## Park base funding and staff (NPS budget justifications, "Green Books")

**What it is.** Each year the National Park Service (NPS) sends Congress a
budget justification, which NPS calls the Green Book. Each book has a table of
each park and program in the Operation of the National Park System (ONPS)
account. The table is called the "Park and Program Summary" in the FY 2010 to
FY 2021 books and the "Park and Program Table" in the FY 2022 to FY 2025
books. Each row in `data/processed/budget.csv` is one budget line in one year:

- `park_base_k`: the park's base operating funding, in thousands of dollars,
  from the book's final or actual column for that year.
- `park_base_fte`: staff paid from park base funding, counted in full-time
  equivalents (FTE).
- `total_fte`: all staff at the park, from any fund source, counted in FTE.

The book for fiscal year N reports the final or actual amount for FY N-2, so
the FY 2025 book gives FY 2023 amounts. We keep only that column. The other
columns (enacted, continuing resolution, request) are plans for later years.

Plain-word definitions, from the table footnotes:

- **Park base.** The footnote on the "Total, Park Base" line says NPS "uses
  these totals when responding to inquiries as to the amount of funding
  directly available for 'park base operations.' Items which follow this total
  also support park operations, but are managed at the Regional or Servicewide
  level" (for example, FY 2014 book, footnote 7, PDF page 199; FY 2025 book,
  footnote 4, PDF page 74). The FY 2010 book says this base funding "is under
  the direct control of the park superintendent" (PDF page 199).
- **What is not in park base.** The table covers only the ONPS account. Other
  money that a park may spend is in other accounts the books list separately,
  such as Construction, Recreation Fee Programs and Donations (FY 2025 book,
  Discretionary and Mandatory Appropriations tables, PDF pages 47 to 51). The
  notes to those tables also list Great American Outdoors Act and Inflation
  Reduction Act amounts outside ONPS (PDF page 52). The
  FY 2011 table shows American Recovery and Reinvestment Act money as one
  separate total line ($146,000K), not in park rows (PDF page 245). Lines after
  "Total, Park Base" in the same table, such as regional offices, servicewide
  programs, cyclic maintenance and repair project funds, the Servicing Human
  Resources Offices, the Major Acquisition Buying Offices, and External
  Administrative Costs (central bills such as GSA rent), are also not in any
  park's base. So a park's base is a part of what is spent at the park, not
  all of it.
- **Park base FTE vs. total FTE.** Footnote 1: park base FTE "Represents
  Full-Time Equivalents (FTE) funded from park base operating dollars."
  Footnote 2: "Total FTE shown for parks are by organization, irrespective of
  funding source. For example, some temporary positions in parks are funded
  from construction, recreation fees, etc." (FY 2025 book, PDF page 74; the
  same wording, with small changes, is in every book from FY 2011 on). An FTE
  is a count of work hours turned into full-time jobs, so two half-time
  workers count as one FTE. The books do not define FTE further.
- **Final, actual, enacted and CR.** Through the FY 2020 book the column is
  headed "Final" (FY 2010 book: "FINAL"). From the FY 2021 book it is headed
  "Actual". The footnotes describe both the same way: "The Actual amounts
  reflect presentation adjustments or shifts of funds within reprogramming
  guidelines. Amounts may vary from previously listed levels" (FY 2025 book,
  footnote 5). The FY 2023 and FY 2024 books head the column "Actual" but the
  footnote calls it "Final." Neither word appears to mean money spent. In the
  one case we checked, the FY 2025 book's FY 2023 "Actual" total for ONPS
  ($2,923,424K, PDF page 74) is the same as the FY 2024 book's FY 2023
  "Enacted" total (PDF page 64). The FY 2012 book's FY 2010 "Final" total and
  its FY 2010 "Adjusted Enacted" total are also the same ($2,261,559K, PDF page
  264). So these figures look like each park's share of the enacted
  appropriation after any approved shifts, not its spending. "Enacted" is the
  amount in the year's appropriations law. "CR" is a continuing resolution,
  a short-term law that keeps funding at about the prior year's level when no
  full-year law has passed.

**Where it comes from.** PDFs linked from
https://www.nps.gov/aboutus/budget.htm (checked 2026-10-22). FY 2010 to FY 2018
are on nps.gov (`/aboutus/upload/FY_<year>_NPS_Greenbook_508.pdf`; FY 2016 is
`FY_2016_NPS_Greenbook_508-2.pdf`). FY 2019 is a zip on nps.gov
(`FY_2019_NPS_Greenbook_508-1-1.zip`) holding one 70 MB PDF. FY 2020 to FY 2025
are on doi.gov; the URLs are in `BOOKS` in `scripts/fetch/greenbooks.py`. The
books run 387 to 675 pages and 7 MB to 70 MB. No login is needed. Cached in
`data/raw/greenbooks/fy<year>.pdf`.

**Version and vintage.** One book per fiscal year, published with the
President's budget, usually in the spring before the fiscal year starts. A
book is not revised after release. The FY 2025 link on the NPS page
(`fy2025-508-nps-greenbook_2.pdf`) is byte-for-byte the same file as
`fy2025-508-nps-greenbook.pdf` on doi.gov (checked 2026-10-22). No FY 2026
book is linked. The FY 2027 book is linked but has no park table (see
`research/availability/budget.md`).

**Coverage.** Books FY 2010 to FY 2025, which give final or actual amounts for
FY 2008 to FY 2023. No older book is linked from the NPS page. All 63 national
parks appear in all 16 books, on 62 budget lines: Sequoia and Kings Canyon
share one line in every book. Several parks share a line with other units
(see "Known quirks"). 992 rows in all: 61 lines with 16 years, plus the
Western Arctic group, which is split into two codes (12 years and 4 years).
The figures are published budget allocations, not estimates or fills.

**Changes over time.** These break straight comparisons across years.

| Book | Year of amount | Amount column as headed | FTE columns as headed | Columns in table |
|---|---|---|---|---|
| FY 2010 | FY 2008 | FY 2008 FINAL | FY08 | 10 (adds visitor use and acreage) |
| FY 2011 | FY 2009 | FY 2009 Final | FY09 | 9 |
| FY 2012 | FY 2010 | FY 2010 Final | FY 2010 | 8 |
| FY 2013 | FY 2011 | FY 2011 Final | FY 2010 (see below) | 7 |
| FY 2014 | FY 2012 | 2012 Enacted (4th column; the 3rd is the 2013 CR) | 2012 | 7 |
| FY 2015 to FY 2020 | FY 2013 to FY 2018 | Final | same year as amount | 7 |
| FY 2021 to FY 2025 | FY 2019 to FY 2023 | Actual | same year as amount | 7 |

- **FY 2014 book.** It has no "Final" column for FY 2012. Its column order is
  "2013 Full Yr. CR" then "2012 Enacted." Footnote 3 says the FY 2012 Enacted
  amounts "reflect presentation adjustments or shifts of funds within
  reprogramming guidelines, in effect, the FY 2012 Final numbers" (PDF page
  199). We use the "2012 Enacted" column for FY 2012.
- **FY 2013 book.** The FTE columns are headed "FY 2010" while the amount
  column is "FY 2011 Final." Its FTE match the FY 2012 book's FY 2010 FTE on
  only 1 of 62 lines, so they are not the same FY 2010 figures. We store them
  under FY 2011 and list the comparison in `research/budget_overlap.md`. We
  could not confirm from the book which year they are.
- **Moves between park lines and central lines.** The books describe these
  moves. We did not find park-by-park amounts for them.
  - FY 2011 and FY 2012 books: central IT billing ($9,089K in FY 2011, $6,027K
    in FY 2012) and some GSA rent money moved from the Park Support subactivity
    to External Administrative Costs (FY 2011 book PDF page 67; FY 2012 book
    PDF page 64).
  - FY 2012 to FY 2020 books: the Space Rental narrative says GSA space
    changes include "transfers of Space funding from park base to this
    centralized billing" (for example FY 2012 book PDF page 179, FY 2020 book
    PDF page 119).
  - FY 2014 book: rent money moved the other way, from External
    Administrative Costs to the Park Support subactivity (PDF page 174).
  - FY 2020 book: $3,313K of "centralized lease costs" moved from Park Support
    to External Administrative Costs (PDF page 42). This is a change to the
    FY 2020 request, so it would first show in FY 2020 amounts.
  - Human resources and contracting. The FY 2012 book describes cutting 74
    Servicing Personnel Offices to 23 Servicing Human Resources Offices (PDF
    page 37). In the tables, the "Servicing Human Resources Office" line is $0
    for FY 2010 (FY 2012 book, PDF page 261), $8,105K for FY 2011 (FY 2013
    book, PDF page 174) and $17,130K for FY 2012 (FY 2014 book, PDF page 196).
    The "Major Acquisition Buying Offices" line is $61K for FY 2010 and
    $14,567K for FY 2011 on the same pages. FY 2012 book footnote 7 says FY
    2010 and FY 2011 park lines include buying-office money at three parks,
    one of them Olympic NP ($171,000 and 2 FTE) (PDF page 264). The books we
    read do not say how much of the new central lines came out of individual
    park lines. Treat park changes between FY 2010 and FY 2012 with care.
  - FY 2020 book on: FTE for the regional HR and buying offices are counted in
    the regional office totals (FY 2020 book footnote 6, PDF page 142).
  - FY 2024 and FY 2025 books add a "Budget Realignment Based on Actuals
    Obligations" exhibit by subactivity (FY 2024 book PDF page 520; FY 2025
    book PDF page 629). It is by subactivity, not by park.
- **FY 2013.** FY 2013 amounts (FY 2015 book) are lower than FY 2012 on all
  62 lines that have both years. FY 2013 was also the year of the federal
  across-the-board cut known as sequestration. The FY 2015 table does not say
  whether or how that cut shows in its "2013 Final" column.
- **Requests in some books are not final plans.** The FY 2019 table says it
  "Does Not Reflect FY 2019 Budget Addendum" (PDF page 108). This affects only
  the request column, which we do not use.

**Suppressed, censored or masked values.** None. Bracketed numbers in the
tables are non-adds (for example, trail units shown again inside the National
Trail System total, or planned absorptions in the FY 2011 book). None of the
63 parks' amounts are bracketed.

**Missing data.** No gaps for the 63 parks in FY 2008 to FY 2023. A zero would
mean zero; none of the 63 parks have one. FY 2024 and later are missing
because no book with a park table has been published since the FY 2025 book
(see `research/availability/budget.md`). FY 2024 will not arrive late in an
old book; it would need a new one.

**Revisions.** Each later book can restate earlier years ("Amounts may vary
from previously listed levels"). Each book reports only one final or actual
year, so we have one value per (line, year) and no overlap to reconcile.
`research/budget_overlap.md` records this. We pin the 16 PDFs in
`data/raw/greenbooks/`.

**Units and rounding.** Thousands of current (nominal) dollars, as published,
not adjusted for inflation. FTE are whole numbers. Table sums may not match
totals because of rounding.

**Known quirks.**

- **Shared lines.** `config/budget_units.json` lists them.
  - `SEKI` = Sequoia and Kings Canyon NPs, one line in every book.
  - `BELA_CAKR_KOVA_NOAT` = Western Arctic National Parklands: Bering Land
    Bridge NPres, Noatak NPres, Cape Krusenstern NM and Kobuk Valley NP, books
    FY 2010 to FY 2021. From the FY 2022 book (FY 2020 amounts), Bering Land
    Bridge has its own line and the group becomes `CAKR_KOVA_NOAT`. Kobuk
    Valley's series breaks at FY 2020.
  - `KATM_ANIA_ALAG` = Katmai NP&Pres, Aniakchak NM&Pres and Alagnak Wild
    River, every book.
  - `NOCA_LACH_ROLA` = North Cascades NP, Lake Chelan NRA and Ross Lake NRA,
    every book.
- **Lines that include something besides the park.** Theodore Roosevelt NP is
  "Theodore Roosevelt NP & International Peace Garden" from the FY 2012 book
  on; before that it is "Theodore Roosevelt NP." Rocky Mountain NP is "Rocky
  Mountain NP & Cache La Poudre" (a national heritage area) in the FY 2010 and
  FY 2012 to FY 2016 books, and plain "Rocky Mountain NP" in FY 2011 and from
  FY 2017 on. These name changes may mark a change in what the line covers.
  The FY 2019 and FY 2020 tables say Everglades restoration and research FTE
  are in Everglades NP's total FTE.
- **Park and preserve on one line.** Denali, Gates of the Arctic, Glacier
  Bay, Great Sand Dunes, Katmai, Lake Clark and Wrangell-St. Elias each show
  the park and the preserve as one line ("NP & Preserve" in the FY 2010 and
  FY 2011 books, "NP&Pres" after). New River Gorge is "National River" or
  "NR" through the FY 2021 book and "NP&Pres" from FY 2022.
- **Renamed parks.** Jefferson National Expansion Memorial (books through FY
  2019) is Gateway Arch NP from FY 2020. Indiana Dunes NL becomes NP in the FY
  2020 book. White Sands NM becomes NP in the FY 2021 book. Pinnacles is "NM"
  in the FY 2010 to FY 2013 and FY 2015 to FY 2018 books and "NP" in FY 2014
  and from FY 2019 on.
- **Text extraction.** Several books print the table rotated on the page. The
  FY 2015 and FY 2018 text layers insert stray spaces inside words. The FY 2012
  text layer splits some numbers ("4, 821", "-9 3"). The FY 2018 text layer
  reads one block of three rows column by column. The script rebuilds rows
  from the position of each piece of text, joins split numbers only when the
  joined row adds up (request = base + changes), and checks that every row for
  the 63 parks adds up. A second parse from the plain text layer agreed on 991
  of 992 rows; the one difference (Biscayne NP, FY 2018 book) was checked
  against the rendered page.

**Uncertainty.** The books give no error bars. The amounts are allocations,
so they are exact as published, but they may not match what a park spent. FTE
are rounded to whole numbers.

**License and attribution.** U.S. government work, public domain. Credit:
"National Park Service, Budget Justifications (Green Books), FY 2010 to FY
2025."
