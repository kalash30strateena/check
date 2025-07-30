def get_hydro_data():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import xgboost as xgb
    import plotly.graph_objects as go

    # Database imports and credentials, adjust per your environment
    from tabs_data.credentials import cred  # type: ignore
    from tabs_data.indexes import get_droughts_index  # type: ignore

    engine = cred()

    @st.cache_data
    def fetch_hydro_data():
        query = """
        SELECT h.station_code, s.station_name, h.daily_date, h.value_index
        FROM hydrological_droughts h
        JOIN stations s ON h.station_code = s.station_code
        ORDER BY s.station_name, h.daily_date
        """
        df = pd.read_sql(query, engine)
        df['daily_date'] = pd.to_datetime(df['daily_date'], format='%d-%m-%Y')
        return df

    def create_lag_features(series, lag=7):
        df_feat = pd.DataFrame()
        for i in range(1, lag + 1):
            df_feat[f'lag_{i}'] = series.shift(i)
        df_feat['target'] = series.values
        df_feat.dropna(inplace=True)
        return df_feat

    @st.cache_data
    def train_xgb_model(ts, lags=7):
        df_train = create_lag_features(ts, lag=lags)
        X = df_train.drop('target', axis=1).values
        y = df_train['target'].values
        model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            verbosity=0,
            random_state=42
        )
        model.fit(X, y)
        return model

    def forecast_xgb(ts, model, forecast_days=8, lags=7):
        last_values = ts.values[-lags:].tolist()
        forecasts = []
        for _ in range(forecast_days):
            x_input = np.array(last_values[-lags:]).reshape(1, -1)
            pred = model.predict(x_input)[0]
            forecasts.append(pred)
            last_values.append(pred)
        last_date = ts.index[-1]
        forecast_dates = [last_date + pd.Timedelta(days=i) for i in range(1, forecast_days + 1)]
        forecast_series = pd.Series(forecasts, index=forecast_dates)
        return forecast_series

    # Load data once
    hydro_df = fetch_hydro_data()
    hydro_cities = hydro_df['station_name'].unique()

    # Get legend and color function from drought index logic
    legend_html, spi_color_func = get_droughts_index()

    # Display legend in Streamlit
    st.markdown(legend_html, unsafe_allow_html=True)

    # Station selection
    hydro_city = st.selectbox("Select a Hydrological station", hydro_cities, key="hydro_city")

    if hydro_city:
        city_df = hydro_df[hydro_df['station_name'] == hydro_city].sort_values('daily_date')
        ts = city_df.set_index('daily_date')['value_index'].astype(float)

        if len(ts) < 14:
            st.warning(f"Not enough data for {hydro_city} (need at least 14 records).")
        else:
            model_xgb = train_xgb_model(ts, lags=7)
            forecast_series = forecast_xgb(ts, model_xgb, forecast_days=8, lags=7)

            fig = go.Figure()

            # Actual data line with thick green markers
            fig.add_trace(go.Scatter(
                x=ts.index[-360:],
                y=ts.values[-360:],
                mode='lines+markers',
                name='Actual Data',
                line=dict(color='#17bf55', width=3),
            ))

            # Forecast line in brown color
            fig.add_trace(go.Scatter(
                x=forecast_series.index,
                y=forecast_series.values,
                mode='lines',
                name='Forecasted Points (Single)',
                line=dict(color='brown', width=1),
                showlegend=True
            ))

            # Forecast markers with SPI color coding, connected by dashed black line
            forecast_colors = [spi_color_func(val) for val in forecast_series.values]
            fig.add_trace(go.Scatter(
                x=forecast_series.index,
                y=forecast_series.values,
                mode='lines+markers',
                name='8-Day XGBoost Forecast (SPI Colored)',
                line=dict(color='black', dash='dash', width=1),
                marker=dict(color=forecast_colors, size=8, line=dict(width=0, color='black')),
            ))

            fig.update_layout(
                title=f'XGBoost Forecast for {hydro_city}',
                xaxis_title='Date',
                yaxis_title='Drought Index Value',
                legend=dict(x=0, y=1),
                template='plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)
