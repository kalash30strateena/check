def get_wildfires_data():
    import streamlit as st 
    import pandas as pd
    import plotly.graph_objects as go
    import calendar
    from pmdarima import auto_arima #type: ignore
    
    from tabs_data.credentials import cred #type: ignore
    engine = cred()
    
    col1, col2 = st.columns([1,1])
    with col1:            
        
        @st.cache_data
        def load_regions():
            
            df = pd.read_sql("SELECT region_id, region_name FROM regions ORDER BY region_name", engine)
            return df

        @st.cache_data
        def load_fires_by_region(region_id):
            
            query = """
                SELECT f.year, r.region_name, f.fire_count
                FROM fires_by_region f
                JOIN regions r ON f.region_id = r.region_id
                WHERE f.region_id = %s
                ORDER BY f.year
            """
            df = pd.read_sql(query, engine, params=(region_id,))
            return df

        regions_df = load_regions()
        region_names = regions_df['region_name'].tolist()
        selected_region_name = st.selectbox("Select a region to view fire alerts per year:", region_names)
        selected_region_id = int(regions_df.loc[regions_df['region_name'] == selected_region_name, 'region_id'].iloc[0])  # Convert to native int
        df_selected = load_fires_by_region(selected_region_id)

        years = df_selected['year'].to_numpy()
        values = df_selected['fire_count'].to_numpy()

        if len(values) > 2:
            model = auto_arima(values, seasonal=False, suppress_warnings=True)
            forecast = model.predict(n_periods=1)
            forecast_years = [years[-1] + i for i in range(1, 4)]
        else:
            forecast = []
            forecast_years = []

        all_years = list(years) + list(forecast_years)
        all_values = list(values) + list(forecast)

        fig = go.Figure()

        # Actual values: solid red line
        fig.add_trace(go.Scatter(
            x=years, y=values,
            mode='lines+markers',
            name='Actual Fire Count',
            line=dict(color='red', width=2)
        ))

        # Forecast values: solid black line
        if forecast_years:
            fig.add_trace(go.Scatter(
                x=forecast_years, y=forecast,
                mode='lines+markers',
                name='Forecasted Fire Count',
                line=dict(color='black', width=2)
            ))
            # Connecting line between last actual and first forecast (dashed)
            fig.add_trace(go.Scatter(
                x=[years[-1], forecast_years[0]],
                y=[values[-1], forecast[0]],
                mode='lines',
                name='Forecast Transition',
                line=dict(color='black', width=2, dash='dash'),
                showlegend=False
            ))

        fig.update_layout(
            title=f"Fires by Month - {selected_region_name}",
            xaxis_title="Year",
            yaxis_title="Fire Count",
            legend=dict(x=0.01, y=0.99, bordercolor="Black", borderwidth=1)
        )

        st.plotly_chart(fig, use_container_width=True)
        
    with col2:

        @st.cache_data
        def load_months():
            df = pd.read_sql("SELECT DISTINCT month FROM fires_by_month ORDER BY month", engine)
            return df['month'].tolist()

        @st.cache_data
        def load_fires_by_month(selected_month):
            
            query = """
                SELECT year, month, fire_count
                FROM fires_by_month
                WHERE month = %s
                ORDER BY year
            """
            df = pd.read_sql(query, engine, params=(selected_month,))
            return df
        
        months = load_months()  # This should return a list of integers
        month_options = [calendar.month_abbr[m] for m in months]
        selected_month_name = st.selectbox("Select a month to view yearly fire alerts:", month_options)
        selected_month = months[month_options.index(selected_month_name)]

        # Load data for selected month
        df_selected = load_fires_by_month(selected_month)
        years = df_selected['year'].to_numpy()
        values = df_selected['fire_count'].to_numpy()

        # Forecast next 3 years
        if len(values) > 2:
            model = auto_arima(values, seasonal=False, suppress_warnings=True)
            forecast = model.predict(n_periods=1)
            forecast_years = [years[-1] + i for i in range(1, 4)]
        else:
            forecast = []
            forecast_years = []

        fig = go.Figure()

        # Historical: royal blue line
        fig.add_trace(go.Scatter(
            x=years, y=values,
            mode='lines+markers',
            name='Actual Fire Count',
            line=dict(color='royalblue', width=2)
        ))

        # Forecast: black line
        if forecast_years:
            fig.add_trace(go.Scatter(
                x=forecast_years, y=forecast,
                mode='lines+markers',
                name='Forecasted Fire Count',
                line=dict(color='black', width=2)
            ))
            # Dashed connecting line
            fig.add_trace(go.Scatter(
                x=[years[-1], forecast_years[0]],
                y=[values[-1], forecast[0]],
                mode='lines',
                name='Forecast Transition',
                line=dict(color='black', width=2, dash='dash'),
                showlegend=False
            ))

        fig.update_layout(
            title=f"Fires by Month - {selected_month}",
            xaxis_title="Year",
            yaxis_title="Fire Count",
            legend=dict(x=0.01, y=0.99, bordercolor="Black", borderwidth=1)
        )

        st.plotly_chart(fig, use_container_width=True)

    
    with col1:
        @st.cache_data
        def load_provinces():
            
            df = pd.read_sql("SELECT province_id, province_name FROM provinces ORDER BY province_name", engine)
            return df

        @st.cache_data
        def load_fires_by_province(province_id):
            
            query = """
                SELECT f.year, p.province_name, f.fire_count
                FROM fires_by_province f
                JOIN provinces p ON f.province_id = p.province_id
                WHERE f.province_id = %s
                ORDER BY f.year
            """
            df = pd.read_sql(query, engine, params=(province_id,))
            return df

        # Province selection
        provinces_df = load_provinces()
        province_names = provinces_df['province_name'].tolist()
        selected_province_name = st.selectbox("Select a Province to view amount of fire alerts:", province_names)
        selected_province_id = int(provinces_df.loc[provinces_df['province_name'] == selected_province_name, 'province_id'].iloc[0])

        # Data for selected province
        df_selected = load_fires_by_province(selected_province_id)
        years = df_selected['year'].to_numpy()
        values = df_selected['fire_count'].to_numpy()

        # Forecast next 3 years
        if len(values) > 2:
            model = auto_arima(values, seasonal=False, suppress_warnings=True)
            forecast = model.predict(n_periods=1)
            forecast_years = [years[-1] + i for i in range(1, 4)]
        else:
            forecast = []
            forecast_years = []

        fig = go.Figure()

        # Historical: seagreen line
        fig.add_trace(go.Scatter(
            x=years, y=values,
            mode='lines+markers',
            name='Actual Fire Count',
            line=dict(color='seagreen', width=2)
        ))

        # Forecast: black line
        if forecast_years:
            fig.add_trace(go.Scatter(
                x=forecast_years, y=forecast,
                mode='lines+markers',
                name='Forecasted Fire Count',
                line=dict(color='black', width=2)
            ))
            # Dashed connecting line
            fig.add_trace(go.Scatter(
                x=[years[-1], forecast_years[0]],
                y=[values[-1], forecast[0]],
                mode='lines',
                name='Forecast Transition',
                line=dict(color='black', width=2, dash='dash'),
                showlegend=False
            ))

        fig.update_layout(
            title=f"Fires by Province - {selected_province_name}",
            xaxis_title="Year",
            yaxis_title="Fire Count",
            legend=dict(x=0.01, y=0.99, bordercolor="Black", borderwidth=1)
        )

        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        @st.cache_data
        def load_provinces():
            
            df = pd.read_sql("SELECT province_id, province_name FROM provinces ORDER BY province_name", engine)
            return df

        @st.cache_data
        def load_hectares_by_province(province_id):
            
            query = """
                SELECT f.year, p.province_name, f.hectares
                FROM fires_by_province f
                JOIN provinces p ON f.province_id = p.province_id
                WHERE f.province_id = %s
                ORDER BY f.year
            """
            df = pd.read_sql(query, engine, params=(province_id,))
            return df

        # Province selection
        provinces_df = load_provinces()
        province_names = provinces_df['province_name'].tolist()
        selected_province_name = st.selectbox("Select a Province to view hectares damaged:", province_names)
        selected_province_id = int(provinces_df.loc[provinces_df['province_name'] == selected_province_name, 'province_id'].iloc[0])

        # Data for selected province
        df_selected = load_hectares_by_province(selected_province_id)
        years = df_selected['year'].to_numpy()
        values = df_selected['hectares'].to_numpy()

        # Forecast next 3 years
        if len(values) > 2:
            model = auto_arima(values, seasonal=False, suppress_warnings=True)
            forecast = model.predict(n_periods=1)
            forecast_years = [years[-1] + i for i in range(1, 4)]
        else:
            forecast = []
            forecast_years = []

        fig = go.Figure()

        # Historical: seagreen line
        fig.add_trace(go.Scatter(
            x=years, y=values,
            mode='lines+markers',
            name='Actual Hectares Damaged',
            line=dict(color='purple', width=2)
        ))

        # Forecast: black line
        if forecast_years:
            fig.add_trace(go.Scatter(
                x=forecast_years, y=forecast,
                mode='lines+markers',
                name='Forecasted Hectares Damaged',
                line=dict(color='black', width=2)
            ))
            # Dashed connecting line
            fig.add_trace(go.Scatter(
                x=[years[-1], forecast_years[0]],
                y=[values[-1], forecast[0]],
                mode='lines',
                name='Forecast Transition',
                line=dict(color='black', width=2, dash='dash'),
                showlegend=False
            ))

        fig.update_layout(
            title=f"Hectares Damaged by Province (Yearly Total) - {selected_province_name}",
            xaxis_title="Year",
            yaxis_title="Hectares Damaged",
            legend=dict(x=0.01, y=0.99, bordercolor="Black", borderwidth=1)
        )

        st.plotly_chart(fig, use_container_width=True)