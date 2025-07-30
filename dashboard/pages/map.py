import streamlit as st
st.set_page_config(layout="wide")

import streamlit.components.v1 as components

with open("new_map.html", "r", encoding="utf-8") as f:
    html_content = f.read()

components.html(html_content, height=500, width=1200, scrolling=False)
