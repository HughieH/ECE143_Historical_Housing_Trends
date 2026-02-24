"""
data cleaning script for Historical House Price Trends Visualizer

produces two cleaned CSV outputs for visualizations:
- output/county_growth_rates.csv (choropleth map)
- output/state_growth_rates.csv (state ranking)
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
            lambda x: x.rolling(3, min_period = 1).mean()
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

    print_summary(county_summary, state_summary, out_dir)


if __name__ == "__main__":
    main()
