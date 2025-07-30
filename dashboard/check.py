import streamlit as st
from components.logged_header import logged_header # type: ignore
st.set_page_config(layout="wide")
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore")
from components.styles import apply_global_styles # type: ignore
apply_global_styles()
import streamlit.components.v1 as components

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

    SE_tabs = st.tabs([
        "Poverty and Inequality",
        "Migration"
    ])

    with SE_tabs[0]:
        from tabs_data.inequality_poverty_data import get_inequality_poverty_data # type: ignore
        get_inequality_poverty_data()

    with SE_tabs[1]:
        from tabs_data.migration_data import get_migration_data # type: ignore
        get_migration_data()

        

with tabs[3]:
    VI_tabs = st.tabs([
    "Age",
    "Gender",
    "Health",
    "Urban development"
])

    with VI_tabs[0]:

        from tabs_data.age_data import get_age_data  # type: ignore
        get_age_data()
            
    with VI_tabs[1]:

        from tabs_data.gender_data import get_gender_data  # type: ignore
        get_gender_data()

    with VI_tabs[2]:

        from tabs_data.health_data import get_health_data  # type: ignore
        get_health_data()
        
    with VI_tabs[3]:

        from tabs_data.urban_development_data import get_urban_development_data # type: ignore
        get_urban_development_data()

with tabs[4]:
    from tabs_data.resilience_data import get_resilience_data  # type: ignore
    get_resilience_data()

with tabs[5]:
    from tabs_data.humanitarian_data import get_humanitarian_data # type: ignore
    get_humanitarian_data()

with tabs[6]:
    with open("new_map.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    components.html(html_content, height=500, width=1200, scrolling=False)
