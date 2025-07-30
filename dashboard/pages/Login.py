import streamlit as st
from components.styles import apply_global_styles  # type: ignore
st.set_page_config(layout="wide")
apply_global_styles()
import psycopg2
import bcrypt #type: ignore
import datetime
from components.header import show_header  # type: ignore
show_header()

st.markdown("""
    <style>
        MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 0rem;}
        h1:hover a, h2:hover a, h3:hover a, h4:hover a, h5:hover a, h6:hover a {display: none !important;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)

DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres.ajbcqqwgdmfscvmkbtqz',
    'password': 'StrateenaAIML',
    'host': 'aws-0-ap-south-1.pooler.supabase.com',
    'port': 6543
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'from_view_indicators' not in st.session_state:
    st.session_state.from_view_indicators = False

col1, col2, col3 = st.columns([9, 8, 9])

with col2:
    if st.session_state.logged_in:
        st.success(f"Already logged in as {st.session_state.user} ({st.session_state.role})")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.role = None
            st.session_state.from_view_indicators = False
            st.experimental_rerun()
        # Immediate redirect after login
        st.session_state.from_view_indicators = True
        st.switch_page('pages/after_login.py')
        st.stop()
    else:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")

        if login_btn:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                try:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute("SELECT user_id, email, password_hash, role FROM users WHERE email = %s", (email,))
                    user = cur.fetchone()
                    if user:
                        user_id, db_email, db_password_hash, role = user
                        if bcrypt.checkpw(password.encode(), db_password_hash.encode()):
                            try:
                                cur.execute(
                                    "UPDATE users SET last_login = %s WHERE user_id = %s",
                                    (datetime.datetime.utcnow(), user_id)
                                )
                                conn.commit()
                            except Exception as e:
                                st.warning(f"Could not update last_login: {e}")
                            st.session_state.logged_in = True
                            st.session_state.user = db_email
                            st.session_state.role = role
                            st.session_state.from_view_indicators = True
                            st.query_params(logged_in="true", from_view_indicators="true")
                            st.success("Login successful! Redirecting...")
                            cur.close()
                            conn.close()
                            st.switch_page('pages/after_login.py')
                            st.stop()
                        else:
                            st.error("Incorrect password.")
                    else:
                        st.error("Invalid email or password.")
                    cur.close()
                    conn.close()
                except Exception as e:
                    st.error(f"Database error: {e}")
        st.markdown(
            "If not registered, <a href='Register' target='_self'><b>Register</b></a>",
            unsafe_allow_html=True
        )
