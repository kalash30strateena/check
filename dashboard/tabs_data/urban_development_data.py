def get_urban_development_data():
    import streamlit as st 
    import pandas as pd 
    import plotly.graph_objects as go
    from sqlalchemy import text
    from tabs_data.credentials import cred  # type: ignore
    engine=cred()
    indicator_groups = {
        "Demographic" : ['Population density (people per sq. km of land area)', 'Population in largest city', 
                'Population in the largest city (% of urban population)', 'Population in urban agglomerations of more than 1 million', 
                'Population in urban agglomerations of more than 1 million (% of total population)', 'Urban population growth (annual %)', 'Urban population', 'Urban population (% of total)'
                ],
        "Health & Safety" : ['Mortality caused by road traffic injury (per 100,000 population)'],
        "Infrastructure": ['Access to electricity, urban (% of urban population)']
    }

    @st.cache_data
    def get_filtered_data(indicator_list):
        if not indicator_list:
            return pd.DataFrame()

        if len(indicator_list) == 1:
            query = text("""
                SELECT year, indicator_name, value 
                FROM urban_development
                WHERE indicator_name = :indicator
                ORDER BY year;
            """)
            df = pd.read_sql_query(query, engine, params={"indicator": indicator_list[0]})
        else:
            # Dynamically generate placeholders and parameter dict
            placeholders = ", ".join([f":indicator_{i}" for i in range(len(indicator_list))])
            query = text(f"""
                SELECT year, indicator_name, value 
                FROM urban_development
                WHERE indicator_name IN ({placeholders})
                ORDER BY year;
            """)
            params = {f"indicator_{i}": val for i, val in enumerate(indicator_list)}
            df = pd.read_sql_query(query, engine, params=params)

        df["year"] = pd.to_datetime(df["year"], format='%Y')
        df.set_index("year", inplace=True)
        df = df.pivot(columns="indicator_name", values="value").sort_index()
        return df


    selected_category = st.selectbox("Select a Category", ["-- Select a category --"] + list(indicator_groups.keys()))
    if selected_category == "-- Select a category --":
        st.info("Please select a category to view urban development data.")
    else:
        selected_indicators = indicator_groups[selected_category]
        df = get_filtered_data(selected_indicators)

        rows = [st.columns(3) for _ in range((len(df.columns) + 2) // 3)]  
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

        for i, indicator in enumerate(df.columns):
            color = colors[i % len(colors)]
            min_year = df[indicator].dropna().index.min()  
            max_year = df[indicator].dropna().index.max()  
            filtered_df = df.loc[min_year:max_year]  
                
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df[indicator], mode="lines+markers", name=indicator, line=dict(color=color)))
            fig.update_layout(title=indicator, xaxis_title="Year", yaxis_title="value", width=450, height=400, template="plotly_white", legend=dict(x=1, y=0.5, bgcolor="rgba(255,255,255,0.5)", font=dict(size=10)))
                
            row = rows[i // 3]  
            row[i % 3].plotly_chart(fig)