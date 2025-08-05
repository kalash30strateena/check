import streamlit as st
def logged_header(authenticator):
    if "language" not in st.session_state:
        st.session_state["language"] = "English"

    # Use columns for horizontal layout
    left_col, right_col = st.columns([3, 1])

    # Left: display logo image with fixed height
    with left_col:
        st.image(
            "https://cruzroja.org.ar/observatorio-humanitario/wp-content/uploads/2020/09/logos-cra-mr-2023.png",
            width=400,
        )

    # Right: logout button
    with right_col:
        st.write("")  # vertical spacer
        if st.button("Logout"):
            authenticator.logout()
            st.session_state.clear()
            st.switch_page('homepage.py')

    # Add a horizontal divider line below header as a grey line
    st.markdown(
        """
        <style>
        .header-divider {
            border-bottom: 2px solid #eaeaea;
            margin-top: 0;
            margin-bottom: 1rem;
        }
        </style>
        <div class="header-divider"></div>
        """,
        unsafe_allow_html=True,
    )
