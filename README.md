# Historical House Price Trends Visualizer

An animated visualization of U.S. real estate price growth rates from approximately 1985–2024, combining animated state rankings with county-level choropleth maps.

[Link to Project Doc](https://docs.google.com/document/d/1YSsB1MgWivRdj0NZkEdz1WsyvrbjEVrToSkB1Ts24Ko/edit?usp=sharing)

## File Structure

```
project/
├── data/
│   ├── raw/                        # raw data files (real estate sales not included due to size)
│   └── README.md                   # description of raw data
├── output/
│   └── (cleaned files: county_growth_rates.csv, state_growth_rates.csv)
├── notebooks/
│   ├── exploration.ipynb
│   ├── choropleth.ipynb
│   └── price_trends_1year_chropleth.ipynb
├── src/
│   └── data_cleaning.py            # data cleaning script
├── .gitignore
├── requirements.txt
└── README.md
```

## How to Run

1. **Install dependencies:** `pip install -r requirements.txt` or `uv sync` if you have `uv`.
2. **Download raw data** instructions can be found in `data/README.md`
3. **Run data cleaning:** `data_cleaning.py`
4. **Run notebooks** in `notebooks/` for choropleth and state ranking visualizations

## Output Files

- **`output/county_growth_rates.csv`**: County level HPI with FIPS, year, and annual change. Used in choropleth map notebooks (`choropleth.ipynb`, `price_trends_1year_chropleth.ipynb`)
- **`output/state_growth_rates.csv`**: State level year on yar growth and 3 year rolling average. Used in state ranking visualization

## Team

- **Andrew Park**
- **Zhengyu Huang**
- **Hou Wai Wan**
- **Tiancheng Shi**
- **Ryan Luo**
