def get_metero_data():
    import urllib
    from sqlalchemy import create_engine
    import streamlit as st
    import plotly.graph_objects as go
    from pandas.tseries.offsets import DateOffset    
    import pandas as pd
    from xgboost import XGBRegressor
    import numpy as np
    
    from tabs_data.indexes import get_droughts_index  # type: ignore
    from tabs_data.credentials import cred # type: ignore
    
    engine = cred()
    
    # Get SPI legend HTML and color function from droughts_index module
    legend_html, get_spi_color = get_droughts_index()
    
    # Display the legend in Streamlit
    st.markdown(legend_html, unsafe_allow_html=True)
    
    # Constants
    LAG_COUNT = 5
    FORECAST_MONTHS = 3 
    
    def get_station_names(engine):
        query = """
        SELECT DISTINCT s.station_name
        FROM meterological_droughts m
        JOIN stations s ON m.station_code = s.station_code
        ORDER BY s.station_name
        """
        df = pd.read_sql(query, engine)
        return df['station_name'].tolist()

    def get_metero_data(engine, station_name):
        query = f"""
        SELECT m.monthly_date, m.value_index
        FROM meterological_droughts m
        JOIN stations s ON m.station_code = s.station_code
        WHERE s.station_name = '{station_name}'
        ORDER BY m.monthly_date
        """
        df = pd.read_sql(query, engine)
        df['monthly_date'] = pd.to_datetime(df['monthly_date'])
        df = df.sort_values('monthly_date').set_index('monthly_date')

        for lag in range(1, LAG_COUNT + 1):
            df[f'lag_{lag}'] = df['value_index'].shift(lag)
        return df.dropna()

    def train_and_forecast(df):
        feature_cols = [f'lag_{i}' for i in range(1, LAG_COUNT + 1)]
        X, y = df[feature_cols], df['value_index']

        model = XGBRegressor()
        model.fit(X, y)
        df['fitted'] = model.predict(X)

        lags = df['value_index'].iloc[-LAG_COUNT:].tolist()
        
        last_actual_date = df.index[-1]
        future_dates = []
        for i in range(1, FORECAST_MONTHS + 1):
            next_month = (last_actual_date + DateOffset(months=i)).replace(day=15)
            future_dates.append(next_month)
            
        future_forecast = []
        for _ in range(FORECAST_MONTHS):
            input_arr = np.array(lags[-LAG_COUNT:]).reshape(1, -1)
            pred = model.predict(input_arr)[0]
            future_forecast.append(pred)
            lags.append(pred)

        forecast_df = pd.DataFrame({
            'monthly_date': future_dates,
            'value_index': [np.nan]*FORECAST_MONTHS,
            'fitted': [np.nan]*FORECAST_MONTHS,
            'future_forecast': future_forecast
        }).set_index('monthly_date')

        full_df = pd.concat([df[['value_index', 'fitted']], forecast_df], axis=0)

        return full_df

    def plot_forecasts(full_df, station_name):
        fig = go.Figure()

        # Actual values (single green color)
        fig.add_trace(go.Scatter(
            x=full_df.index,
            y=full_df['value_index'],
            name="Actual",
            mode='lines+markers',
            line=dict(color='#17bf55')
        ))

        # Predicted values (single brown dashed line)
        fig.add_trace(go.Scatter(
            x=full_df.index,
            y=full_df['fitted'],
            name="Predicted",
            mode='lines+markers',
            line=dict(dash='dash', color='brown')
        ))

        # Forecast values with SPI color coding
        forecast_only = full_df[~full_df['future_forecast'].isna()]
        if not forecast_only.empty:
            # Use imported get_spi_color function to map color based on SPI thresholds
            forecast_colors = forecast_only['future_forecast'].apply(get_spi_color)

            fig.add_trace(go.Scatter(
                x=forecast_only.index,
                y=forecast_only['future_forecast'],
                name="Forecast (Next 3 Months)",
                mode='markers+lines',
                marker=dict(color=list(forecast_colors)),
                line=dict(dash='dot', color='#17bf55')  # optional connecting line among forecast points
            ))

            # Optional connecting line from last actual to first forecast point
            last_actual_date = full_df['value_index'].last_valid_index()
            last_actual_value = full_df.loc[last_actual_date, 'value_index']
            first_forecast_date = forecast_only.index[0]
            first_forecast_value = forecast_only.iloc[0]['future_forecast']
            fig.add_trace(go.Scatter(
                x=[last_actual_date, first_forecast_date],
                y=[last_actual_value, first_forecast_value],
                mode='lines',
                line=dict(dash='dot', color='#17bf55'),
                showlegend=False
            ))

        fig.update_layout(
            title=f"Value Index Forecast for {station_name}",
            xaxis_title="Date",
            yaxis_title="Value Index",
            template='plotly_white',
            width=600, height=500
        )
        return fig

    stations = get_station_names(engine)
    station_name = st.selectbox("Select a Meteorological Station:", ["-- Select a station --"] + stations, index=0)

    if station_name != "-- Select a station --":
        df = get_metero_data(engine, station_name)
        if df.empty:
            st.warning("No data available for the selected station.")
        else:
            full_df = train_and_forecast(df)
            fig = plot_forecasts(full_df, station_name)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select a station from the dropdown above to see the forecast.")
