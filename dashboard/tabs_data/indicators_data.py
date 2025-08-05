## code for poverty, health, infrastructure, environment in one file with each functions 

import streamlit as st
from tabs_data.indicators_utils import fetch_categories, fetch_indicators, plotly_indicators # type: ignore

def get_poverty_data():
    categories_df = fetch_categories("P")
    selected_category = st.selectbox("Select Poverty Category", categories_df['category_name'])
    if selected_category:
        category_id = int(categories_df[categories_df['category_name'] == selected_category]['category_id'].values[0])
        indicators_df = fetch_indicators(category_id)
        if not indicators_df.empty:
            plots = plotly_indicators(indicators_df)
            for i in range(0, len(plots), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(plots):
                        with cols[j]:
                            st.plotly_chart(plots[i + j], use_container_width=True)
        else:
            st.warning("No indicator data found.")

def get_health_data():
    categories_df = fetch_categories("H")
    selected_category = st.selectbox("Select Health Category", categories_df['category_name'])
    if selected_category:
        category_id = int(categories_df[categories_df['category_name'] == selected_category]['category_id'].values[0])
        indicators_df = fetch_indicators(category_id)
        if not indicators_df.empty:
            plots = plotly_indicators(indicators_df)
            for i in range(0, len(plots), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(plots):
                        with cols[j]:
                            st.plotly_chart(plots[i + j], use_container_width=True)
        else:
            st.warning("No indicator data found.")

def get_environment_data():
    categories_df = fetch_categories("E")
    selected_category = st.selectbox("Select Environment Category", categories_df['category_name'])
    if selected_category:
        category_id = int(categories_df[categories_df['category_name'] == selected_category]['category_id'].values[0])
        indicators_df = fetch_indicators(category_id)
        if not indicators_df.empty:
            plots = plotly_indicators(indicators_df)
            for i in range(0, len(plots), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(plots):
                        with cols[j]:
                            st.plotly_chart(plots[i + j], use_container_width=True)
        else:
            st.warning("No indicator data found.")

def get_infrastructure_data():
    categories_df = fetch_categories("I")
    selected_category = st.selectbox("Select Infrastructure Category", categories_df['category_name'])
    if selected_category:
        category_id = int(categories_df[categories_df['category_name'] == selected_category]['category_id'].values[0])
        indicators_df = fetch_indicators(category_id)
        if not indicators_df.empty:
            plots = plotly_indicators(indicators_df)
            for i in range(0, len(plots), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(plots):
                        with cols[j]:
                            st.plotly_chart(plots[i + j], use_container_width=True)
        else:
            st.warning("No indicator data found.")
