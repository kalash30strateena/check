def get_gender_data():
    import streamlit as st 
    import pandas as pd 
    import numpy as  np 
    from pmdarima import auto_arima #type: ignore
    import plotly.graph_objects as go
    from tabs_data.credentials import cred  # type: ignore
    engine=cred()
    
    @st.cache_data
    def get_filtered_data(indicator_list):
        """Fetch specified indicators from the database and preprocess."""
        
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
        df["year"] = pd.to_datetime(df["year"], format='%Y')
        df.set_index("year", inplace=True)
        df = df.pivot(columns="indicator_name", values="value").sort_index()
        df.fillna(method="ffill", inplace=True)
        return df

    def forecast_next_5_years(df, indicator):
        df_filtered = df[[indicator]].fillna(method="ffill")

        model = auto_arima(df_filtered, seasonal=False, suppress_warnings=True)

        forecast_years = pd.date_range(start=df.index[-1] + pd.DateOffset(years=1), periods=5, freq="YS")
        forecast_values = model.predict(n_periods=5)
        forecast_values_np=np.array(forecast_values)

        forecast_df = pd.DataFrame(forecast_values_np, index=forecast_years, columns=[indicator])
        return forecast_df

    def plot_combined_forecast(df, indicators):
        fig = go.Figure()

        color_palette = ['#9467bd', '#ff7f0e', '#2ca02c']
        color_map = {ind: color_palette[i % len(color_palette)] for i, ind in enumerate(indicators)}

        for indicator in indicators:
            if indicator in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df[indicator],
                    mode="lines+markers",
                    name=f"{indicator} - Actual",
                    line=dict(color=color_map[indicator])  
                ))

        for indicator in indicators:
            forecast_df = forecast_next_5_years(df, indicator)
            if forecast_df is not None:
                fig.add_trace(go.Scatter(
                    x=forecast_df.index,
                    y=forecast_df[indicator],
                    mode="lines",
                    name=f"{indicator} - Forecast",
                    line=dict(color=color_map[indicator], dash="dash")  
                ))
        fig.update_layout(
            title="Population Forecast for Next 5 Years",
            xaxis_title="Year",
            yaxis_title="Population Count",
            template="plotly_white"
        )
        st.plotly_chart(fig)

    gender_indicators = ["Population, total", "Population, female", "Population, male"]
    
    # require explicit selection to render
    selected_option = st.selectbox("Select Gender Indicators to view", ["-- Select --", "Show Data"])
    if selected_option == "-- Select --":
        st.info("Please select 'Show Data' to view gender population data.")
    else:
        df = get_filtered_data(gender_indicators)
        plot_combined_forecast(df, gender_indicators)