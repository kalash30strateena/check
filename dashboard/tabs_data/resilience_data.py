def get_resilience_data():
    import streamlit as  st 
    import pandas as pd 
    import plotly.graph_objects as go
    from sqlalchemy import text, bindparam
    from tabs_data.credentials import cred  # type: ignore
    engine = cred()
    
    indicator_categories = {
        "Digital Connectivity & ICT": [
            'Mobile cellular subscriptions', 'Fixed telephone subscriptions', 'Fixed broadband subscriptions', 
            'Secure Internet servers', 'Secure Internet servers (per 1 million people)', 
            'Individuals using the Internet (% of population)'
        ],
        "Energy Infrastructure": [
            'Investment in energy with private participation (current US$)', 
            'Public private partnerships investment in energy (current US$)'
        ],
        "Innovation & Industry": [
            'Industrial design applications, nonresident, by count', 'Industrial design applications, resident, by count', 
            'Trademark applications, nonresident, by count', 'Trademark applications, resident, by count'
        ],
        "Transport Infrastructure": [
            'Investment in transport with private participation (current US$)', 
            'Public private partnerships investment in transport (current US$)',
            'Air transport, registered carrier departures worldwide', 'Air transport, freight (million ton-km)', 
            'Air transport, passengers carried', 'Railways, goods transported (million ton-km)', 
            'Railways, passengers carried (million passenger-km)', 'Rail lines (total route-km)'
        ],
        "Water Infrastructure": [
            'Annual freshwater withdrawals, agriculture (% of total freshwater withdrawal)', 
            'Annual freshwater withdrawals, domestic (% of total freshwater withdrawal)', 
            'Annual freshwater withdrawals, industry (% of total freshwater withdrawal)', 
            'Annual freshwater withdrawals, total (billion cubic meters)', 
            'Annual freshwater withdrawals, total (% of internal resources)', 
            'Renewable internal freshwater resources per capita (cubic meters)', 
            'Investment in water and sanitation with private participation (current US$)', 
            'Public private partnerships investment in water and sanitation (current US$)'
        ]
    }

    @st.cache_data
    def get_filtered_data(indicator_list):
        from sqlalchemy import text, bindparam

        if isinstance(indicator_list, str):
            indicator_list = [indicator_list]

        # Handle empty list gracefully
        if not indicator_list:
            return pd.DataFrame()

        query = text("""
            SELECT year, indicator_name, value 
            FROM infrastructure 
            WHERE indicator_name IN :indicators
            ORDER BY year;
        """).bindparams(bindparam("indicators", expanding=True))

        # VERY IMPORTANT: SQLAlchemy `text()` query and expanding bindparam
        df = pd.read_sql(query, con=engine, params={"indicators": indicator_list})

        df["year"] = pd.to_datetime(df["year"], format='%Y', errors='coerce')
        df.set_index("year", inplace=True)
        df = df.pivot(columns="indicator_name", values="value").sort_index()

        return df

    selected_category = st.selectbox("Select a category", ["-- Select a category --"] + list(indicator_categories.keys()))
    if selected_category == "-- Select a category --":
        st.info("Please select a category to view infrastructure data.")
    else:
        selected_indicators = indicator_categories[selected_category]
        df = get_filtered_data(selected_indicators)

        rows = [st.columns(3) for _ in range((len(df.columns) + 2) // 3)]  
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
            
        for i, indicator in enumerate(df.columns):
            color = colors[i % len(colors)]
            min_year = df[indicator].dropna().index.min()  # Get first available year
            max_year = df[indicator].dropna().index.max()  # Get last available year
            filtered_df = df.loc[min_year:max_year]  # Filter dataframe within this range
                
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=filtered_df.index,
                y=filtered_df[indicator],
                mode="lines+markers",
                name=indicator,
                line=dict(color=color)
            ))
            fig.update_layout(
                title=indicator,
                xaxis_title="Year",
                yaxis_title="Population (%)",
                width=450,
                height=400,
                template="plotly_white",
                legend=dict(x=1, y=0.5, bgcolor="rgba(255,255,255,0.5)", font=dict(size=10))
            )

            row = rows[i // 3]  
            row[i % 3].plotly_chart(fig)