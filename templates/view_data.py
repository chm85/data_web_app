


import pandas as pd
import os
 
import psycopg2

# Database connection details
DB_HOST = os.getenv("PGHOST", "hackathon-fun-server.postgres.database.azure.com")
DB_NAME = os.getenv("PGDATABASE", "postgres")
DB_USER = os.getenv("PGUSER", "lfcqxcirwp")
DB_PASSWORD = os.getenv("PGPASSWORD") 
DB_PORT = os.getenv("PGPORT", "5432")

def get_db_connection():
    """Connect to PostgreSQL database."""
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        sslmode="require"  # Required for Azure
    )

def execute_query(query, params=None):
    """Execute a SQL query and return results as a pandas DataFrame if applicable."""
    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute(query, params or ())
        
        if query.strip().lower().startswith("select"):
            columns = [desc[0] for desc in cursor.description]  # Get column names
            data = cursor.fetchall()  # Fetch all rows
            return pd.DataFrame(data, columns=columns)  # Convert to DataFrame
        
        conn.commit()  # Commit changes for INSERT, UPDATE, DELETE
        print("Query executed successfully.")

df = execute_query("SELECT * FROM projects")