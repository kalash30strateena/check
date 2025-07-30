def get_humanitarian_data():
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from tabs_data.credentials import cred # type: ignore
    engine=cred()
    # -------- Agriculture mappings --------
    agriculture_mapping = {
        "Fertilizer consumption (% of fertilizer production)": "Agricultural Inputs",
        "Fertilizer consumption (kilograms per hectare of arable land)": "Agricultural Inputs",
        "Annual freshwater withdrawals, agriculture (% of total freshwater withdrawal)": "Agricultural Value & GDP Contribution",
        "Agriculture, forestry, and fishing, value added (current US$)": "Agricultural Value & GDP Contribution",
        "Agriculture, forestry, and fishing, value added (% of GDP)": "Agricultural Value & GDP Contribution",
        "Employment in agriculture, female (% of female employment) (modeled ILO estimate)": "Agricultural Value & GDP Contribution",
        "Employment in agriculture, male (% of male employment) (modeled ILO estimate)": "Agricultural Value & GDP Contribution",
        "Employment in agriculture (% of total employment) (modeled ILO estimate)": "Agricultural Value & GDP Contribution",
        "Agricultural land (sq. km)": "Crop Production & Yield",
        "Agricultural land (% of land area)": "Crop Production & Yield",
        "Arable land (hectares)": "Crop Production & Yield",
        "Arable land (hectares per person)": "Crop Production & Yield",
        "Arable land (% of land area)": "Crop Production & Yield",
        "Land under cereal production (hectares)": "Crop Production & Yield",
        "Permanent cropland (% of land area)": "Crop Production & Yield",
        "Forest area (% of land area)": "Crop Production & Yield",
        "Agricultural irrigated land (% of total agricultural land)": "Crop Production & Yield",
        "Cereal production (metric tons)": "Crop Production & Yield",
        "Crop production index (2014–2016 = 100)": "Crop Production & Yield",
        "Food production index (2014–2016 = 100)": "Crop Production & Yield",
        "Livestock production index (2014–2016 = 100)": "Crop Production & Yield",
        "Cereal yield (kg per hectare)": "Crop Production & Yield",
        "Forest area (sq. km)": "Forestry & Land Use",
        "Agricultural raw materials imports (% of merchandise imports)": "Other",
        "Agricultural raw materials exports (% of merchandise exports)": "Other",
        "Access to electricity, rural (% of rural population)": "Rural Population & Development",
        "Rural population": "Rural Population & Development",
        "Rural population growth (annual %)": "Rural Population & Development",
        "Rural population (% of total population)": "Rural Population & Development"
    }
    normalized_mapping = {k.strip().lower(): v for k, v in agriculture_mapping.items()}

    # -------- Environment indicator categories --------
    indicator_categories = {
        "Agriculture & Rural Development": [
            'Agricultural land (% of land area)', 'Arable land (% of land area)', 'Forest area (sq. km)', 'Forest area (% of land area)',
            'Access to clean fuels and technologies for cooking, rural (% of rural population)', 'Terrestrial protected areas (% of total land area)',
            'Forest rents (% of GDP)','People using at least basic drinking water services, rural (% of rural population)',
            'People using at least basic sanitation services, rural (% of rural population)'
        ],
        "Environment & Climate": {
            "Pollution": [
                'PM2.5 air pollution, mean annual exposure (micrograms per cubic meter)',
                'PM2.5 pollution, population exposed to levels exceeding WHO Interim Target-1 value (% of total)',
                'PM2.5 pollution, population exposed to levels exceeding WHO Interim Target-2 value (% of total)',
                'PM2.5 pollution, population exposed to levels exceeding WHO Interim Target-3 value (% of total)',
                'PM2.5 air pollution, population exposed to levels exceeding WHO guideline value (% of total)'
            ],
            "Greenhouse Gas Emission": [
                'Total greenhouse gas emissions including LULUCF (Mt CO2e)','Total greenhouse gas emissions excluding LULUCF (Mt CO2e)',
                'Total greenhouse gas emissions excluding LULUCF per capita (t CO2e/capita)', 'Total greenhouse gas emissions excluding LULUCF (% change from 1990)'
            ],
            "Methane (CH4) Emission": [
                'Methane (CH4) emissions from Agriculture (Mt CO2e)','Methane (CH4) emissions from Building (Energy) (Mt CO2e)',
                'Methane (CH4) emissions from Fugitive Emissions (Energy) (Mt CO2e)','Methane (CH4) emissions from Industrial Combustion (Energy) (Mt CO2e)',
                'Methane (CH4) emissions from Industrial Processes (Mt CO2e)','Methane (CH4) emissions (total) excluding LULUCF (Mt CO2e)',
                'Methane (CH4) emissions from Power Industry (Energy) (Mt CO2e)','Methane (CH4) emissions from Transport (Energy) (Mt CO2e)',
                'Methane (CH4) emissions from Waste (Mt CO2e)', 'Methane (CH4) emissions (total) excluding LULUCF (% change from 1990)'
            ],
            "Carbon Dioxide (CO2) Emission": [
                'Carbon dioxide (CO2) emissions from Agriculture (Mt CO2e)', 'Carbon dioxide (CO2) emissions from Building (Energy) (Mt CO2e)',
                'Carbon dioxide (CO2) emissions from Fugitive Emissions (Energy) (Mt CO2e)','Carbon dioxide (CO2) emissions from Industrial Combustion (Energy) (Mt CO2e)',
                'Carbon dioxide (CO2) emissions from Industrial Processes (Mt CO2e)','Carbon dioxide (CO2) net fluxes from LULUCF - Deforestation (Mt CO2e)',
                'Carbon dioxide (CO2) net fluxes from LULUCF - Forest Land (Mt CO2e)','Carbon dioxide (CO2) net fluxes from LULUCF - Total excluding non-tropical fires (Mt CO2e)',
                'Carbon dioxide (CO2) net fluxes from LULUCF - Other Land (Mt CO2e)','Carbon dioxide (CO2) net fluxes from LULUCF - Organic Soil (Mt CO2e)',
                'Carbon dioxide (CO2) emissions (total) excluding LULUCF (Mt CO2e)','Carbon dioxide (CO2) emissions excluding LULUCF per capita (t CO2e/capita)',
                'Carbon dioxide (CO2) emissions from Power Industry (Energy) (Mt CO2e)'
            ],
            "F Gas Emission": [
                'F-gases emissions from Industrial Processes (Mt CO2e)'
            ],
            "Nitrous Oxide (N2O) Emission": [
                'Nitrous oxide (N2O) emissions from Agriculture (Mt CO2e)','Nitrous oxide (N2O) emissions from Building (Energy) (Mt CO2e)',
                'Nitrous oxide (N2O) emissions from Fugitive Emissions (Energy) (Mt CO2e)','Nitrous oxide (N2O) emissions from Industrial Combustion (Energy) (Mt CO2e)', 
                'Nitrous oxide (N2O) emissions from Industrial Processes (Mt CO2e)','Nitrous oxide (N2O) emissions (total) excluding LULUCF (Mt CO2e)', 
                'Nitrous oxide (N2O) emissions from Power Industry (Energy) (Mt CO2e)','Nitrous oxide (N2O) emissions from Transport (Energy) (Mt CO2e)',
                'Nitrous oxide (N2O) emissions from Waste (Mt CO2e)','Nitrous oxide (N2O) emissions (total) excluding LULUCF (% change from 1990)'
            ]
        },
        "Health": [
            'Mortality rate attributed to unintentional poisoning (per 100,000 population)',
            'Mortality rate attributed to unintentional poisoning, female (per 100,000 female population)',
            'Mortality rate attributed to unintentional poisoning, male (per 100,000 male population)',
            'Mortality rate attributed to household and ambient air pollution, age-standardized (per 100,000 population)',
            'Mortality rate attributed to unsafe water, unsafe sanitation and lack of hygiene (per 100,000 population)'
        ],
        "Infrastructure & Urban Development": [
            'Access to clean fuels and technologies for cooking, urban (% of urban population)','Access to electricity (% of population)', 
            'Urban population living in areas where elevation is below 5 meters (% of total population)','Population living in slums (% of urban population)',
            'People using at least basic sanitation services, urban (% of urban population)','People using at least basic drinking water services, urban (% of urban population)',
            'People practicing open defecation, urban (% of urban population)','People using safely managed sanitation services, urban (% of urban population)'
        ],
        "Other" : [
            'Energy intensity level of primary energy (MJ/$2017 PPP GDP)','Renewable energy consumption (% of total final energy consumption)','Plant species (higher), threatened', 
            'Mammal species, threatened','Population living in areas where elevation is below 5 meters (% of total population)',
            'Water productivity, total (constant 2015 US$ GDP per cubic meter of total freshwater withdrawal)',  'Level of water stress: freshwater withdrawal as a proportion of available freshwater resources',
            'Marine protected areas (% of territorial waters)','Terrestrial and marine protected areas (% of total territorial area)','Coal rents (% of GDP)','Mineral rents (% of GDP)', 
            'Natural gas rents (% of GDP)','Oil rents (% of GDP)', 'Total natural resources rents (% of GDP)','People using at least basic drinking water services (% of population)',
            'People using at least basic sanitation services (% of population)','People practicing open defecation (% of population)','People using safely managed sanitation services (% of population)'
        ]
    }

    # -------- Data loading helpers --------
    @st.cache_data(show_spinner="Loading agricultural data...")
    def load_agriculture_data():
        
        df = pd.read_sql("SELECT year, indicator_name, value FROM agriculture", engine)
        df['indicator_name'] = df['indicator_name'].astype(str).str.strip().str.lower()
        df['year'] = pd.to_datetime(df['year'], format='%Y', errors='coerce')
        return df

    @st.cache_data(show_spinner="Loading environment data...")
    def get_filtered_env_data(indicator_list):
        # Ensure it's a tuple for SQL parameterization
        indicators_tuple = tuple(indicator_list)
        
        query = """
            SELECT year, indicator_name, value 
            FROM environment 
            WHERE indicator_name IN %(indicators)s
            ORDER BY year;
        """
        
        df = pd.read_sql(query, engine, params={"indicators": indicators_tuple})
        
        df["year"] = pd.to_datetime(df["year"], format='%Y', errors='coerce')
        df.set_index("year", inplace=True)
        df = df.pivot(columns="indicator_name", values="value").sort_index()
        
        return df


    st.header("Agriculture")
    agriculture_categories = ["-- Select Category --"] + sorted(set(normalized_mapping.values()))
    selected_category = st.selectbox("Select a Category", agriculture_categories, key="agriculture_category")

    if selected_category == "-- Select Category --":
        st.info("Please select an agricultural category to see data.")
    else:
        agri_df = load_agriculture_data()
        agri_indicators = [k for k, v in normalized_mapping.items() if v == selected_category]
        filtered_df = agri_df[
            agri_df['indicator_name'].isin([i.strip().lower() for i in agri_indicators])
        ]
        color_cycle = ['orange', 'blue', 'green', 'purple']
        for i in range(0, len(agri_indicators), 3):
            cols = st.columns(3)
            for j, indicator in enumerate(agri_indicators[i:i+3]):
                indf = filtered_df[filtered_df['indicator_name'] == indicator.lower()]
                if not indf.empty:
                    color = color_cycle[(i + j) % len(color_cycle)]
                    fig = px.bar(
                        indf,
                        x="year",
                        y="value",
                        title=indicator.title(),
                        color_discrete_sequence=[color]
                    )
                    cols[j].plotly_chart(fig, use_container_width=True)

    st.header("Environment")
    env_categories = ["-- Select Category --"] + list(indicator_categories.keys())
    selected_main_category = st.selectbox("Select Environment Category", env_categories, key="env_main_category")

    if selected_main_category == "-- Select Category --":
        st.info("Please select an environment category and subcategory to view data.")
    elif isinstance(indicator_categories[selected_main_category], dict):
        subcategories = ["-- Select Subcategory --"] + list(indicator_categories[selected_main_category].keys())
        selected_subcategory = st.selectbox("Select Subcategory", subcategories)
        if selected_subcategory == "-- Select Subcategory --":
            st.info("Please select an environment subcategory to view data.")
        else:
            indicators = indicator_categories[selected_main_category][selected_subcategory]
            df_env = get_filtered_env_data(indicators)
            rows = [st.columns(3) for _ in range((len(df_env.columns) + 2) // 3)]
            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
            for i, indicator in enumerate(df_env.columns):
                color = colors[i % len(colors)]
                filtered_col = df_env[indicator].dropna()
                if not filtered_col.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=filtered_col.index, y=filtered_col.values,
                                            mode="lines+markers", name=indicator, line=dict(color=color)))
                    fig.update_layout(title=indicator, xaxis_title="Year", yaxis_title="Value",
                                    width=450, height=400, template="plotly_white",
                                    showlegend=False)
                    row = rows[i // 3]
                    row[i % 3].plotly_chart(fig)
    else:
        indicators = indicator_categories[selected_main_category]
        df_env = get_filtered_env_data(indicators)
        rows = [st.columns(3) for _ in range((len(df_env.columns) + 2) // 3)]
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
        for i, indicator in enumerate(df_env.columns):
            color = colors[i % len(colors)]
            filtered_col = df_env[indicator].dropna()
            if not filtered_col.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=filtered_col.index, y=filtered_col.values,
                                        mode="lines+markers", name=indicator, line=dict(color=color)))
                fig.update_layout(title=indicator, xaxis_title="Year", yaxis_title="Value",
                                width=450, height=400, template="plotly_white",
                                showlegend=False)
                row = rows[i // 3]
                row[i % 3].plotly_chart(fig)