def get_inequality_poverty_data():
    import pandas as pd 
    import plotly.graph_objects as go
    import streamlit as st
    import numpy as np 
    from pmdarima import auto_arima #type: ignore
    from sqlalchemy import text
    from tabs_data.credentials import cred  # type: ignore
    engine = cred()
    indicator_groups = {
        "Income Share Distribution": [
            "Income Share of First Quintile", "Income Share of Second Quintile",
            "Income Share of Third Quintile", "Income Share of Fourth Quintile",
            "Income Share of Fifth Quintile", "Income share held by second 20%",
            "Income share held by third 20%", "Income share held by fourth 20%",
            "Income share held by highest 20%", "Income share held by highest 10%"],
        "Labor-Linked Poverty": ["Labor Income Poverty Index"],
        "Middle Class & Vulnerable Groups": [
            "Middle Class ($10-50 a day) Headcount", "Vulnerable ($4-10 a day) Headcount"],
        "Extreme & Moderate Poverty": [
            "Poverty Gap ($1.90 a day)", "Poverty Gap ($2.50 a day)", "Poverty Gap ($4 a day)",
            "Poverty Headcount ($1.90 a day)", "Poverty Headcount ($2.50 a day)", "Poverty Headcount ($4 a day)",
            "Poverty Severity ($1.90 a day)", "Poverty Severity ($2.50 a day)", "Poverty Severity ($4 a day)",
            "Poverty headcount ratio at national poverty lines (% of population)",
            "Proportion of people living below 50 percent of median income (%)"],
        "Poverty Gap - PPP": [
            "Official Moderate Poverty Rate-Urban", "Poverty gap at $2.15 a day (2017 PPP) (%)",
            "Poverty gap at $3.65 a day (2017 PPP) (%)", "Poverty gap at $6.85 a day (2017 PPP) (%)"]
    }
    forecast_indicators = [
        "Poverty headcount ratio at $2.15 a day (2017 PPP) (% of population)",
        "Poverty headcount ratio at $3.65 a day (2017 PPP) (% of population)",
        "Poverty headcount ratio at $6.85 a day (2017 PPP) (% of population)"]

    inequality_options = {
        "Income": [
            "Atkinson, A(.5)", "Atkinson, A(1)", "Atkinson, A(2)",
            "Generalized Entrophy, GE(-1)", "Generalized Entrophy, GE(2)", "Gini Coefficient",
            "Gini Coefficient (No Zero Income)", "Gini index", "Gini, Urban",
            "Mean Log Deviation, GE(0)", "Mean Log Deviation, GE(0), Urban",
            "Rate 75/25", "Rate 90/10", "Theil Index, GE(1)", "Theil Index, GE(1), Urban"],
        "Human Development": ['Coefficient of human inequality', 'Inequality in eduation', 'Inequality in income', 'Inequality in life expectancy',]
    }

    @st.cache_data
    def get_filtered_data(indicator_list, category):
        if not indicator_list:
            return pd.DataFrame()

        table_name = "poverty" if category != "Human Development" else "human_development"

        if len(indicator_list) == 1:
            query = text(f"""
                SELECT year, indicator_name, value 
                FROM {table_name}
                WHERE indicator_name = :indicator
                ORDER BY year;
            """)
            df = pd.read_sql_query(query, engine, params={"indicator": indicator_list[0]})
        else:
            placeholders = ", ".join([f":indicator_{i}" for i in range(len(indicator_list))])
            query = text(f"""
                SELECT year, indicator_name, value 
                FROM {table_name}
                WHERE indicator_name IN ({placeholders})
                ORDER BY year;
            """)
            params = {f"indicator_{i}": val for i, val in enumerate(indicator_list)}
            df = pd.read_sql_query(query, engine, params=params)

        df["year"] = pd.to_datetime(df["year"], format='%Y')
        df.set_index("year", inplace=True)
        df = df.pivot(columns="indicator_name", values="value").sort_index()
        return df


    st.subheader("Poverty Data")
    # ---------------------------
    # User must select a category
    selected_category = st.selectbox(
        "Select a Poverty Category",
        ["-- Select a category --"] + list(indicator_groups.keys()),
        index=0
    )
    if selected_category == "-- Select a category --":
        st.info("Please select a category to view poverty data.")
    else:
        selected_indicators = indicator_groups[selected_category]
        df = get_filtered_data(selected_indicators, selected_category)

        def forecast_and_plot(df):
            forecast_df = pd.DataFrame()
            future_years = pd.date_range(start=str(df.index[-1].year + 1), periods=5, freq="YS")
            fig = go.Figure()
            colors = ["blue", "green", "orange"]
            for i, indicator in enumerate(forecast_indicators):
                series = df[indicator].fillna(method="ffill")
                model = auto_arima(series, seasonal=False, stepwise=True, suppress_warnings=True)
                forecast_values = model.predict(n_periods=5)
                forecast_df[indicator] = np.array(forecast_values)
                forecast_df.index = future_years
                clean_label = next(word for word in indicator.split() if "$" in word) + " a day"
                # Actual values
                fig.add_trace(go.Scatter(
                    x=df.index, y=series, mode="lines+markers",
                    name=f"Actual: {clean_label}", line=dict(color=colors[i])
                ))
                # Forecasted values
                fig.add_trace(go.Scatter(
                    x=forecast_df.index, y=forecast_df[indicator], mode="lines",
                    name=f"Forecast: {clean_label}", line=dict(dash="dash", color=colors[i])
                ))
            fig.update_layout(
                title="Forecast for Poverty Headcount Ratios with 5 year forecast",
                xaxis_title="Year",
                yaxis_title="Population (%)",
                width=1000,
                height=500,
                legend=dict(x=1, y=0.5, bgcolor="rgba(255,255,255,0.5)", font=dict(size=10)),
                template="plotly_white"
            )
            st.plotly_chart(fig)

        if selected_category == "Extreme & Moderate Poverty":
            forecast_df = get_filtered_data(forecast_indicators, "Extreme & Moderate Poverty")
            forecast_and_plot(forecast_df)
            rows = [st.columns(3) for _ in range((len(df.columns) + 2) // 3)]
            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
            for i, indicator in enumerate(df.columns):
                color = colors[i % len(colors)]
                min_year = df[indicator].dropna().index.min()
                max_year = df[indicator].dropna().index.max()
                filtered_df = df.loc[min_year:max_year]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df[indicator], mode="lines+markers", name=indicator, line=dict(color=color)))
                fig.update_layout(title=indicator, xaxis_title="Year", yaxis_title="value", width=450, height=400)
                row = rows[i // 3]
                row[i % 3].plotly_chart(fig)
        else:
            rows = [st.columns(3) for _ in range((len(df.columns) + 2) // 3)]
            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
            for i, indicator in enumerate(df.columns):
                color = colors[i % len(colors)]
                min_year = df[indicator].dropna().index.min()
                max_year = df[indicator].dropna().index.max()
                filtered_df = df.loc[min_year:max_year]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df[indicator], mode="lines+markers", name=indicator, line=dict(color=color)))
                fig.update_layout(title=indicator, xaxis_title="Year", yaxis_title="Population (%)", width=450, height=400, template="plotly_white", legend=dict(x=1, y=0.5, bgcolor="rgba(255,255,255,0.5)", font=dict(size=10)))
                row = rows[i // 3]
                row[i % 3].plotly_chart(fig)

    # Inequality Section
    st.subheader("Inequality Data")
    selected_inequality_category = st.selectbox(
        "Select an Inequality category",
        ["-- Select a category --"] + list(inequality_options.keys()),
        index=0,
        key="ineq"
    )
    if selected_inequality_category == "-- Select a category --":
        st.info("Please select a category to view inequality data.")
    else:
        selected_indicators = inequality_options[selected_inequality_category]
        df = get_filtered_data(selected_indicators, selected_inequality_category)
        rows = [st.columns(3) for _ in range((len(df.columns) + 2) // 3)]
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
        for i, indicator in enumerate(df.columns):
            color = colors[i % len(colors)]
            min_year = df[indicator].dropna().index.min()
            max_year = df[indicator].dropna().index.max()
            filtered_df = df.loc[min_year:max_year]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df[indicator], mode="lines+markers", name=indicator, line=dict(color=color)))
            fig.update_layout(title=indicator, xaxis_title="Year", yaxis_title="Population (%)", width=450, height=400, template="plotly_white", legend=dict(x=1, y=0.5, bgcolor="rgba(255,255,255,0.5)", font=dict(size=10)))
            row = rows[i // 3]
            row[i % 3].plotly_chart(fig)