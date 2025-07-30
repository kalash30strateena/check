def get_temperature_data():
    import streamlit as st
    import folium
    import plotly.graph_objects as go
    import pandas as pd
    import requests
    from datetime import timedelta
    from xgboost import XGBRegressor
    from streamlit_folium import st_folium
    from tabs_data.credentials import cred # type: ignore
    engine = cred()

    left_col, right_col = st.columns([4,5])
    with left_col:
        def get_station_df():
            conn = engine
            query = """
                SELECT station_code, station_name, province, latitude, longitude, altitude
                FROM stations
                WHERE station_code IS NOT NULL
                AND station_name IS NOT NULL
                AND province IS NOT NULL
                AND latitude IS NOT NULL
                AND longitude IS NOT NULL
                AND altitude IS NOT NULL;
            """
            df = pd.read_sql_query(query, conn)
            return df

        station_df = get_station_df()

        province_list = sorted(station_df["province"].dropna().unique())
        selected_province = st.selectbox("Filter stations by province:", ["All"] + province_list, key="province_select")

        if selected_province == "All":
            filtered_df = station_df
            map_center = [-38.4161, -63.6167]  # Center of Argentina
            zoom_level = 4
        else:
            filtered_df = station_df[station_df["province"] == selected_province]
            if not filtered_df.empty:
                map_center = [
                    filtered_df["latitude"].mean(),
                    filtered_df["longitude"].mean()
                ]
                zoom_level = 5
            else:
                map_center = [-38.4161, -63.6167]
                zoom_level = 4

        m = folium.Map(location=map_center, zoom_start=zoom_level)
        for _, row in filtered_df.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                tooltip=f"{row['station_name']} ({row['station_name']})",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)

        st_map = st_folium(m, width=450, height=400, use_container_width=True)

    # --- RIGHT COLUMN: Weather, plots, and forecast ---
    with right_col:
        st.write("")
        st.write("")

        # --- Authenticate for API ---
        auth_url = "https://api-test.smn.gob.ar/v1/api-token/auth"
        auth_data = {
            "username": "cruzroja",
            "password": "TCpqNb7b"
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        auth_response = requests.post(auth_url, headers=headers, json=auth_data)

        # --- Get clicked station info from map ---
        clicked_station_code = None
        clicked_station_name = None
        if st_map and st_map.get("last_object_clicked"):
            lat = st_map["last_object_clicked"]["lat"]
            lng = st_map["last_object_clicked"]["lng"]
            tolerance = 1e-5
            match = station_df[
                (abs(station_df["latitude"] - lat) < tolerance) &
                (abs(station_df["longitude"] - lng) < tolerance)
            ]
            if not match.empty:
                clicked_station_code = str(int(match.iloc[0]["station_code"])).strip()
                clicked_station_name = match.iloc[0]["station_name"].strip()
        
        # --- Show station weather card ---
        if auth_response.status_code == 200 and clicked_station_code:
            token = auth_response.json().get("token", "").strip()
            stations_url = f"https://api-test.smn.gob.ar/v1/weather/station/{clicked_station_code}"
            headers_with_auth = {
                "Authorization": f"JWT {token}",
                "Accept": "application/json"
            }
            stations_response = requests.get(stations_url, headers=headers_with_auth)
            if stations_response.status_code == 200:
                stations_data = stations_response.json()
                weather_desc = stations_data['weather'].get('description', '')

                from datetime import datetime
                try:
                    date_obj = datetime.fromisoformat(stations_data['date'])
                    date_str = date_obj.strftime('%A, %d %b %Y, %I:%M %p')
                except Exception:
                    date_str = stations_data['date']

                # Display station NAME instead of ID
                st.markdown(
                    f"""
                    <div style="
                        background: #b9d9fa; 
                        border-radius: 16px; 
                        padding: 10px 10px; 
                        width: 100%; 
                        max-width: 100vw;
                        margin: 0 auto;
                        display: flex; 
                        flex-direction: column;
                        gap: 10px;
                    ">
                        <div style="display: flex; flex-direction: row; gap: 22px; align-items: center;">
                            <div style="font-size: 1.05em; font-weight: 600;">{clicked_station_name}</div>
                            <div style="font-size: 0.97em;">{weather_desc}</div>
                            <div style="color: #000305; font-size: 0.97em;">{date_str}</div>
                        </div>
                        <div style="display: flex; flex-direction: row; gap: 22px; flex-wrap: wrap;">
                            <div><b>Temperature:</b> {stations_data['temperature']}°C</div>
                            <div><b>Humidity:</b> {stations_data['humidity']}%</div>
                            <div><b>Pressure:</b> {stations_data['pressure']} hPa</div>
                            <div><b>Visibility:</b> {stations_data['visibility']} km</div>
                            <div><b>Wind:</b> {stations_data['wind']['speed']} km/h {stations_data['wind']['direction']} ({stations_data['wind']['deg']}°)</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.info("Failed to fetch station weather data.")
        elif not clicked_station_code:
            st.info("Click on a station marker to view its climate, temperature and pressure data.")
        else:
            st.info("Failed to authenticate for station data.")
            
    #     # --- Climate data plot ---
        def get_climate_data(station_code):
            conn = engine
            query = """
                SELECT month, max_temp, min_temp, avg_pressure
                FROM climate_months
                WHERE station_code = %s
            """
            df = pd.read_sql_query(query, conn, params=(station_code,))
            return df

        if clicked_station_code:
            climate_df = get_climate_data(clicked_station_code)
            if not climate_df.empty:
                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=climate_df["month"],
                    y=climate_df["max_temp"],
                    mode="lines+markers",
                    name="Max Temp",
                    line=dict(color="red"),
                    marker=dict(symbol="circle", size=8, color="red"),
                    yaxis="y1"
                ))

                fig.add_trace(go.Scatter(
                    x=climate_df["month"],
                    y=climate_df["min_temp"],
                    mode="lines+markers",
                    name="Min Temp",
                    line=dict(color="orange"),
                    marker=dict(symbol="circle", size=8, color="orange"),
                    yaxis="y1"
                ))

                fig.add_trace(go.Scatter(
                    x=climate_df["month"],
                    y=climate_df["avg_pressure"],
                    mode="lines+markers",
                    name="Avg Pressure",
                    line=dict(color="grey"),
                    marker=dict(symbol="circle", size=8, color="grey"),
                    yaxis="y2"
                ))

                # Use the station name in the title!
                fig.update_layout(
                    title=f"Monthly Average Data for {clicked_station_name}",
                    xaxis=dict(title="Month"),
                    yaxis=dict(title="Temperature (°C)"),
                    yaxis2=dict(
                        title="Pressure (hPa)",
                        overlaying="y",
                        side="right"
                    ),
                    legend=dict(title="Variable"),
                    width=700,
                    height=400,
                    margin=dict(l=40, r=40, t=60, b=40)
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No climate data available for this station.")

    # --------------- Temeperature max-min forecast -------
    if clicked_station_code is not None:
        # --- Get historical data ---
        def get_historical_temperature(station_code):
            conn = engine
            query = """
                SELECT date, min_temp, max_temp
                FROM temperature
                WHERE station_code = %s
                ORDER BY date DESC
                LIMIT 300
            """
            df = pd.read_sql_query(query, conn, params=(station_code,))
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            return df
        # Fetch forecast data for selected station
        def get_forecast_temperature(station_code):
            conn = engine
            query = """
                SELECT date, min_temp, max_temp, risk_level
                FROM temperature_forecast
                WHERE station_code = %s
                ORDER BY date
            """
            df = pd.read_sql_query(query, conn, params=(station_code,))
            df['date'] = pd.to_datetime(df['date'])
            return df
        
        
        hist_df = get_historical_temperature(clicked_station_code)
        forecast_df = get_forecast_temperature(clicked_station_code)

        for target_col, display_name in zip(['max_temp', 'min_temp'], ['Maximum Temperature', 'Minimum Temperature']):
            fig = go.Figure()

            # 1. Historical data
            fig.add_trace(go.Scatter(
                x=hist_df['date'],
                y=hist_df[target_col],
                mode='lines+markers',
                name=f'Actual',
                marker=dict(color='#17bf55', size=8),
                line=dict(color='#17bf55'),
            ))

            # 2. Forecast data with risk coloring
            color_map = {'H': 'red', 'L': 'blue'}
            marker_colors = [color_map.get(risk, 'orange') for risk in forecast_df['risk_level']]
            risk_text = [
                'High Risk' if risk == 'H' else
                'Low Risk' if risk == 'L' else
                'Normal'
                for risk in forecast_df['risk_level']
            ]

            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df[target_col],
                mode='lines+markers',
                name='Predicted',
                marker=dict(color=marker_colors, size=6, symbol='circle'),
                line=dict(color='orange', dash='dash'),
                text=risk_text,
                ))

            # 3. Connecting line for continuity
            if not hist_df.empty and not forecast_df.empty:
                fig.add_trace(go.Scatter(
                    x=[hist_df['date'].iloc[-1], forecast_df['date'].iloc[0]],
                    y=[hist_df[target_col].iloc[-1], forecast_df[target_col].iloc[0]],
                    mode='lines',
                    line=dict(color='orange', dash='dot'),
                    showlegend=False
                ))

            fig.update_layout(
                title=f"{display_name} 7-day Forecast for {clicked_station_name}",
                xaxis_title="Date",
                yaxis_title=f"{display_name} (°C)",
                legend=dict(x=1, y=1, xanchor='right', yanchor='top'),
                width=700,
                height=400,
                margin=dict(l=40, r=40, t=60, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Click on a station marker to view its temperature data and forecast.")
        
    # --- Pressure forecast functions ---
    @st.cache_data
    def get_station_list(_engine):
        query = "SELECT DISTINCT station_code FROM pressure"
        df = pd.read_sql(query, _engine)
        return df['station'].sort_values().tolist()

    def load_station_data(engine, station_code):
        query = "SELECT date, pressure FROM pressure WHERE station_code = %s ORDER BY date"
        df = pd.read_sql(query, engine, params=(station_code,))
        df['date'] = pd.to_datetime(df['date'])
        df['pressure'] = pd.to_numeric(df['pressure'], errors='coerce')
        df = df.set_index('date').ffill().reset_index()
        return df

    def create_lag_features(df, lags=7):
        df = df.copy()
        for lag in range(1, lags + 1):
            df[f'lag_{lag}'] = df['pressure'].shift(lag)
        return df.dropna()

    def forecast_pressure(df, lags=7, horizon=7):
        df_lagged = create_lag_features(df, lags)
        X = df_lagged.drop(columns=['pressure', 'date'])
        y = df_lagged['pressure']

        model = XGBRegressor(n_estimators=100)
        model.fit(X, y)
        df_lagged['predicted'] = model.predict(X)

        last = df_lagged.iloc[-1:].copy()
        future_rows = []

        for _ in range(horizon):
            next_input = last.copy()
            for lag in range(1, lags + 1):
                col = f'lag_{lag}'
                next_input[col] = last['pressure'].iloc[-lag] if lag <= len(last) else next_input[col]

            next_pred = model.predict(next_input.drop(columns=['pressure', 'predicted', 'date']))[0]
            next_date = last['date'].iloc[-1] + timedelta(days=1)
            future_rows.append({'date': next_date, 'forecast': next_pred})
            last = pd.concat([last, pd.DataFrame({'date': [next_date], 'pressure': [next_pred]})]).tail(lags)

        forecast_df = pd.DataFrame(future_rows).set_index('date')
        return df_lagged.set_index('date'), forecast_df

    def plot_forecast(df, forecast_df, station_name):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['pressure'], name='Actual', mode='lines+markers', line=dict(color='#17bf55', width=2)))
        fig.add_trace(go.Scatter(x=df.index, y=df['predicted'], name='Predicted', mode='lines', line=dict(color='#82070d', dash="dash")))
        fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df['forecast'], name='Forecast', mode='lines+markers', line=dict(color="orange", dash="dash")))
        fig.add_trace(go.Scatter(
            x=[df.index[-1], forecast_df.index[0]],
            y=[df['pressure'].iloc[-1], forecast_df['forecast'].iloc[0]],
            mode='lines',
            line=dict(color="orange", dash="dash"),
            showlegend=False
        ))
        # Use the name in the title
        fig.update_layout(title=f"Pressure Forecast for 7 days - {station_name}", xaxis_title='Date', yaxis_title='Pressure (hPa)')
        return fig

    # --- Use clicked_station_code for pressure forecast ---
    if clicked_station_code:
        df = load_station_data(engine, clicked_station_code)
        if len(df) < 22:
            st.warning("Not enough data to forecast.")
        else:
            hist_df, forecast_df = forecast_pressure(df)
            # Filter to show only data from 2025 onwards
            hist_df = hist_df[hist_df.index >= pd.to_datetime("2025-01-01")]

            if hist_df.empty:
                hist_df = hist_df.tail(40)

            if hist_df.empty:
                st.warning("No data available for this station.")
            else:
                fig = plot_forecast(hist_df, forecast_df, clicked_station_name)
                st.plotly_chart(fig, use_container_width=True)
    else:
        pass