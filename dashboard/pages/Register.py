import streamlit as st
st.set_page_config(layout="wide")
from components.styles import apply_global_styles # type: ignore
apply_global_styles()
import re
import bcrypt
import psycopg2
from components.header import show_header # type: ignore
show_header()


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

DB_CONFIG = {
        'dbname': 'postgres',
        'user': 'postgres.ajbcqqwgdmfscvmkbtqz',
        'password': 'StrateenaAIML',
        'host': 'aws-0-ap-south-1.pooler.supabase.com',
        'port': 6543
}

# --- Database Connection ---
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# --- Form Layout ---
st.markdown("<h2 align=center>Register</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([9, 8, 9])  # Creates a 3-column layout

with col2:
    with st.form("register_form"):
        fname_col, lname_col = st.columns(2)
        with fname_col:
            first_name = st.text_input('First name')
        with lname_col:
            last_name = st.text_input('Last name')
        email = st.text_input('Enter your Email address')
        username = st.text_input("Choose a Username")
        password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        register_btn = st.form_submit_button("Register")

    if register_btn:
        # --- Input Validation ---
        if not all([first_name.strip(), last_name.strip(), email.strip(), username.strip(), password, confirm_password]):
            st.error("All fields are required.")
        elif password != confirm_password:
            st.error("Passwords do not match!")
        elif len(username) < 3 or len(password) < 8:
            st.warning("Username must be at least 3 characters and password at least 8 characters.")
        elif not re.match(r"^[a-zA-Z0-9_]+$", username):
            st.warning("Username can only contain letters, numbers, and underscores.")
        elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            st.warning("Invalid email format.")
        else:
            # --- Hash Password ---
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            # --- Check for Duplicates and Insert ---
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                # Check if username or email already exists
                cur.execute("SELECT 1 FROM users WHERE username=%s OR email=%s", (username, email))
                if cur.fetchone():
                    st.error("Username or email already exists.")
                else:
                    cur.execute("""
                        INSERT INTO users (first_name, last_name, username, email, password_hash)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (first_name, last_name, username, email, hashed_pw))
                    conn.commit()
                    st.success("Registration successful! You can now login.")
                cur.close()
                conn.close()
                st.switch_page("pages/Login.py")
            except Exception as e:
                st.error(f"Database error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)
