# Historical House Price Trends Visualizer

An animated visualization of U.S. real estate price growth rates from approximately 1985–2024, combining animated state rankings with county-level choropleth maps.

[Link to Project Doc](https://docs.google.com/document/d/1YSsB1MgWivRdj0NZkEdz1WsyvrbjEVrToSkB1Ts24Ko/edit?usp=sharing)

## State Level Chloropath Animation

https://github.com/user-attachments/assets/3a7a76e2-3d75-40b5-8814-d5afb7df3db6

## ARIMA Forecast Model

We use an **ARIMA** (AutoRegressive Integrated Moving Average) model to forecast HPI 10 years into the future for all 51 U.S. states. The implementation uses `pmdarima.auto_arima` to automatically select the best (p, d, q) order for each state via AIC minimization.

- **Training**: Fit on historical HPI data per state
- **Evaluation**: 5-year holdout (2020–2024) with MAE, RMSE, and MAPE metrics
- **Forecast**: 10-year ahead predictions (2025–2034) with 95% confidence intervals
- **Visualizations**: Single/multi-state forecast plots, choropleth maps, animated choropleth, and error analysis

See `notebooks/hpi_prediction.ipynb` for the full analysis and `src/prediction.py` for the model code.

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
│   ├── price_trends_1year_chropleth.ipynb
│   └── hpi_prediction.ipynb        # ARIMA forecast analysis
├── src/
│   ├── data_cleaning.py            # data cleaning script
│   ├── prediction.py               # ARIMA forecasting module
│   ├── plot_utils.py               # visualization utilities
│   └── render_choropleth_to_video.py
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
