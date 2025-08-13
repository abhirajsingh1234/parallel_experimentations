import pyodbc
from config.configuration import Config

conn_str = Config.DB_CONN_STR

def get_db_connection():
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        raise Exception(f"Database connection error: {str(e)}")