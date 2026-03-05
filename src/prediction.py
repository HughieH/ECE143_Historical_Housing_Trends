"""
HPI prediction module using ARIMA model.

Forecasts HPI 10 years into the future for all 51 U.S. states
and evaluates performance on a 5-year holdout set.
"""

import numpy as np
import pandas as pd
from pmdarima import auto_arima


# ---------------------------------------------------------------------------
# Data Preparation
# ---------------------------------------------------------------------------

def split_train_test(df, test_years=5):
    """
    Temporal split into train and test sets.

    parameters:
        input:
            df (pd.DataFrame): full dataset with Year column
            test_years (int): number of most recent years to hold out
        output:
            tuple (train_df, test_df)
    """
    assert isinstance(df, pd.DataFrame)
    assert "Year" in df.columns
    max_year = df["Year"].max()
    cutoff = max_year - test_years
    train = df[df["Year"] <= cutoff].copy()
    test = df[df["Year"] > cutoff].copy()
    return train, test


# ---------------------------------------------------------------------------
# ARIMA Forecasting
# ---------------------------------------------------------------------------

def fit_arima_state(train_series, state_abbrev):
    """
    Fit auto_arima on a single state's HPI training series.

    parameters:
        input:
            train_series (pd.Series): HPI values ordered by year
            state_abbrev (str): state abbreviation for logging
        output:
            fitted ARIMA model
    """
    assert isinstance(train_series, pd.Series)
    model = auto_arima(
        train_series,
        seasonal=False,
        stepwise=True,
        suppress_warnings=True,
        error_action="ignore",
    )
    return model


def forecast_arima(model, n_periods=10):
    """
    Generate forecast and 95% confidence intervals from a fitted ARIMA model.

    parameters:
        input:
            model: fitted pmdarima ARIMA model
            n_periods (int): number of periods to forecast
        output:
            tuple (forecast array, confidence interval array of shape (n, 2))
    """
    forecast, conf_int = model.predict(n_periods=n_periods, return_conf_int=True)
    return np.asarray(forecast), np.asarray(conf_int)


def run_arima_all_states(df, forecast_years=10, test_years=5):
    """
    Fit ARIMA for all states and return forecasts + evaluation data.

    parameters:
        input:
            df (pd.DataFrame): full HPI dataset from prepare_state_hpi
            forecast_years (int): years to forecast after full data
            test_years (int): holdout years for evaluation
        output:
            tuple (forecast_df, eval_df, models_dict)
    """
    assert isinstance(df, pd.DataFrame)
    train_df, test_df = split_train_test(df, test_years=test_years)
    max_year = df["Year"].max()
    states = df["Abbreviation"].unique()

    eval_rows = []
    forecast_rows = []
    models = {}

    for state in states:
        state_train = train_df[train_df["Abbreviation"] == state].sort_values("Year")
        state_test = test_df[test_df["Abbreviation"] == state].sort_values("Year")
        state_full = df[df["Abbreviation"] == state].sort_values("Year")
        state_name = state_full["State"].iloc[0]

        # fit on train, predict test period for evaluation
        model_eval = fit_arima_state(state_train["HPI"], state)
        test_pred, test_ci = forecast_arima(model_eval, n_periods=test_years)

        for i, (_, row) in enumerate(state_test.iterrows()):
            eval_rows.append({
                "Abbreviation": state,
                "State": state_name,
                "Year": int(row["Year"]),
                "Actual": row["HPI"],
                "Predicted": test_pred[i],
                "CI_Lower": test_ci[i, 0],
                "CI_Upper": test_ci[i, 1],
            })

        # refit on full data, forecast into future
        model_full = fit_arima_state(state_full["HPI"], state)
        future_pred, future_ci = forecast_arima(model_full, n_periods=forecast_years)
        models[state] = model_full

        for i in range(forecast_years):
            forecast_rows.append({
                "Abbreviation": state,
                "State": state_name,
                "Year": max_year + 1 + i,
                "Predicted": future_pred[i],
                "CI_Lower": future_ci[i, 0],
                "CI_Upper": future_ci[i, 1],
            })

    eval_df = pd.DataFrame(eval_rows)
    forecast_df = pd.DataFrame(forecast_rows)
    return forecast_df, eval_df, models


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def compute_metrics(eval_df):
    """
    Compute MAE, RMSE, and MAPE per state from evaluation DataFrame.

    parameters:
        input:
            eval_df (pd.DataFrame): with columns [Abbreviation, Actual, Predicted]
        output:
            pd.DataFrame with columns [Abbreviation, State, MAE, RMSE, MAPE]
    """
    assert isinstance(eval_df, pd.DataFrame)
    metrics = []
    for state, group in eval_df.groupby("Abbreviation"):
        actual = group["Actual"].values
        predicted = group["Predicted"].values
        mae = np.mean(np.abs(actual - predicted))
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        metrics.append({
            "Abbreviation": state,
            "State": group["State"].iloc[0],
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "MAPE": round(mape, 2),
        })
    return pd.DataFrame(metrics).sort_values("MAPE")
