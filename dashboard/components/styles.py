import streamlit as st

def apply_global_styles():
    st.markdown("""
        <style>
            MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .block-container {padding-top: 0rem;}
            h1:hover a, h2:hover a, h3:hover a, h4:hover a, h5:hover a, h6:hover a {display: none !important;}
        </style>
    """, unsafe_allow_html=True)
