# Deferred maintenance: overlapping copies

Written by `scripts/fetch/deferred_maintenance.py` on 2026-10-22.

Rule: when two copies give a value for the same unit and fiscal year, the build keeps the most
recent copy (latest capture date; on a tie, the more precise copy). A rounded copy, such as a
fact sheet that prints "$138 M", counts as a disagreement only when the other value falls
outside its rounding range.

## Copies compared

| Fiscal year | Source | Copies | Units |
|---|---|---|---|
| 2014 | nps_state_park_pdf | 2 | 62 |
| 2015 | nps_state_park_pdf | 2 | 62 |
| 2016 | nps_state_park_pdf | 1 | 62 |
| 2017 | nps_state_park_pdf | 3 | 62 |
| 2018 | nps_state_park_pdf | 5 | 62 |
| 2022 | nps_park_dataset | 7 | 62 |
| 2023 | crs_r48136_table4 | 1 | 8 |
| 2024 | nps_factsheet | 44 | 24 |
| 2025 | doi_unit_xlsx | 1 | 62 |
| 2025 | nps_factsheet | 80 | 61 |

## Differences

None. Every overlapping copy agrees within rounding.

## Not written: FY2022 Quarter 1 snapshot

The first version of the NPS park dataset (captured 2022-06-12) holds a Fiscal Year 2022 Quarter 1
snapshot (national total $21.8 billion). It is not a fiscal-year-end figure, so it is not written to
the processed file. Values for our units, for the record:

| Unit | FY2022 Q1 snapshot | Source |
|---|---|---|
| ACAD | 133,845,728 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| ARCH | 8,434,823 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| BADL | 61,453,997 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| BIBE | 126,818,781 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| BISC | 75,649,043 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| BLCA | 11,750,010 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| BRCA | 13,889,028 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| CANY | 51,182,120 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| CARE | 19,681,880 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| CAVE | 52,623,266 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| CHIS | 90,464,294 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| CONG | 22,756,473 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| CRLA | 164,120,041 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| CUVA | 188,714,474 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| DENA | 52,053,672 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| DEVA | 213,685,666 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| DRTO | 135,705,585 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| EVER | 224,882,246 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| GAAR | 562,957 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| GLAC | 99,286,330 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| GLBA | 22,799,755 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| GRBA | 21,627,510 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| GRCA | 939,596,858 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| GRSA | 7,922,066 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| GRSM | 245,474,989 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| GRTE | 148,993,303 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| GUMO | 46,079,969 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| HALE | 74,397,758 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| HAVO | 208,451,197 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| HOSP | 28,540,369 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| INDU | 44,115,027 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| ISRO | 56,971,407 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| JEFF | 37,748,944 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| JOTR | 104,514,025 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| KATM | 5,557,415 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| KEFJ | 1,165,597 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| LACL | 3,525,132 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| LAVO | 63,039,904 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| MACA | 67,096,725 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| MEVE | 121,042,352 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| MORA | 230,191,193 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| NERI | 75,723,817 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| NOCA | 46,928,076 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| NPSA | 407,728 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| OLYM | 183,142,774 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| PEFO | 88,780,982 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| PINN | 30,655,772 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| REDW | 202,347,538 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| ROMO | 117,751,001 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| SAGU | 51,346,957 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| SEKI | 184,379,962 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| SHEN | 134,843,664 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| THRO | 71,885,373 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| VIIS | 79,278,365 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| VOYA | 23,081,050 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| WEAR | 817,129 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| WHSA | 6,309,846 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| WICA | 18,248,043 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| WRST | 65,820,829 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| YELL | 929,376,036 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| YOSE | 1,041,651,425 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |
| ZION | 57,618,512 | https://web.archive.org/web/20220612201140/https://www.nps.gov/common/uploads/sortable_dataset/infrastructure/9143F3CC-B3B8-3F78-2F70BE310E528B37/9143F3CC-B3B8-3F78-2F70BE310E528B37.json?_=1655064699563 |

## Total checks

| Check | Parsed | Published |
|---|---|---|
| FY2014 state-and-park PDF, sum of all rows (20150404041038) | 11,493,168,810 | 11,493,168,812 (national total line) |
| FY2014 state-and-park PDF, sum of all rows (20160509144749) | 11,493,168,810 | 11,493,168,812 (national total line) |
| FY2015 state-and-park PDF, sum of all rows (20160210170158) | 11,927,413,973 | 11,927,413,975 (national total line) |
| FY2015 state-and-park PDF, sum of all rows (20170910032008) | 11,927,413,973 | 11,927,413,975 (national total line) |
| FY2016 state-and-park PDF, sum of all rows (20181012025059) | 11,331,249,910 | 11,331,597,849 (national total line) |
| FY2017 state-and-park PDF, sum of all rows (20181012025046) | 11,606,780,399 | 11,606,780,393 (national total line) |
| FY2017 state-and-park PDF, sum of all rows (20190729211858) | 11,606,780,399 | 11,606,780,393 (national total line) |
| FY2017 state-and-park PDF, sum of all rows (20250115015239) | 11,606,780,399 | 11,606,780,393 (national total line) |
| FY2018 state-and-park PDF, sum of all rows (20190309155240) | 11,920,058,666 | 11,920,058,668 (national total line) |
| FY2018 state-and-park PDF, sum of all rows (20190810223142) | 11,920,058,666 | 11,920,058,668 (national total line) |
| FY2018 state-and-park PDF, sum of all rows (20220313025954) | 11,920,058,666 | 11,920,058,668 (national total line) |
| FY2018 state-and-park PDF, sum of all rows (20240702043033) | 11,920,058,666 | 11,920,058,668 (national total line) |
| FY2018 state-and-park PDF, sum of all rows (20241126214342) | 11,920,058,666 | 11,920,058,668 (national total line) |
| FY2022 Q1 park dataset, sum of all rows (20220612201140) | 21,831,069,988 | $21.8 billion (NPS news release, May 9, 2022) |
| FY2022 park dataset, sum of all rows (20230417023052) | 22,221,728,844 | $22.288 billion (CRS R48136, NPS-wide FY2022) |
| FY2022 park dataset, sum of all rows (20230508012203) | 22,221,728,844 | $22.288 billion (CRS R48136, NPS-wide FY2022) |
| FY2022 park dataset, sum of all rows (20240927130554) | 22,221,728,844 | $22.288 billion (CRS R48136, NPS-wide FY2022) |
| FY2022 park dataset, sum of all rows (20250129150722) | 22,221,728,844 | $22.288 billion (CRS R48136, NPS-wide FY2022) |
| FY2022 park dataset, sum of all rows (20250206063313) | 22,221,728,844 | $22.288 billion (CRS R48136, NPS-wide FY2022) |
| FY2022 park dataset, sum of all rows (20250408200949) | 22,221,728,844 | $22.288 billion (CRS R48136, NPS-wide FY2022) |
| FY2022 park dataset, sum of all rows (20250408203738) | 22,221,728,844 | $22.288 billion (CRS R48136, NPS-wide FY2022) |
| FY2025 DOI workbook, all NPS installations | 24,237,331,444 | $24,237M (nps.gov regional table, grand total) |
| FY2025 DOI workbook, NPS installations in Alaska | 288,690,194 | $289M (AKR, nps.gov regional table) |
