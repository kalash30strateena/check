import streamlit as st

st.markdown("""
    <style>
        MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 0rem; /* Adjust this value as needed */
        }
        
        h1:hover a, h2:hover a, h3:hover a, h4:hover a, h5:hover a, h6:hover a {
        display: none !important;
        }
        
    </style>
""", unsafe_allow_html=True)

def show_header():
    if "language" not in st.session_state:
        st.session_state["language"] = "English"

    st.markdown("""
    <style>
    /* Header styling */
    .custom-header {{
        background-color: #ffffff;
        font-size: 20.5px;
        padding: 0px 0px;
        border-bottom: 2px solid #eaeaea;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0px;
    }}
    .custom-header img {{
        height: 100px;
    }}
    .custom-header .header-center {{
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    .custom-header .header-links {{
        display: flex;
        align-items: center;
    }}
    .custom-header .header-links a {{
        color: #7a2e2b;
        margin-left: 10px;
        font-size: 16px;
        text-decoration: none;
        padding: 8px 8px;
        border-radius: 18px;
        transition: background 0.2s, color 0.2s;
    }}
    .custom-header .header-links a:hover {{
        background-color: #b22222;
        color: #fff !important;
        border-radius: 18px;
        text-decoration: none;
    }}
    .language-select {{
        margin-right: 30px;
        font-size: 16px;
        padding: 4px 8px;
        border-radius: 4px;
        border: 1px solid #ccc;
        color: #7a2e2b;
        background-color: #f9f9f9;
    }}
    .stTabs [data-baseweb="tab"] {{
        margin-right: 7px !important;
    }}
    .stTabs [data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {{
        font-size: 20px !important;
        color: #7a2e2b;
        transition: color 0.2s;
    }}
    /* Active (clicked) tab styling */
    .stTabs [data-baseweb="tab"][aria-selected="true"] > div[data-testid="stMarkdownContainer"] > p {{
        color: #e53935 !important; 
    }}
    </style>

    <div class="custom-header">
        <div>
    <a href="/" target="_self">
        <img src="https://cruzroja.org.ar/observatorio-humanitario/wp-content/uploads/2020/09/logos-cra-mr-2023.png" alt="Logo" width="400">
    </a>
    </div>
        <div class="header-center"></div>
        <div class="header-links">
            <form action="" method="get" id="lang-form">
                <select name="language" class="language-select" onchange="document.getElementById('lang-form').submit();">
                    <option value="English" {eng_selected}>English</option>
                    <option value="Español" {esp_selected}>Español</option>
                </select>
            </form>
            <a href="/" target="_self">Home</a>
            <a href="/Login" target="_self">Login</a>
            <a href="/Register" target="_self">Register</a>
        </div>
    </div>
    """.format(
        eng_selected="selected" if st.session_state.get("language", "English") == "English" else "",
        esp_selected="selected" if st.session_state.get("language", "English") == "Español" else "",
    ), unsafe_allow_html=True)

    st.markdown('<div class="main-content">', unsafe_allow_html=True)
