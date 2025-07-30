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

# DB_CONFIG = {
    #         'dbname': 'new_db',
    #         'user': 'postgres',
    #         'password':'Database@123',
    #         'host': 'localhost',
    #         'port': 5432
    #     }
    # def get_engine():
    #     password = urllib.parse.quote_plus(DB_CONFIG['password'])
    #     url = (
    #         f"postgresql+psycopg2://{DB_CONFIG['user']}:{password}"
    #         f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    #     )
    #     return create_engine(url)
    # return get_engine()