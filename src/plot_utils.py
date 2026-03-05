"""
Plotting utilities for HPI forecasting visualizations.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_state_forecast(state_abbrev, historical_df, forecast_df,
                        eval_df=None):
    """
    Plot a single state's historical HPI with ARIMA forecast and CIs.

    parameters:
        input:
            state_abbrev (str): state abbreviation
            historical_df (pd.DataFrame): full historical HPI data
            forecast_df (pd.DataFrame): ARIMA forecast data
            eval_df (pd.DataFrame, optional): ARIMA evaluation predictions
        output:
            plotly Figure
    """
    hist = historical_df[historical_df["Abbreviation"] == state_abbrev].sort_values("Year")
    state_name = hist["State"].iloc[0]
    last_hist_year = hist["Year"].max()
    last_hist_hpi = hist["HPI"].iloc[-1]

    fig = go.Figure()

    # identify the train/test cutoff — last year before eval period
    train_cutoff_year = last_hist_year
    train_cutoff_hpi = last_hist_hpi
    if eval_df is not None:
        ae = eval_df[eval_df["Abbreviation"] == state_abbrev].sort_values("Year")
        if len(ae) > 0:
            train_cutoff_year = ae["Year"].min() - 1
            train_cutoff_row = hist[hist["Year"] == train_cutoff_year]
            if len(train_cutoff_row) > 0:
                train_cutoff_hpi = train_cutoff_row["HPI"].iloc[0]

    # historical line
    fig.add_trace(go.Scatter(
        x=hist["Year"], y=hist["HPI"],
        mode="lines", name="Historical",
        line=dict(color="black", width=2),
    ))

    # ARIMA evaluation predictions — bridge from last train point
    if eval_df is not None:
        ae = eval_df[eval_df["Abbreviation"] == state_abbrev].sort_values("Year")
        if len(ae) > 0:
            bridge_x = pd.concat([pd.Series([train_cutoff_year]), ae["Year"]])
            bridge_y = pd.concat([pd.Series([train_cutoff_hpi]), ae["Predicted"]])
            fig.add_trace(go.Scatter(
                x=bridge_x, y=bridge_y,
                mode="lines+markers", name="ARIMA (eval)",
                line=dict(color="blue", dash="dot"),
            ))

    # ARIMA forecast — bridge from last historical point
    af = forecast_df[forecast_df["Abbreviation"] == state_abbrev].sort_values("Year")
    if len(af) > 0:
        fc_x = pd.concat([pd.Series([last_hist_year]), af["Year"]])
        fc_y = pd.concat([pd.Series([last_hist_hpi]), af["Predicted"]])
        fig.add_trace(go.Scatter(
            x=fc_x, y=fc_y,
            mode="lines+markers", name="ARIMA Forecast",
            line=dict(color="blue", width=2),
        ))
        ci_x = pd.concat([pd.Series([last_hist_year]), af["Year"], af["Year"][::-1], pd.Series([last_hist_year])])
        ci_y = pd.concat([pd.Series([last_hist_hpi]), af["CI_Upper"], af["CI_Lower"][::-1], pd.Series([last_hist_hpi])])
        fig.add_trace(go.Scatter(
            x=ci_x, y=ci_y,
            fill="toself", fillcolor="rgba(0,0,255,0.1)",
            line=dict(color="rgba(0,0,0,0)"),
            name="ARIMA 95% CI", showlegend=True,
        ))

    fig.update_layout(
        title=f"HPI Forecast: {state_name} ({state_abbrev})",
        xaxis_title="Year",
        yaxis_title="HPI",
        template="plotly_white",
        legend=dict(x=0.01, y=0.99),
        width=900, height=500,
    )
    return fig


def plot_forecast_grid(historical_df, forecast_df, eval_df=None, states=None):
    """
    Create a subplot grid of ARIMA forecast plots for representative states.

    parameters:
        input:
            historical_df (pd.DataFrame): full historical HPI data
            forecast_df (pd.DataFrame): ARIMA forecast data
            eval_df (pd.DataFrame, optional): ARIMA eval predictions
            states (list, optional): list of state abbreviations to plot
                                     (default: 6 representative states)
        output:
            plotly Figure
    """
    if states is None:
        states = ["CA", "TX", "NY", "FL", "IL", "WA"]

    n_states = len(states)
    n_cols = 3
    n_rows = (n_states + n_cols - 1) // n_cols

    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=[
            f"{s} - {historical_df[historical_df['Abbreviation'] == s]['State'].iloc[0]}"
            for s in states
        ],
    )

    for idx, state in enumerate(states):
        row = idx // n_cols + 1
        col = idx % n_cols + 1

        hist = historical_df[historical_df["Abbreviation"] == state].sort_values("Year")
        af = forecast_df[forecast_df["Abbreviation"] == state].sort_values("Year")
        last_hist_year = hist["Year"].max()
        last_hist_hpi = hist["HPI"].iloc[-1]

        show_legend = idx == 0

        # find train cutoff for eval bridge
        train_cutoff_year = last_hist_year
        train_cutoff_hpi = last_hist_hpi
        if eval_df is not None:
            ae_tmp = eval_df[eval_df["Abbreviation"] == state].sort_values("Year")
            if len(ae_tmp) > 0:
                train_cutoff_year = ae_tmp["Year"].min() - 1
                tc_row = hist[hist["Year"] == train_cutoff_year]
                if len(tc_row) > 0:
                    train_cutoff_hpi = tc_row["HPI"].iloc[0]

        fig.add_trace(go.Scatter(
            x=hist["Year"], y=hist["HPI"],
            mode="lines", name="Historical",
            line=dict(color="black", width=1.5),
            showlegend=show_legend, legendgroup="hist",
        ), row=row, col=col)

        if eval_df is not None:
            ae = eval_df[eval_df["Abbreviation"] == state].sort_values("Year")
            if len(ae) > 0:
                bx = pd.concat([pd.Series([train_cutoff_year]), ae["Year"]])
                by = pd.concat([pd.Series([train_cutoff_hpi]), ae["Predicted"]])
                fig.add_trace(go.Scatter(
                    x=bx, y=by,
                    mode="lines", name="ARIMA (eval)",
                    line=dict(color="blue", dash="dot", width=1),
                    showlegend=show_legend, legendgroup="arima_eval",
                ), row=row, col=col)

        if len(af) > 0:
            fc_x = pd.concat([pd.Series([last_hist_year]), af["Year"]])
            fc_y = pd.concat([pd.Series([last_hist_hpi]), af["Predicted"]])
            fig.add_trace(go.Scatter(
                x=fc_x, y=fc_y,
                mode="lines", name="ARIMA Forecast",
                line=dict(color="blue", width=2),
                showlegend=show_legend, legendgroup="arima",
            ), row=row, col=col)

    fig.update_layout(
        title="ARIMA HPI Forecast (Selected States)",
        template="plotly_white",
        height=300 * n_rows, width=1100,
        legend=dict(x=0.01, y=1.02, orientation="h"),
    )
    return fig


def plot_forecast_choropleth(forecast_df, year):
    """
    Choropleth map of ARIMA predicted HPI for a given year.

    parameters:
        input:
            forecast_df (pd.DataFrame): forecast data with Abbreviation, Year, Predicted
            year (int): year to visualize
        output:
            plotly Figure
    """
    year_data = forecast_df[forecast_df["Year"] == year].copy()

    fig = px.choropleth(
        year_data,
        locations="Abbreviation",
        locationmode="USA-states",
        color="Predicted",
        color_continuous_scale="RdYlGn",
        scope="usa",
        title=f"ARIMA Predicted HPI — {year}",
        labels={"Predicted": "HPI"},
    )
    fig.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        template="plotly_white",
        width=900, height=500,
    )
    return fig


def plot_forecast_choropleth_animated(historical_df, forecast_df, history_years=5):
    """
    Animated choropleth combining recent history and ARIMA forecast years.

    parameters:
        input:
            historical_df (pd.DataFrame): full historical data
            forecast_df (pd.DataFrame): ARIMA forecast data
            history_years (int): number of recent historical years to include
        output:
            plotly Figure
    """
    max_hist_year = historical_df["Year"].max()
    recent = historical_df[
        historical_df["Year"] > max_hist_year - history_years
    ][["Abbreviation", "State", "Year", "HPI"]].copy()
    recent = recent.rename(columns={"HPI": "Predicted"})
    recent["Type"] = "Historical"

    fc = forecast_df.copy()
    fc["Type"] = "Forecast"

    combined = pd.concat([recent, fc[["Abbreviation", "State", "Year", "Predicted", "Type"]]],
                         ignore_index=True)
    combined = combined.sort_values(["Year", "Abbreviation"])

    # compute global color range
    vmin = combined["Predicted"].min() * 0.95
    vmax = combined["Predicted"].max() * 1.05

    fig = px.choropleth(
        combined,
        locations="Abbreviation",
        locationmode="USA-states",
        color="Predicted",
        animation_frame="Year",
        color_continuous_scale="RdYlGn",
        range_color=[vmin, vmax],
        scope="usa",
        title="ARIMA HPI: Recent History + Forecast",
        labels={"Predicted": "HPI"},
    )
    fig.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        template="plotly_white",
        width=900, height=550,
    )
    return fig


def plot_metrics_bar(metrics_df, metric="MAPE", top_n=20):
    """
    Bar chart of ARIMA evaluation metrics by state.

    parameters:
        input:
            metrics_df (pd.DataFrame): output of compute_metrics()
            metric (str): metric to plot (MAE, RMSE, or MAPE)
            top_n (int): number of states to show (sorted descending)
        output:
            plotly Figure
    """
    plot_df = metrics_df.sort_values(metric, ascending=False).head(top_n)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=plot_df["Abbreviation"],
        y=plot_df[metric],
        name="ARIMA",
        marker_color="blue",
    ))
    fig.update_layout(
        title=f"ARIMA {metric} by State (Top {top_n})",
        xaxis_title="State",
        yaxis_title=metric,
        template="plotly_white",
        width=1000, height=500,
    )
    return fig
