def get_health_data():
    import pandas as pd 
    import streamlit as st
    from sqlalchemy import text
    import plotly.graph_objects as go
    from tabs_data.credentials import cred  # type: ignore
    engine=cred()
    
    import itertools
    color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    color_cycle = itertools.cycle(color_palette)

    indicator_groups = {
        "Alcohol & Substance Use": [
        'Total alcohol consumption per capita, female (liters of pure alcohol, projected estimates, female 15+ years of age)',
        'Total alcohol consumption per capita, male (liters of pure alcohol, projected estimates, male 15+ years of age)',
        'Total alcohol consumption per capita (liters of pure alcohol, projected estimates, 15+ years of age)',
    ],
        "Disease Burden": [
            ["Number of infant deaths", "Number of infant deaths, female", "Number of infant deaths, male"],
            ["Number of under-five deaths", "Number of under-five deaths, female", "Number of under-five deaths, male"], 
            ["Number of neonatal deaths"],  
            ["Mortality rate, under-5 (per 1,000 live births)", "Mortality rate, under-5, female (per 1,000 live births)", "Mortality rate, under-5, male (per 1,000 live births)"], 
            ["Mortality from CVD, cancer, diabetes or CRD between exact ages 30 and 70, female (%)"], 
            ["Mortality from CVD, cancer, diabetes or CRD between exact ages 30 and 70, male (%)"],  
            ["Mortality from CVD, cancer, diabetes or CRD between exact ages 30 and 70 (%)"],  
            ["Mortality rate, neonatal (per 1,000 live births)"], ["Number of maternal deaths"],
            ["Lifetime risk of maternal death (1 in: rate varies by country)"], ["Lifetime risk of maternal death (%)"],
            ["Maternal mortality ratio (national estimate, per 100,000 live births)"],
            ["Suicide mortality rate, female (per 100,000 female population)", "Suicide mortality rate, male (per 100,000 female population)", "Suicide mortality rate (per 100,000 population)"],  
            ["Mortality caused by road traffic injury (per 100,000 population)"], 
            ["Mortality rate, adult, female (per 1,000 female adults)", "Mortality rate, adult, male (per 1,000 male adults)"],  
            ["Death rate, crude (per 1,000 people)"], 
            ["Mortality rate, infant, female (per 1,000 live births)", "Mortality rate, infant (per 1,000 live births)", "Mortality rate, infant, male (per 1,000 live births)"]  
        ],
        "Health Services Access": [
        "Hospital beds (per 1,000 people)", "Nurses and midwives (per 1,000 people)", "Physicians (per 1,000 people)",
        "Current health expenditure (% of GDP)", "Current health expenditure per capita (current US$)", "Current health expenditure per capita, PPP (current international $)",
        "External health expenditure (% of current health expenditure)", "External health expenditure per capita (current US$)",
        "External health expenditure per capita, PPP (current international $)", "Domestic general government health expenditure (% of current health expenditure)",
        "Domestic general government health expenditure (% of GDP)", "Domestic general government health expenditure (% of general government expenditure)",
        "Domestic general government health expenditure per capita (current US$)", "Domestic private health expenditure (% of current health expenditure)",
        "Domestic private health expenditure per capita (current US$)", "Domestic private health expenditure per capita, PPP (current international $)"
    ],
        "Maternal & Child Health": [
            'Prevalence of anemia among children (% of children ages 6-59 months)',
            'Immunization, HepB3 (% of one-year-old children)', 'Immunization, DPT (% of children ages 12-23 months)',
            'Immunization, measles (% of children ages 12-23 months)', 'Immunization, measles second dose (% of children by the nationally recommended age)',
            'Births attended by skilled health staff (% of total)', 'Low-birthweight babies (% of births)',
            'Adolescent fertility rate (births per 1,000 women ages 15-19)', 'Birth rate, crude (per 1,000 people)',
            'Life expectancy at birth, female (years)', 'Life expectancy at birth, male (years)', 'Life expectancy at birth, total (years)',
            'Fertility rate, total (births per woman)', 'Sex ratio at birth (male births per female births)',
            'Number of stillbirths', 'Stillbirth rate (per 1,000 total births)'
        ],
        "Other": [ 
            "Prevalence of anemia among pregnant women (%)",
            "Prevalence of anemia among non-pregnant women (% of women ages 15-49)",
            "Prevalence of HIV, total (% of population ages 15-49)",
            "Incidence of HIV, all (per 1,000 uninfected population)",
            "Incidence of HIV, ages 15-49 (per 1,000 uninfected population ages 15-49)",
            "Incidence of malaria (per 1,000 population at risk)",
            "Risk of catastrophic expenditure for surgical care (% of people at risk)",
            "Risk of impoverishing expenditure for surgical care (% of people at risk)",
            "Tuberculosis treatment success rate (% of new cases)",
            "Tuberculosis case detection rate (%, all forms)",
            "Incidence of tuberculosis (per 100,000 people)",
            "Out-of-pocket expenditure per capita (current US$)",
            "Out-of-pocket expenditure per capita, PPP (current international $)",
            "Prevalence of undernourishment (% of population)",
            "Population growth (annual %)"
        ]
    }

    maternal_child_health_indicators = [
        "Prevalence of anemia among children (% of children ages 6-59 months)",
        "Immunization, HepB3 (% of one-year-old children)",
        "Immunization, DPT (% of children ages 12-23 months)",
        "Immunization, measles (% of children ages 12-23 months)",
        "Births attended by skilled health staff (% of total)",
        "Low-birthweight babies (% of births)",
        "Prevalence of stunting, height for age, female (% of children under 5)",
        "Prevalence of stunting, height for age, male (% of children under 5)",
        "Prevalence of wasting, weight for height, female (% of children under 5)",
        "Prevalence of wasting, weight for height, male (% of children under 5)",
        "Prevalence of wasting, weight for height (% of children under 5)",
        "Prevalence of severe wasting, weight for height, female (% of children under 5)",
        "Prevalence of severe wasting, weight for height, male (% of children under 5)",
        "Prevalence of severe wasting, weight for height (% of children under 5)",
        "Adolescent fertility rate (births per 1,000 women ages 15-19)",
        "Birth rate, crude (per 1,000 people)",
        "Fertility rate, total (births per woman)",
        "Sex ratio at birth (male births per female births)",
        "Completeness of birth registration, male (%)",
        "Completeness of birth registration (%)",
        "Number of stillbirths",
        "Stillbirth rate (per 1,000 total births)",
        "Immunization, measles second dose (% of children by the nationally recommended age)"
    ]

    @st.cache_data
    def get_filtered_data(indicator_list):
        if not indicator_list:
            return pd.DataFrame()

        if len(indicator_list) == 1:
            query = text("""
                SELECT year, indicator_name, value 
                FROM health
                WHERE indicator_name = :indicator
                ORDER BY year;
            """)
            df = pd.read_sql_query(query, engine, params={"indicator": indicator_list[0]})
        else:
            placeholders = ", ".join([f":indicator_{i}" for i in range(len(indicator_list))])
            query = text(f"""
                SELECT year, indicator_name, value 
                FROM health
                WHERE indicator_name IN ({placeholders})
                ORDER BY year;
            """)
            # Construct params dict
            params = {f"indicator_{i}": val for i, val in enumerate(indicator_list)}
            df = pd.read_sql_query(query, engine, params=params)

        df["year"] = pd.to_datetime(df["year"], format='%Y')
        df.set_index("year", inplace=True)
        df = df.pivot(columns="indicator_name", values="value").sort_index()
        return df


    def plot_data(df, indicators, title):
        if df.empty:
            return None  

        min_year, max_year = df.index.min(), df.index.max()  # Get available range
        
        fig = go.Figure()
        for indicator in indicators:
            if indicator in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.loc[min_year:max_year].index, 
                    y=df.loc[min_year:max_year, indicator],
                    mode="lines+markers",
                    name=simplify_indicator_name(indicator),
                    line=dict(color=next(color_cycle))
                ))  
        fig.update_layout(
            title=title,
            xaxis_title="Year",
            yaxis_title="Value",
            template="plotly_white"
        )
        return fig

    def simplify_indicator_name(indicator):
        if "female" in indicator.lower():
            return "Female"
        elif "male" in indicator.lower():
            return "Male"
        else:
            return "Both"

    def plot_individual_indicators(df, indicator):
        if df.empty or indicator not in df.columns:
            return None
        min_year, max_year = df.index.min(), df.index.max()  # Determine available range
        
        fig = go.Figure()   
        fig.add_trace(go.Scatter(
            x=df.loc[min_year:max_year].index,  # Filter between min/max years
            y=df.loc[min_year:max_year, indicator],
            mode="lines+markers",
            name=indicator,
            line=dict(color=next(color_cycle))
        ))
        fig.update_layout(
            title=indicator,
            xaxis_title="Year",
            yaxis_title="Value",
            template="plotly_white"
        )
        return fig
        
    def plot_grouped_indicators(df, indicator_set, title): 
        fig = go.Figure()
        for indicator in indicator_set:
            simplified_label = simplify_indicator_name(indicator)  # Extract 'Female', 'Male', 'Both'
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[indicator],
                mode="lines+markers",
                name=simplified_label,
                line=dict(color=next(color_cycle))
            ))
        fig.update_layout(
            title=title,
            xaxis_title="Year",
            yaxis_title="Value",
            template="plotly_white"
        )
        return fig

    def plot_alcohol_substance_use():
        plots = []
        grouped_plots = [
            (['Total alcohol consumption per capita, female (liters of pure alcohol, projected estimates, female 15+ years of age)',
            'Total alcohol consumption per capita, male (liters of pure alcohol, projected estimates, male 15+ years of age)',
            'Total alcohol consumption per capita (liters of pure alcohol, projected estimates, 15+ years of age)'],
                "Total Alcohol Consumption per Capita by Gender")]
        
        for indicators, title in grouped_plots:
            df = get_filtered_data(indicators)
            fig = plot_data(df, indicators, title)
            if fig:
                plots.append(fig)
        return plots
            
    def plot_disease_burden():
        plots = []
        grouped_plots = [
            (["Number of infant deaths", "Number of infant deaths, female", "Number of infant deaths, male"], "Number of Infant Deaths"),
            (["Number of under-five deaths", "Number of under-five deaths, female", "Number of under-five deaths, male"], "Number of Under-Five Deaths"),
            (["Mortality rate, under-5 (per 1,000 live births)", "Mortality rate, under-5, female (per 1,000 live births)", "Mortality rate, under-5, male (per 1,000 live births)"], "Mortality Rate Under-5"),
            (['Suicide mortality rate, female (per 100,000 female population)','Suicide mortality rate, male (per 100,000 male population)','Suicide mortality rate (per 100,000 population)'], "Suicide Mortality Rate"),
            (["Mortality rate, adult, female (per 1,000 female adults)", "Mortality rate, adult, male (per 1,000 male adults)"], "Adult Mortality Rate"),
            (["Mortality rate, infant, female (per 1,000 live births)", "Mortality rate, infant (per 1,000 live births)", "Mortality rate, infant, male (per 1,000 live births)"], "Infant Mortality Rate")
        ]

        for indicator_set, title in grouped_plots:
            df = get_filtered_data(indicator_set)
            fig = plot_data(df, indicator_set, title)
            if fig:
                plots.append(fig)

        individual_plots = [indicators[0] for indicators in indicator_groups["Disease Burden"] if len(indicators) == 1]

        for indicator in individual_plots:
            df = get_filtered_data([indicator])
            fig = plot_data(df, [indicator], indicator)
            if fig:
                plots.append(fig)
        return plots 
        
    def plot_health_services_access():
        plots = []
        for indicator in indicator_groups["Health Services Access"]:
            df = get_filtered_data([indicator])
            fig = plot_data(df, [indicator], indicator)
            if fig:
                plots.append(fig)
        return plots
            
    def plot_maternal_child_health():
        plots = []
        grouped_life_expectancy = [
            'Life expectancy at birth, female (years)',
            'Life expectancy at birth, male (years)',
            'Life expectancy at birth, total (years)'
        ]

        df_grouped = get_filtered_data(grouped_life_expectancy)
        fig = plot_data(df_grouped, grouped_life_expectancy, "Life Expectancy at Birth")
        if fig:
            plots.append(fig)

        for indicator in indicator_groups["Maternal & Child Health"]:
            if indicator not in grouped_life_expectancy:
                df = get_filtered_data([indicator])
                fig = plot_data(df, [indicator], indicator)
                if fig:
                    plots.append(fig)

        return plots

    def plot_other():
        plots = []
        for item in indicator_groups["Other"]:  
            if isinstance(item, str):  
                df = get_filtered_data([item])
                fig = plot_data(df, [item], item)
                if fig:
                    plots.append(fig)
        return plots
            
    def flatten_indicators(category):
        indicators = []
        for item in indicator_groups[category]:
            if isinstance(item, list):
                indicators.extend(item) 
            else:
                indicators.append(item)
        return indicators

    def display_plots(plots):
        num_cols = 3
        cols = st.columns(num_cols)
        for i, plot in enumerate(plots):
            with cols[i % num_cols]:  
                st.plotly_chart(plot)

    selected_category = st.selectbox("Select a category", ["-- Select a category --"] + list(indicator_groups.keys()))
    if selected_category == "-- Select a category --":
        st.info("Please select a category to view health data.")
    else:
        selected_indicators = flatten_indicators(selected_category)
        df = get_filtered_data(selected_indicators)

        plots = []
        if selected_category == "Disease Burden":
            plots.extend(plot_disease_burden())
        elif selected_category == "Health Services Access":
            plots.extend(plot_health_services_access())
        elif selected_category == "Maternal & Child Health":
            plots.extend(plot_maternal_child_health())
        elif selected_category == "Alcohol & Substance Use":
            plots.extend(plot_alcohol_substance_use())
        elif selected_category == "Other":
            plots.extend(plot_other())

        display_plots(plots)