import streamlit as st
st.set_page_config(layout="wide")
import streamlit_authenticator as stauth  # type: ignore
import streamlit.components.v1 as components
from tabs_data.credentials import user_check  # type: ignore
from tabs_data.indicators_data import (get_poverty_data, get_health_data, get_environment_data, get_infrastructure_data,)  # type: ignore

# Set page config upfront
st.set_page_config(layout="wide")

# Style loader function
def load_custom_css(css_file_path):
    with open(css_file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Apply your global styles ASAP before creating widgets
from components.styles import apply_global_styles  # type: ignore
apply_global_styles()
load_custom_css("components/styles.css")

# Load credentials and create the authenticator
credentials = user_check()
authenticator = stauth.Authenticate(
    credentials,
    cookie_name="AI_db_view",
    key="2160",  # Use your own secure key string
    cookie_expiry_days=1/24,
)

# Header function with image + logout + separator
def logged_header(authenticator):
    left_col, _, right_col = st.columns([3, 5, 1])
    with left_col:
        st.image(
            "https://cruzroja.org.ar/observatorio-humanitario/wp-content/uploads/2020/09/logos-cra-mr-2023.png",
            width=400,
        )
    with right_col:
        st.write("") 
        st.write("")
        if st.button("Logout"):
            st.session_state.clear()
            st.switch_page('homepage.py')

    st.markdown(
        """
        <style>
        .header-divider {
            border-bottom: 2px solid #eaeaea;
            margin-top: 0;
            margin-bottom: 0.3rem;
            width: 100%;
        }
        </style>
        <div class="header-divider"></div>
        """,
        unsafe_allow_html=True,
    )

logged_header(authenticator)

# Main content container opening div if used in your CSS layout
st.markdown('<div class="main-content">', unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; font-size: 2.5em; font-weight: bold;'>ARGENTINA</div>",
    unsafe_allow_html=True,
)

# Inject CSS to customize tab fonts globally
st.markdown(
    """
    <style>
    /* Customize font size, weight, color of Streamlit tabs */
    .stTabs [data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 20px !important;
        font-weight: 400 !important;
        color: #7a2e2b !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Create tabs with your seven indicators
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
        from tabs_data.country_profile import get_country_data  # type: ignore
        get_country_data()

    with tabs[1]:
        CLI_tabs = st.tabs([
            "Temperature",
            "Precipitation",
            "Droughts and Floods",
            "Wildfires"
        ])

        with CLI_tabs[0]:
            from tabs_data.temperature_data import get_temperature_data  # type: ignore
            get_temperature_data()

        with CLI_tabs[1]:
            from tabs_data.precipitation_data import get_precipitation_data  # type: ignore
            get_precipitation_data()

        with CLI_tabs[2]:
            from tabs_data.hydro_droughts_data import get_hydro_data  # type: ignore
            from tabs_data.metero_droughts_data import get_metero_data  # type: ignore
            get_hydro_data()
            get_metero_data()

        with CLI_tabs[3]:
            from tabs_data.wildfires_data import get_wildfires_data  # type: ignore
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