import streamlit as st
import streamlit_authenticator as stauth # type: ignore
from tabs_data.credentials import user_check  # type: ignore
from components.header import show_header  # type: ignore
from components.styles import apply_global_styles  # type: ignore

apply_global_styles()
show_header()

st.set_page_config(layout="wide")

# Load credentials from DB
credentials = user_check()

col1, col2, col3 = st.columns([8,9,8])
with st.spinner("Verifying credentials..."):
    with col2:
        st.info("Login using Email and password.")
        # Instantiate the authenticator
        authenticator = stauth.Authenticate(
            credentials,
            cookie_name="AI-db-view",
            key="2160",  # Change to your own secure random key
            cookie_expiry_days=1/24
        )

        authenticator.login(location="main")

        # Retrieve authentication state from session_state
        authentication_status = st.session_state.get("authentication_status")
        name = st.session_state.get("name")
        username = st.session_state.get("username")

        if authentication_status:
            st.success(f"Welcome {name}! Redirecting to dashboard...")
            st.switch_page('pages/after_login.py')
        elif authentication_status is False:
            st.error("Incorrect email or password. Please try again.")
