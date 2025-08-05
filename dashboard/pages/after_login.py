import streamlit as st

# --- Restore login flags from URL query params if missing or False in session state ---
query_params = st.query_params

if not st.session_state.get("logged_in", False):
    if query_params.get("logged_in", ["false"])[0].lower() == "true":
        st.session_state["logged_in"] = True

if not st.session_state.get("from_view_indicators", False):
    if query_params.get("from_view_indicators", ["false"])[0].lower() == "true":
        st.session_state["from_view_indicators"] = True

# --- Redirect if not logged in after restoring ---
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/Login.py")
    st.stop()

if not st.session_state.get("from_view_indicators", False):
    st.switch_page("pages/Login.py")
    st.stop()

from components.logged_header import logged_header # type: ignore
st.set_page_config(layout="wide")
from components.styles import apply_global_styles # type: ignore
apply_global_styles()

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore")

import streamlit.components.v1 as components
from tabs_data.indicators_data import (get_poverty_data,get_health_data,get_environment_data,get_infrastructure_data) # type: ignore
logged_header()

def load_custom_css(css_file_path):
    with open(css_file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the style at runtime
load_custom_css("components/styles.css")


st.markdown('<div class="main-content">', unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; font-size: 2.5em; font-weight: bold;'>ARGENTINA</div>",
    unsafe_allow_html=True
)

tabs = st.tabs([
    "Country Profile",
    "Climate Indicators",
    "Socio-economic Indicators",
    "Vulnerability Indicators",
    "Resilience Indicators",
    "Humanitarian Indicators",
    "Populations"
])

with st.spinner("Loading Data..."):
    with tabs[0]:
        from tabs_data.country_profile import get_country_data # type: ignore
        get_country_data()

    with tabs[1]:
        
        CLI_tabs = st.tabs([
        "Temperature",
        "Precipitation",
        "Droughts and Floods",
        "Wildfires"])
        
        with CLI_tabs[0]:
            from tabs_data.temperature_data import get_temperature_data # type: ignore
            get_temperature_data()

        with CLI_tabs[1]:
            from tabs_data.precipitation_data import get_precipitation_data # type: ignore
            get_precipitation_data()

        with CLI_tabs[2]:
            from tabs_data.hydro_droughts_data import get_hydro_data # type: ignore
            from tabs_data.metero_droughts_data import get_metero_data # type: ignore
            get_hydro_data()
            get_metero_data()
            
        with CLI_tabs[3]:
            from tabs_data.wildfires_data import get_wildfires_data # type: ignore
            get_wildfires_data()
            
    with tabs[2]:
        get_poverty_data()        

    with tabs[3]:
        get_health_data()

    with tabs[4]:
        get_infrastructure_data()

    with tabs[5]:
        get_environment_data()

    with tabs[6]:
        with open("new_map.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        components.html(html_content, height=500, width=1200, scrolling=False)
