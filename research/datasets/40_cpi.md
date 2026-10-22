# Consumer Price Index for All Urban Consumers (BLS)

**What it is.** CPI-U, all items, U.S. city average, not seasonally adjusted, series CUUR0000SA0. It is a monthly index of consumer prices, with 1982-84 = 100. We use it only to turn each fiscal year's budget into FY2025 dollars.

**Where it comes from.** The BLS Public Data API v2 (https://api.bls.gov/publicAPI/v2/timeseries/data/), pulled by `scripts/fetch/cpi.py` with the key loaded by `d4tp_env.py`. Raw responses are cached in `data/raw/bls/`. No login is needed beyond the free API key.

**Version and vintage.** We pulled it on 2026-10-22 and cover January 1978 to December 2025. The not seasonally adjusted CPI-U is not revised after release.

**Coverage.** Urban consumers, about 90% of the U.S. population according to BLS. It measures consumer prices, not the costs the Park Service pays. A budget adjusted by CPI-U shows buying power in consumer terms, which is a common choice but not the only one.

**Changes over time.** BLS updates the market basket and methods from time to time. We know of no break that affects a fiscal-year average comparison over 2008 to 2025.

**Suppressed, censored or masked values.** None.

**Missing data.** October 2025 has no value. Its BLS footnote reads: "Data unavailable due to the 2025 lapse in appropriations." Our fiscal-year averages use October to September, so FY2025 (October 2024 to September 2025) is complete. The calendar 2025 average is not computed, and we do not use it.

**Revisions.** None for this series.

**Units and rounding.** An index level to three decimals. Fiscal-year averages are kept to four decimals in `data/processed/cpi.csv`.

**Known quirks.** The federal fiscal year starts October 1, so FY2025 starts in calendar 2024.

**Uncertainty.** BLS publishes standard errors for CPI changes. They are small next to the changes shown here, and we do not show them.

**License and attribution.** U.S. government work, in the public domain. Credit: U.S. Bureau of Labor Statistics.
