# Historical House Price Trends Visualizer

An animated visualization of U.S. real estate price growth rates from approximately 1985–2024, combining animated state rankings with county-level choropleth maps. Data sourced from the [FHFA House Price Index (HPI)](https://www.fhfa.gov/data/hpi).

[Link to Project Doc](https://docs.google.com/document/d/1YSsB1MgWivRdj0NZkEdz1WsyvrbjEVrToSkB1Ts24Ko/edit?usp=sharing)

## State Level Choropleth Animation

https://github.com/user-attachments/assets/3a7a76e2-3d75-40b5-8814-d5afb7df3db6

## Bar Chart Race (HPI by State over Time)

An interactive bar chart race showing HPI rankings across all 51 U.S. states from 1975 to 2025, broken down by quarter.

[View Interactive Bar Chart Race](https://public.flourish.studio/visualisation/27943328/)

The input data was reformatted from the raw FHFA HPI CSV into a wide format suitable for Flourish using `src/HPI_to_race.py`.

## ARIMA Forecast Model

We use an **ARIMA** (AutoRegressive Integrated Moving Average) model to forecast HPI 10 years into the future for all 51 U.S. states. The implementation uses `pmdarima.auto_arima` to automatically select the best (p, d, q) order for each state via AIC minimization.

- **Training**: Fit on historical HPI data per state
- **Evaluation**: 5-year holdout (2020–2024) with MAE, RMSE, and MAPE metrics
- **Forecast**: 10-year ahead predictions (2025–2034) with 95% confidence intervals
- **Visualizations**: Single/multi-state forecast plots, choropleth maps, animated choropleth, and error analysis

See `notebooks/visualizations.ipynb` for all visualizations and `src/prediction.py` for the model code.

## File Structure

```
project/
├── data/
│   ├── raw/                        # raw data files (see data/README.md for sources)
│   └── README.md                   # description of raw data sources
├── output/
│   ├── county_growth_rates.csv     # county HPI with FIPS, year, annual change
│   ├── state_growth_rates.csv      # state year-on-year and 3-year rolling growth
│   ├── hpi_bar_chart_race.csv      # wide-format HPI for Flourish bar chart race
│   ├── state_fastest_growth.csv    # state 5yr/10yr fastest growth rankings
│   ├── county_fastest_growth.csv   # county 5yr/10yr fastest growth rankings
│   ├── state_growth_rates_choropleth_animation.mp4
│   └── state_growth_rates_over_3_yrs_choropleth_animation.mp4
├── notebooks/
│   ├── visualizations.ipynb        # main notebook — all visualizations for the presentation
│   ├── state_level_choropleth.ipynb
│   ├── fastest_growth_visualizations.ipynb
│   └── hpi_prediction.ipynb
├── src/
│   ├── data_cleaning.py            # data cleaning & CSV generation
│   ├── HPI_to_race.py              # data processing for bar chart race
│   ├── prediction.py               # ARIMA forecasting module
│   ├── plot_utils.py               # visualization utilities for ARIMA plots
│   └── render_choropleth_to_video.py  # render choropleth frames to MP4
├── .gitignore
├── requirements.txt
├── pyproject.toml
└── README.md
```

## How to Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Or, if you have [uv](https://docs.astral.sh/uv/):
   ```bash
   uv sync
   ```

2. **Download raw data** — instructions can be found in `data/README.md`.

3. **Run data cleaning:**
   ```bash
   python src/data_cleaning.py
   ```

4. **Open the main notebook** and run all cells:
   ```
   notebooks/visualizations.ipynb
   ```
   This single notebook contains every visualization used in the presentation.

## Third-Party Modules

| Module | Purpose |
|--------|---------|
| [pandas](https://pandas.pydata.org/) | Data manipulation and CSV/Excel I/O |
| [numpy](https://numpy.org/) | Numerical operations |
| [plotly](https://plotly.com/python/) | Interactive visualizations (choropleth maps, bar charts, scatter plots) |
| [openpyxl](https://openpyxl.readthedocs.io/) | Reading `.xlsx` Excel files |
| [lxml](https://lxml.de/) | HTML table parsing (used by `pd.read_html`) |
| [kaleido](https://github.com/plotly/Kaleido) | Static image export for Plotly figures |
| [pmdarima](https://alkaline-ml.com/pmdarima/) | Auto ARIMA model selection and fitting |
| [statsmodels](https://www.statsmodels.org/) | Statistical modeling (ARIMA backend) |
| [scipy](https://scipy.org/) | Statistical tests (linear regression in error analysis) |
| [nbformat](https://nbformat.readthedocs.io/) | Jupyter notebook format utilities |

## Team

- **Andrew Park**
- **Zhengyu Huang**
- **Hou Wai Wan**
- **Tiancheng Shi**
- **Ryan Luo**
