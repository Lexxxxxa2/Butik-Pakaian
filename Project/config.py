import pyodbc

DB_CONFIG = {
    "driver": "{ODBC Driver 17 for SQL Server}",
    "server": r"DESKTOP\ALEXANDER",
    "database": "ButikPakaian",
    "trusted": "yes"
}

def get_connection():
    conn_str = (
        f"Driver={DB_CONFIG['driver']};"
        f"Server={DB_CONFIG['server']};"
        f"Database={DB_CONFIG['database']};"
        f"Trusted_Connection={DB_CONFIG['trusted']};"
    )
    return pyodbc.connect(conn_str, autocommit=False)
