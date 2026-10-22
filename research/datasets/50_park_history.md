# Park history

These sources feed `config/park_history.json`, a short list of dated events
for each of the 63 national parks: when each was first set aside, and when it
was established, renamed or redesignated. The page turns these into a short
summary under each park's name. `scripts/fetch/park_history.py` builds the
file. The event list for each park is picked by hand in that script. The
script stops if any quoted text is not found in the source, if a park has no
matching Index entry, or if an acreage row is missing. All downloads are
cached in `data/raw/history/`.

## The National Parks: Index 2012-2016 (National Park Service)

**What it is.** The official NPS list of every unit of the National Park
System, often called the "Red Book." Each entry gives the unit's name,
address, a short description, a history line, and acreage. The history line
lists, in plain text, when the unit was proclaimed, authorized, established,
renamed or redesignated, plus a list of boundary change dates.

**Where it comes from.** https://www.nps.gov/aboutus/upload/npindex2012-2016.pdf,
a 159-page PDF, about 6.5 MB, no login. It is linked from the NPS publications
page (https://www.nps.gov/aboutus/publications.htm). Cached as
`data/raw/history/npindex2012-2016.pdf`.

**Version and vintage.** The 2012-2016 edition. The server reports the file
was last changed on October 10, 2017. We looked for a newer edition and did
not find one. The NPS publications page links only this edition and a
2016-2017 addendum. The addendum link returned "not found" when we tried it on
October 22, 2026. It covers only units added after December 31, 2015, so it
would not change any of the 63 parks. We tried likely file names for newer
editions on nps.gov and found none. We could not reach the NPS History
eLibrary (npshistory.com) index pages we tried. A newer edition may exist that
we did not find.

**Coverage.** All 63 parks in `config/parks.json` have an entry. Events run
from 1832 (Hot Springs Reservation) to 2013 (Pinnacles). A few entries cover more than one
park or unit:
- Sequoia and Kings Canyon have separate entries, but both list the web
  address www.nps.gov/seki. The script picks each by its page and first words.
- The www.nps.gov/noca address appears on three entries: North Cascades
  National Park and two national recreation areas. Only the park entry is used.
- The www.nps.gov/grte address also appears on the John D. Rockefeller, Jr.
  Memorial Parkway entry. Only the Grand Teton entry is used.
- The park-and-preserve units (Denali, Gates of the Arctic, Glacier Bay, Great
  Sand Dunes, Katmai, Lake Clark, Wrangell-St. Elias) each have one entry with
  one history line for both parts.

**Changes over time.** Four parks changed name or type after this edition:
Gateway Arch (2018, then Jefferson National Expansion Memorial), Indiana Dunes
(2019, then a national lakeshore), White Sands (2019, then a national
monument) and New River Gorge (2020, then a national river). Those changes
come from the Recent Changes page below.

**Suppressed, censored or masked values.** None.

**Missing data.** Some entries give fewer dates than others. Isle Royale and
Virgin Islands give only an authorization date, with no separate
establishment date. For Isle Royale we added the 1940 establishment date from
another NPS document (see below). For Virgin Islands we did not find one and
left the gap. Many entries say only "a national monument" or "redesignated"
without naming the unit. In those cases the event's `name` joins the park's
name with the unit type, and `name_stated` is false. That is true for 20 of
the 142 events.

**Revisions.** The Index is reissued every few years, not revised in place. We
pin the 2012-2016 edition.

**Units and rounding.** Dates are written in the Index's own style, such as
"Feb. 26, 1919" and "March 4, 1929". We keep that as `date_text` and add an
ISO date.

**Known quirks.**
- The PDF's text layer is not clean. It drops or adds spaces inside words
  ("establis hed", "Nov . 10") and stores every hyphen as a soft hyphen, so
  line-break hyphens and real hyphens look the same. The `text` we keep is the
  source wording with those spacing and hyphen errors fixed. The script checks
  each `text` against the source with spaces and hyphens ignored, so a wrong
  word or date stops the build.
- One sentence can hold two events. Grand Teton's 1943 Jackson Hole National
  Monument and its 1950 enlargement both quote the same sentence.
- Zion has two different units named Zion National Monument (1918 and 1937),
  and Grand Canyon has two named Grand Canyon National Monument (1908 and
  1932).
- Bryce Canyon's entry says "renamed and redesignated Utah National Park June
  7, 1924" and "renamed Bryce Canyon National Park Feb. 25, 1928."
- The Index writes "Mt. McKinley National Park," "Haleakalā" with a macron,
  and "Hawai'i Volcanoes" with an okina in the heading. We do not know how the
  name was spelled in 1961, so that event uses "Hawaii Volcanoes National
  Park" and is marked `name_stated: false`.
- Kenai Fjords' Index acreage is printed as "669.983.65." We do not use Index
  acreage.

**What we left out.** Boundary change lists, wilderness dates, Biosphere
Reserve and World Heritage Site dates, Dark Sky Park dates, and El Portal
(Yosemite). We kept a boundary event only where the Index calls it out apart
from the list: Acadia's 1986 permanent boundary, Biscayne's 1980 enlargement,
Kings Canyon's 1940 renaming and enlargement, Grand Canyon's 1975
combination, Grand Teton's 1950 enlargement, Wind Cave's 1935 addition of the
game preserve, and Zion's 1956 addition of the second monument. We also kept
transfers from the U.S. Forest Service and dedication dates as `other`.

**Uncertainty.** The Index does not cite laws or proclamations. Where it
disagrees with Recent Changes, both dates are in `notes` and the event list
follows the Index.

**License and attribution.** U.S. government work, in the public domain.
Credit: National Park Service, The National Parks: Index 2012-2016.

## Recent Changes to the National Park System (National Park Service)

**What it is.** An NPS web page with tables of new units and changes to unit
designations, by date, with the law or proclamation and the NPS director at
the time.

**Where it comes from.** https://www.nps.gov/aboutus/recent-changes.htm, HTML,
no login. Cached as `data/raw/history/recent-changes.htm`.

**Version and vintage.** The page says "Last updated: September 23, 2025."
Downloaded October 22, 2026.

**Coverage.** The designation table goes back to 1994. We use it for four
events after the Index: Gateway Arch (February 22, 2018), Indiana Dunes
(February 15, 2019), White Sands (December 20, 2019) and New River Gorge
(December 27, 2020). For these, `text` joins the date, park and law cells of
the table row with " | ".

**Changes over time.** The page is edited in place. Older versions are not
posted.

**Suppressed, censored or masked values.** None.

**Missing data.** Rows before 1994 are not on the page.

**Revisions.** We keep the cached copy. A later download could differ.

**Units and rounding.** Dates are written out in full ("February 22, 2018").

**Known quirks.**
- The Gateway Arch row names the old unit "Jefferson Expansion Memorial"
  (missing "National") and cites "S. 1438" instead of a public law number.
- The Indiana Dunes row cites "P.L. 166-6" as printed.
- The New River Gorge row says "renamed from New River Gorge National River."
  We list it as `redesignated` because the unit type changed.
- Rows for other parks overlap the Index. They agree on dates for Black
  Canyon, Congaree, Cuyahoga Valley, Death Valley, Joshua Tree and Pinnacles.
  Two disagree:
  - Saguaro: the Index says "redesignated Oct. 4, 1994"; Recent Changes says
    October 14, 1994 (P.L. 103-364).
  - Great Sand Dunes: the Index gives the redesignation on Nov. 22, 2000 and
    establishment on Sept. 24, 2004; Recent Changes lists the redesignation on
    September 24, 2004 (P.L. 106-530).

**Uncertainty.** The page is a summary table. We did not check the laws
themselves.

**License and attribution.** U.S. government work, in the public domain.
Credit: National Park Service.

## Isle Royale Foundation Document Overview, 2016 (National Park Service)

**What it is.** A short NPS planning document for Isle Royale National Park.
We use one sentence from page 4: "The park was formally authorized on March 3,
1931, and was officially established on April 3, 1940." It fills the
establishment date the Index leaves out. The same source is already used in
`config/designations.json`.

**Where it comes from.**
https://www.nps.gov/isro/learn/management/upload/ISRO_Web_Accessible_Foundation_Document_Overview_2016.pdf,
cached as `data/raw/history/ISRO_Foundation_Document_Overview_2016.pdf`.

**Version and vintage.** 2016.

**License and attribution.** U.S. government work, in the public domain.
Credit: National Park Service.

## Listing of Acreage, 09/30/2026 (NPS Land Resources Division)

**What it is.** A quarterly table of acreage for every NPS unit, split by
owner: NPS fee, NPS less than fee, other federal, other public and private.
We use the "Gross Area Acres" column, which is all land inside the
authorized boundary, whoever owns it.

**Where it comes from.** The NPS acreage reports page,
https://www.nps.gov/subjects/lwcf/acreagereports.htm. The file is
https://www.nps.gov/subjects/lwcf/upload/NPS-Acreage-09-30-2026.xlsx, an Excel
workbook, no login. Cached as `data/raw/history/NPS-Acreage-09-30-2026.xlsx`.
The script reads the first sheet, "Listing of Acreage."

**Version and vintage.** As of September 30, 2026, the newest report on the
page on October 22, 2026. Reports go back to at least 2011, mostly for the
end of each quarter or year.

**Coverage.** Every unit, keyed by a shortened upper-case name ("GREAT SMOKY
MTS NP," "T ROOSEVELT NP"). There is no park code column, so the script maps
codes to row names by hand.

**Changes over time.** Gross acres change as boundaries change. Mammoth Cave
is one large case: 72,041.73 gross acres in this report (20,034.11 of them
non-federal) against 52,830.19 in the 2012-2016 Index. The reports do not say
why. The 12/31/2025 and 06/30/2026 reports we checked show the same Mammoth
Cave figure.

**Suppressed, censored or masked values.** None.

**Missing data.** None of the 63 parks is missing a row.

**Revisions.** Each quarter replaces the last. We pin 09/30/2026.

**Units and rounding.** Acres, to two decimals as published.

**Known quirks.**
- Park and preserve on separate rows: Denali, Gates of the Arctic, Glacier
  Bay, Great Sand Dunes, Katmai, Lake Clark and Wrangell-St. Elias. For these,
  `acres` is the national park row only, `acres_preserve` is the preserve
  row, and `acres_park_and_preserve` is the sum.
- New River Gorge has one combined row, "NEW RIVER GORGE NP & PRES," so its
  park and preserve parts cannot be split. `acres` is the combined figure.
- Everglades is split into "EVERGLADES NP" and "EVERGLADES EXPANSION."
  Endnote 6 says to add them for the park's total, and `acres` is that sum.
- National Park of American Samoa is all "Other Public Acres." The Index says
  the land is leased.
- Gross area includes private and other non-federal land inside the
  boundary, which is large for some parks (for example Redwood, Channel
  Islands and Voyageurs).

**Uncertainty.** NPS does not publish error bars. Two-decimal precision is
finer than the accuracy of most boundary surveys.

**License and attribution.** U.S. government work, in the public domain.
Credit: National Park Service, Land Resources Division.
