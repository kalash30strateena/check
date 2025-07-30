def get_age_data():
    import streamlit as st 
    import pandas as  pd 
    import numpy as  np 
    import plotly.graph_objects as go
    from pmdarima import auto_arima #type: ignore
    from sqlalchemy import text, bindparam  # Make sure this is imported
    
    from tabs_data.credentials import cred  # type: ignore
    engine=cred()

    @st.cache_data
    def get_filtered_data(indicator_list):
        """Fetch specified indicators from the database and preprocess."""

        if isinstance(indicator_list, str):
            indicator_list = [indicator_list]

        if not indicator_list:
            return pd.DataFrame()

        query = text("""
            SELECT year, indicator_name, value 
            FROM health
            WHERE indicator_name IN :indicators
            ORDER BY year;
        """).bindparams(bindparam("indicators", expanding=True))

        df = pd.read_sql(query, con=engine, params={"indicators": indicator_list})

        df["year"] = pd.to_datetime(df["year"], format='%Y', errors='coerce')
        df.set_index("year", inplace=True)
        df = df.pivot(columns="indicator_name", values="value").sort_index()
        df.fillna(method="ffill", inplace=True)

        return df

    def forecast_next_5_years(df, indicator):
        """Train Auto ARIMA and forecast the next 5 years for the given indicator."""
        df_filtered = df[[indicator]].dropna()

        model = auto_arima(df_filtered, seasonal=False, suppress_warnings=True)

        forecast_years = pd.date_range(start=df.index[-1] + pd.DateOffset(years=1), periods=5, freq="YS")
        forecast_values = model.predict(n_periods=5)
        forecast_values_np=np.array(forecast_values)

        forecast_df = pd.DataFrame(forecast_values_np, index=forecast_years, columns=[indicator])
        return forecast_df

    def plot_all_indicators_with_forecast(df):
        for indicator in df.columns:
            forecast_df = forecast_next_5_years(df, indicator)
            
            last_actual_year = df.index[-1]
            first_forecast_year = forecast_df.index[0]
            last_actual_value = df[indicator].iloc[-1]
            first_forecast_value = forecast_df[indicator].iloc[0]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[indicator],
                mode="lines+markers",
                name="Actual Data",
                line=dict(color="blue")
            ))
            # Bridging line (dashed)
            fig.add_trace(go.Scatter(
                x=[last_actual_year, first_forecast_year],
                y=[last_actual_value, first_forecast_value],
                mode="lines",
                showlegend=False,
                line=dict(color="red", dash="dash")
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

    categories = {
        "Population": [
            "Population ages 0-14, total",
            "Population ages 15-64, total",
            "Population ages 65 and above, total"
        ],
        "Survival": [
            "Survival to age 65, female (% of cohort)",
            "Survival to age 65, male (% of cohort)"
        ],
        "Dependency Ratio": [
            "Age dependency ratio (% of working-age population)"
        ]
    }

    st.title("Age")

    selected_category = st.selectbox("Select a category", ["-- Select a category --"] + list(categories.keys()))
    if selected_category == "-- Select a category --":
        st.info("Please select a category to view the data.")
    else:
        selected_indicators = categories[selected_category]
        df = get_filtered_data(selected_indicators)
        plot_all_indicators_with_forecast(df)