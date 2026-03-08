"""
data cleaning script for Historical House Price Trends Visualizer

produces cleaned CSV outputs for visualizations and analysis:
- output/county_growth_rates.csv (choropleth map)
- output/state_growth_rates.csv (state ranking)
- output/state_fastest_growth.csv (state level fastest valuation growth)
- output/county_fastest_growth.csv (county level fastest valuation growth)
"""

from pathlib import Path

import pandas as pd


def get_project_paths():
    """
    resolve project root and data/output directories using pathlib

    parameters:
        input:
            none
        output:
            tuple (project_root, raw_dir, out_dir as Path objects)
    """
    project_root = Path(__file__).resolve().parent.parent
    raw_dir = project_root / "data" / "raw"
    out_dir = project_root / "output"
    return project_root, raw_dir, out_dir


def load_county_raw(raw_dir):
    """
    load county level HPI info from hpi_at_county.xlsx

    parameters:
        input:
            raw_dir (path to data/raw directory)
        output:
            pd.DataFrame (raw county HPI data)
    """
    assert isinstance(raw_dir, Path)
    assert raw_dir.is_dir()
    path = raw_dir / "hpi_at_county.xlsx"
    return pd.read_excel(path, engine = "openpyxl", header = 5)


def clean_county_fips(df):
    """
    pad FIPS code to 5 digits (e.g. 1001 -> 01001)

    parameters:
        input:
            df (dataframe with 'FIPS code' column)
        output:
            pd.DataFrame (same dataframe with FIPS code zero-padded)
    """
    assert isinstance(df, pd.DataFrame)
    assert "FIPS code" in df.columns
    df = df.copy()
    df["FIPS code"] = df["FIPS code"].astype(str).str.strip()
    df["FIPS code"] = df["FIPS code"].str.zfill(5)
    return df


def clean_county_annual_change(df):
    """
    change annual percentage change to numeric and drop rows where missing

    parameters:
        input:
            df (dataframe with annual change (%) column)
        output:
            tuple (cleaned dataframe w/ number of rows dropped)
    """
    assert isinstance(df, pd.DataFrame)
    assert "Annual Change (%)" in df.columns
    before = len(df)
    df["Annual Change (%)"] = pd.to_numeric(df["Annual Change (%)"], errors = "coerce")
    df = df.dropna(subset = ["Annual Change (%)"])
    dropped = before - len(df)
    return df, dropped


def build_county_growth_rates(raw_dir, out_dir):
    """
    create county_growth_rates.csv from hpi_at_county.xlsx

    parameters:
        input:
            raw_dir (path to data/raw directory)
            out_dir (path to output directory)
        output:
            dict (summary with counts and drop reasons)
    """
    assert isinstance(raw_dir, Path)
    assert raw_dir.is_dir()
    assert isinstance(out_dir, Path)
    summary = {"initial_rows": 0, "dropped_annual_change": 0, "dropped_missing_key": 0, "final_rows": 0}

    df = load_county_raw(raw_dir)
    summary["initial_rows"] = len(df)

    df = clean_county_fips(df)
    df, dropped_ac = clean_county_annual_change(df)
    summary["dropped_annual_change"] = dropped_ac
    if dropped_ac:
        print(f"  Dropped {dropped_ac} rows with missing or non-numeric 'Annual Change (%)'.")

    required = ["FIPS code", "State", "County", "Year"]
    before = len(df)
    df = df.dropna(subset = required)
    summary["dropped_missing_key"] = before - len(df)
    if summary["dropped_missing_key"]:
        print(f"  Dropped {summary['dropped_missing_key']} rows missing one of {required}.")

    df = df.sort_values(by = ["State", "County", "Year"])
    out_cols = ["State", "County", "FIPS code", "Year", "Annual Change (%)", "HPI"]
    df = df[out_cols]

    out_dir.mkdir(parents = True, exist_ok = True)
    out_path = out_dir / "county_growth_rates.csv"
    df.to_csv(out_path, index = False)
    summary["final_rows"] = len(df)
    print(f"  Saved {summary['final_rows']} rows to {out_path}.")
    return summary


def load_state_raw(raw_dir):
    """
    load state level HPI info from hpi_at_state.xlsx

    parameters:
        input:
            raw_dir (path to data/raw directory)
        output:
            pd.DataFrame (raw state HPI data)
    """
    assert isinstance(raw_dir, Path)
    assert raw_dir.is_dir()
    path = raw_dir / "hpi_at_state.xlsx"
    return pd.read_excel(path, engine = "openpyxl", header = 5)


def prepare_state_hpi(raw_dir):
    """
    load raw state HPI values and return a clean DataFrame

    parameters:
        input:
            raw_dir (Path to data/raw directory)
        output:
            pd.DataFrame with columns [Abbreviation, State, Year, HPI]
    """
    assert isinstance(raw_dir, Path)
    assert raw_dir.is_dir()
    df = load_state_raw(raw_dir)
    df = df.dropna(subset=["Abbreviation", "State", "Year", "HPI"])
    df["HPI"] = pd.to_numeric(df["HPI"], errors="coerce")
    df = df.dropna(subset=["HPI"])
    df["Year"] = df["Year"].astype(int)
    df = df[["Abbreviation", "State", "Year", "HPI"]].sort_values(
        by=["Abbreviation", "Year"]
    )
    return df.reset_index(drop=True)


def build_state_growth_rates(raw_dir, out_dir):
    """
    create state_growth_rates.csv from raw hpi_at_state.xlsx

    parameters:
        input:
            raw_dir (path to data/raw directory)
            out_dir (path to output directory)
        output:
            dict (summary with counts and drop reasons)
    """
    assert isinstance(raw_dir, Path)
    assert raw_dir.is_dir()
    assert isinstance(out_dir, Path)
    summary = {"initial_rows": 0, "dropped_missing": 0, "final_rows": 0}

    df = load_state_raw(raw_dir)
    summary["initial_rows"] = len(df)

    required = ["Abbreviation", "State", "Year"]
    before = len(df)
    df = df.dropna(subset = required)
    summary["dropped_missing"] = before - len(df)
    if summary["dropped_missing"]:
        print(f"  Dropped {summary['dropped_missing']} rows missing one of {required}.")

    df["Annual Change (%)"] = pd.to_numeric(df["Annual Change (%)"], errors="coerce")
    df = df.sort_values(by = ["Abbreviation", "Year"])
    df["Rolling Avg Growth Rate (3yr)"] = (
        df.groupby("Abbreviation")["Annual Change (%)"].transform(
            lambda x: x.rolling(3, min_periods=1).mean()
        )
    )

    out_cols = ["Abbreviation", "State", "Year", "Annual Change (%)", "Rolling Avg Growth Rate (3yr)"]
    df = df[out_cols]
    df = df.sort_values(by = ["Abbreviation", "Year"])
    summary["final_rows"] = len(df)

    out_dir.mkdir(parents = True, exist_ok = True)
    out_path = out_dir / "state_growth_rates.csv"
    df.to_csv(out_path, index = False)
    print(f"  Saved {summary['final_rows']} rows to {out_path}.")
    return summary


def build_state_fastest_growth(out_dir, min_years_5=3, min_years_10=5):
    """
    create state_fastest_growth.csv: state-level analysis of fastest growing valuations

    uses state_growth_rates.csv; computes average annual change over last 5 and 10 years
    per state and ranks states by those averages.

    parameters:
        input:
            out_dir (path to output directory)
            min_years_5 (minimum data points required in 5yr window, default 3)
            min_years_10 (minimum data points required in 10yr window, default 5)
        output:
            dict (summary with row count and year windows used)
    """
    assert isinstance(out_dir, Path)
    assert out_dir.is_dir()
    path = out_dir / "state_growth_rates.csv"
    assert path.exists(), "state_growth_rates.csv must be built first"
    df = pd.read_csv(path)
    df["Annual Change (%)"] = pd.to_numeric(df["Annual Change (%)"], errors="coerce")
    df = df.dropna(subset=["Abbreviation", "State", "Year", "Annual Change (%)"])
    df = df.sort_values(by=["Abbreviation", "Year"])

    max_year = int(df["Year"].max())
    window_5 = list(range(max_year - 4, max_year + 1))
    window_10 = list(range(max_year - 9, max_year + 1))

    df_5 = df[df["Year"].isin(window_5)]
    counts_5 = df_5.groupby(["Abbreviation", "State"]).size().reset_index(name="n")
    valid_5 = counts_5[counts_5["n"] >= min_years_5][["Abbreviation", "State"]]
    agg_5 = (
        df_5.merge(valid_5, on=["Abbreviation", "State"])
        .groupby(["Abbreviation", "State"], as_index=False)["Annual Change (%)"]
        .mean()
        .rename(columns={"Annual Change (%)": "Avg Annual Change (5yr) %"})
    )

    df_10 = df[df["Year"].isin(window_10)]
    counts_10 = df_10.groupby(["Abbreviation", "State"]).size().reset_index(name="n")
    valid_10 = counts_10[counts_10["n"] >= min_years_10][["Abbreviation", "State"]]
    agg_10 = (
        df_10.merge(valid_10, on=["Abbreviation", "State"])
        .groupby(["Abbreviation", "State"], as_index=False)["Annual Change (%)"]
        .mean()
        .rename(columns={"Annual Change (%)": "Avg Annual Change (10yr) %"})
    )
    merged = agg_5.merge(agg_10, on=["Abbreviation", "State"], how="outer")
    merged["Rank by 5yr Growth"] = merged["Avg Annual Change (5yr) %"].rank(ascending=False, method="min").astype("Int64")
    merged["Rank by 10yr Growth"] = merged["Avg Annual Change (10yr) %"].rank(ascending=False, method="min").astype("Int64")
    merged = merged.sort_values(by="Rank by 5yr Growth")

    out_path = out_dir / "state_fastest_growth.csv"
    merged.to_csv(out_path, index=False)
    summary = {"final_rows": len(merged), "year_end": max_year, "window_5": f"{max_year-4}-{max_year}", "window_10": f"{max_year-9}-{max_year}"}
    print(f"  Saved {summary['final_rows']} rows to {out_path} (5yr: {summary['window_5']}, 10yr: {summary['window_10']}).")
    return summary


def build_county_fastest_growth(out_dir, min_years_5=3, min_years_10=5):
    """
    create county_fastest_growth.csv: county-level analysis of fastest growing valuations

    uses county_growth_rates.csv; computes average annual change over last 5 and 10 years
    per county; ranks counties nationally and within state.

    parameters:
        input:
            out_dir (path to output directory)
            min_years_5 (minimum data points required in 5yr window, default 3)
            min_years_10 (minimum data points required in 10yr window, default 5)
        output:
            dict (summary with row count and year windows used)
    """
    assert isinstance(out_dir, Path)
    assert out_dir.is_dir()
    path = out_dir / "county_growth_rates.csv"
    assert path.exists(), "county_growth_rates.csv must be built first"
    df = pd.read_csv(path, dtype={"FIPS code": str})
    df["Annual Change (%)"] = pd.to_numeric(df["Annual Change (%)"], errors="coerce")
    df = df.dropna(subset=["State", "County", "FIPS code", "Year", "Annual Change (%)"])
    df = df.sort_values(by=["State", "County", "Year"])

    max_year = int(df["Year"].max())
    window_5 = list(range(max_year - 4, max_year + 1))
    window_10 = list(range(max_year - 9, max_year + 1))
    group_cols = ["State", "County", "FIPS code"]

    df_5 = df[df["Year"].isin(window_5)]
    counts_5 = df_5.groupby(group_cols).size().reset_index(name="n")
    valid_5 = counts_5[counts_5["n"] >= min_years_5][group_cols]
    agg_5 = (
        df_5.merge(valid_5, on=group_cols)
        .groupby(group_cols, as_index=False)["Annual Change (%)"]
        .mean()
        .rename(columns={"Annual Change (%)": "Avg Annual Change (5yr) %"})
    )

    df_10 = df[df["Year"].isin(window_10)]
    counts_10 = df_10.groupby(group_cols).size().reset_index(name="n")
    valid_10 = counts_10[counts_10["n"] >= min_years_10][group_cols]
    agg_10 = (
        df_10.merge(valid_10, on=group_cols)
        .groupby(group_cols, as_index=False)["Annual Change (%)"]
        .mean()
        .rename(columns={"Annual Change (%)": "Avg Annual Change (10yr) %"})
    )

    merged = agg_5.merge(agg_10, on=group_cols, how="outer")
    merged["Rank National (5yr)"] = merged["Avg Annual Change (5yr) %"].rank(ascending=False, method="min").astype("Int64")
    merged["Rank National (10yr)"] = merged["Avg Annual Change (10yr) %"].rank(ascending=False, method="min").astype("Int64")
    merged["Rank in State (5yr)"] = merged.groupby("State")["Avg Annual Change (5yr) %"].rank(ascending=False, method="min").astype("Int64")
    merged["Rank in State (10yr)"] = merged.groupby("State")["Avg Annual Change (10yr) %"].rank(ascending=False, method="min").astype("Int64")
    merged = merged.sort_values(by=["State", "Rank in State (5yr)"])

    out_path = out_dir / "county_fastest_growth.csv"
    merged.to_csv(out_path, index=False)
    summary = {"final_rows": len(merged), "year_end": max_year, "window_5": f"{max_year-4}-{max_year}", "window_10": f"{max_year-9}-{max_year}"}
    print(f"  Saved {summary['final_rows']} rows to {out_path} (5yr: {summary['window_5']}, 10yr: {summary['window_10']}).")
    return summary


def print_summary(county_summary, state_summary, out_dir):
    """
    print summary of row counts, year range, unique states/counties, drops

    parameters:
        input:
            county_summary (dict from build_county_growth_rates)
            state_summary (dict from build_state_growth_rates or None)
            out_dir (path to output directory)
        output:
            none
    """
    assert isinstance(out_dir, Path)
    assert out_dir.is_dir()
    county_path = out_dir / "county_growth_rates.csv"
    state_path = out_dir / "state_growth_rates.csv"

    county_df = pd.read_csv(county_path, dtype = {"FIPS code": str})

    print("\n" + "=" * 60)
    print("DATA CLEANING SUMMARY")
    print("=" * 60)
    print("\n--- county_growth_rates.csv ---")
    print(f"  Rows: {len(county_df)}")
    print(f"  Year range: {county_df['Year'].min()} – {county_df['Year'].max()}")
    print(f"  Unique states: {county_df['State'].nunique()}")
    print(f"  Unique counties (FIPS): {county_df['FIPS code'].nunique()}")
    print(f"  Rows dropped (missing Annual Change %): {county_summary['dropped_annual_change']}")
    print(f"  Rows dropped (missing key columns): {county_summary['dropped_missing_key']}")

    if state_summary is not None and state_path.exists():
        state_df = pd.read_csv(state_path)
        print("\n--- state_growth_rates.csv ---")
        print(f"  Rows: {len(state_df)}")
        print(f"  Year range: {state_df['Year'].min()} – {state_df['Year'].max()}")
        print(f"  Unique states: {state_df['Abbreviation'].nunique()}")
        print(f"  Rows dropped (missing key columns): {state_summary['dropped_missing']}")
    if (out_dir / "state_fastest_growth.csv").exists():
        sf = pd.read_csv(out_dir / "state_fastest_growth.csv")
        print("\n--- state_fastest_growth.csv ---")
        print(f"  Rows: {len(sf)} (one per state)")
    if (out_dir / "county_fastest_growth.csv").exists():
        cf = pd.read_csv(out_dir / "county_fastest_growth.csv")
        print("\n--- county_fastest_growth.csv ---")
        print(f"  Rows: {len(cf)} (one per county)")
    print("=" * 60)


def main():
    """
    run county and state cleaning pipelines and write outputs to output directory  

    parameters:
        input:
            none
        output:
            none
    """
    _, raw_dir, out_dir = get_project_paths()
    assert isinstance(raw_dir, Path)
    assert isinstance(out_dir, Path)

    if not (raw_dir / "hpi_at_county.xlsx").exists():
        raise FileNotFoundError(
            f"County data not found: {raw_dir / 'hpi_at_county.xlsx'}. "
            "Run from project root and ensure raw data is in data/raw/ per data/README.md."
        )

    print("Building county_growth_rates.csv ...")
    county_summary = build_county_growth_rates(raw_dir, out_dir)

    state_summary = None
    if (raw_dir / "hpi_at_state.xlsx").exists():
        print("\nBuilding state_growth_rates.csv ...")
        state_summary = build_state_growth_rates(raw_dir, out_dir)
    else:
        print(
            "\nSkipping state_growth_rates.csv (hpi_at_state.xlsx not found in data/raw/). "
            "Add it per data/README.md to generate state output."
        )

    print("\nBuilding fastest-growth analysis (state and county) ...")
    build_county_fastest_growth(out_dir)
    if state_summary is not None and (out_dir / "state_growth_rates.csv").exists():
        build_state_fastest_growth(out_dir)

    print_summary(county_summary, state_summary, out_dir)


if __name__ == "__main__":
    main()
