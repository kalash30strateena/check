import streamlit as st
st.set_page_config(layout="wide")
from components.styles import apply_global_styles
apply_global_styles()
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore")
from components.header import show_header 
show_header()
from tabs_data.credentials import cred # type: ignore
engine=cred()
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore")

st.markdown("<div style='text-align: center; font-size: 2.5em; font-weight: bold;'>ARGENTINA</div>", unsafe_allow_html=True)
st.markdown(
"""
<div style="background-color:#e8e1e1; color:#99111a; padding:15px; border-radius:8px; font-size:16px;">
    Please register or login to access all the indicators on the AI dashboard
</div>
""",
unsafe_allow_html=True
)
st.session_state["logged_in"] = False
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
    
for i in range(1, 7):
    with tabs[i]:
        st.markdown("""
        <div style="
            pointer-events: none;
            opacity: 1;
            background: #e8e1e1;
            color: #99111a;
            padding: 15px;
            border-radius: 10px;
            text-align: center;">
            <h3>Login to view the content</h3>
        </div>
        """, unsafe_allow_html=True)
        
