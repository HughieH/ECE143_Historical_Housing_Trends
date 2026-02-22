# Raw Data Sources

Instructions for obtaining and placing raw data files used by the Historical House Price Trends Visualizer. Place all files in `data/raw/`.

---

## 1. FHFA Housing Price Index (county-level) — `hpi_at_county.csv`

- **Source:** [FHFA HPI Datasets — Annual Data](https://www.fhfa.gov/data/hpi/datasets?tab=annual-data)
- **Columns:** State, County, FIPS code, Year, Annual Change (%), HPI, HPI with 1990 base, HPI with 2000 base

---

## 2. FHFA Housing Price Index (state-level) — `hpi_at_state.xlsx`

- Place in `data/raw/` after download
- **Source:** [FHFA HPI Datasets — Annual Data](https://www.fhfa.gov/data/hpi/datasets?tab=annual-data)
- **Columns:** State, Abbreviation, FIPS, Year, Annual Change (%), HPI, HPI with 1990 base, HPI with 2000 base

---

## 3. Redfin State Market Tracker — `state_market_tracker.tsv000`

- Place in `data/raw/` after downloading the state market tracker file (note: rename to `state_market_tracker.tsv000`)
 - **Source:** [Redfin Data Center](https://www.redfin.com/news/data-center/)
- **Note:** Supplementary data source & is not used directly in main data cleaning script

---

## 4. Real Estate Sales 2001–2018 — `real_estate_sales.csv`

- Place in `data/raw/` after downloading the state market tracker file (note: rename to `real_estate_sales.csv`)
- **Source:** [Real Estate Sales 2001-2018 — Data.gov](https://catalog.data.gov/dataset/real-estate-sales-2001-2018)
- **Columns:** Serial Number, List Year, Date Recorded, Town, Address, Assessed Value, Sale Amount, Sales Ratio, Property Type, Residential Type, Non Use Code, Assessor Remarks, OPM remarks, Location
