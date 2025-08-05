def cred():
    from sqlalchemy import create_engine
    import urllib
    
    DB_CONFIG = {
        'dbname': 'new_db',
        'user': 'postgres',
        'password': 'Strateena@check',
        'host': '34.93.35.170',
        'port': 5432
    }
    
    def get_engine():
        password = urllib.parse.quote_plus(DB_CONFIG['password'])
        url = (
            f"postgresql+psycopg2://{DB_CONFIG['user']}:{password}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
        )
        return create_engine(url)
        
    return get_engine()

import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'dbname': 'new_db',
    'user': 'postgres',
    'password': 'Strateena@check',
    'host': '34.93.35.170',
    'port': 5432
}

def db_query(query):
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            results = cur.fetchall()  # List of dicts
        return results
    except Exception as e:
        print("Database query error:", e)
        return []
    finally:
        if conn:
            conn.close()

def user_check():
    users = db_query("SELECT first_name, last_name, username, email, password_hash FROM users")
    creds = {"usernames": {}}
    for user in users:
        full_name = f"{user['first_name']} {user['last_name']}".strip()
        creds["usernames"][user["username"]] = {
            "name": full_name,
            "email": user["email"],
            "password": user["password_hash"]  # bcrypt-hashed passwords expected by streamlit-authenticator
        }
    return creds
