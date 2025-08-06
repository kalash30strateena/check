import streamlit as st
st.set_page_config(layout="wide")
from components.styles import apply_global_styles  # type: ignore
apply_global_styles()
import re
import bcrypt  # type: ignore
import psycopg2
import psycopg2.extras
from components.header import show_header  # type: ignore
show_header()
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore")
st.session_state["logged_in"] = False


# CSS for styling
st.markdown("""
    <style>
    .custom-form-container {
        background-color: #000000;
        padding: 2.5rem 2rem 2rem 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.07);
        max-width: 400px;
        margin: 2rem auto;
    }
    .custom-form-container h2 {
        color: #2a52be;
        text-align: center;
        margin-bottom: 2rem;
    }
    label {
        color: #2a52be !important;
        font-weight: 600 !important;
    }
    .stTextInput input {
        background-color: #eaf0fb;
        color: #1a1a1a;
        border-radius: 8px;
    }
    .stButton button {
        background-color: #2a52be;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        padding: 0.5rem 1.2rem;
    }
    .stButton button:hover {
        background-color: #1e3a8a;
        color: #fff;
    }
    </style>
""", unsafe_allow_html=True)


# Database connection parameters - UPDATE these according to your setup
conn_params = {
    'dbname': 'new_db',
    'user': 'postgres',
    'password': 'Strateena@check',
    'host': '34.93.35.170',
    'port': 5432
}


# Registration form layout
st.markdown("<h2 align=center>Register</h2>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([9, 8, 9])  # 3-column layout


with col2:
    with st.form("register_form"):
        fname_col, lname_col = st.columns(2)
        with fname_col:
            first_name = st.text_input('First name')
        with lname_col:
            last_name = st.text_input('Last name')
        email = st.text_input('Enter your Email address (used as username)')
        password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        register_btn = st.form_submit_button("Register")

    if register_btn:
        # Input validation
        if not all([first_name.strip(), last_name.strip(), email.strip(), password, confirm_password]):
            st.error("All fields are required.")
        elif password != confirm_password:
            st.error("Passwords do not match!")
        elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            st.warning("Invalid email format.")
        elif len(password) < 8:
            st.warning("Password must be at least 8 characters long.")
        else:
            # Hash password securely
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            try:
                # Connect to the database
                with psycopg2.connect(**conn_params) as conn:
                    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                        # Check if username or email exists (same value here)
                        cur.execute("SELECT 1 FROM users WHERE username=%s OR email=%s", (email, email))
                        if cur.fetchone():
                            st.error("Username or email already exists.")
                        else:
                            insert_sql = """
                                INSERT INTO users (first_name, last_name, username, email, password_hash)
                                VALUES (%s, %s, %s, %s, %s)
                            """
                            # Insert same value in username and email fields
                            cur.execute(insert_sql, (first_name, last_name, email, email, hashed_pw))
                            conn.commit()
                            st.success("Registration successful! You can now login.")
                            st.switch_page("pages/Login.py")

            except Exception as e:
                st.error(f"Database error: {e}")
