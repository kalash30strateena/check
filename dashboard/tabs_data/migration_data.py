def get_migration_data():
    import pandas as pd 
    import streamlit as st 
    import plotly.graph_objects as go
    from pmdarima import auto_arima #type: ignore
    import numpy as np
    from tabs_data.credentials import cred  # type: ignore
    engine=cred()
    
    def get_filtered_data(indicator_list):
        if len(indicator_list) == 1:
            query = f"""
            SELECT year, indicator_name, value 
            FROM health
            WHERE indicator_name = '{indicator_list[0]}'
            ORDER BY year;
            """
        else:
            query = f"""
            SELECT year, indicator_name, value 
            FROM health
            WHERE indicator_name IN {tuple(indicator_list)}
            ORDER BY year;
            """
        df = pd.read_sql(query, engine)
        df["year"] = pd.to_datetime(df["year"])
        df.set_index("year", inplace=True)
        df = df.pivot(columns="indicator_name", values="value").sort_index()
        df.fillna(method="ffill", inplace=True)
        return df

    def forecast_next_5_years(df, indicator):
        df_filtered = df[[indicator]].dropna()
        model = auto_arima(df_filtered, seasonal=False, suppress_warnings=True)
        forecast_years = pd.date_range(start=df.index[-1] + pd.DateOffset(years=1), periods=5, freq="YS")
        forecast_values = model.predict(n_periods=5)
        forecast_values_np = np.array(forecast_values)
        forecast_df = pd.DataFrame(forecast_values_np, index=forecast_years, columns=[indicator])
        return forecast_df

    def plot_all_indicators_with_forecast(df):
        for indicator in df.columns:
            forecast_df = forecast_next_5_years(df, indicator)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[indicator],
                mode="lines+markers",
                name="Actual Data",
                line=dict(color="blue")
            ))
            fig.add_trace(go.Scatter(
                x=forecast_df.index,
                y=forecast_df[indicator],
                mode="lines+markers",
                name="Forecasted Data",
                line=dict(color="red", dash="dash")
            ))
            fig.update_layout(
                title=f"{indicator} with 5 year forecast",
                xaxis_title="Year",
                yaxis_title="Value",
                template="plotly_white"
            )
            st.plotly_chart(fig, key=f"plot_{indicator}")

    # Category selection for migration indicators
    migration_indicators_options = ["-- Select a migration indicator --", "Net migration"]
    selected_migration_indicator = st.selectbox(
        "Select a Migration Indicator", migration_indicators_options, index=0, key="migration"
    )
    if selected_migration_indicator == "-- Select a migration indicator --":
        st.info("Please select a migration indicator to view migration data.")
    else:
        df = get_filtered_data([selected_migration_indicator])
        plot_all_indicators_with_forecast(df)