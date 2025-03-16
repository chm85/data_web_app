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
    """Execute a SQL query and return the results if applicable."""
    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute(query, params or ())
        if query.strip().lower().startswith("select"):
            return cursor.fetchall()  # Return results for SELECT queries
        conn.commit()  # Commit changes for INSERT, UPDATE, DELETE
        print("Query executed successfully.")

def list_tables():
    """List all tables in the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to get table names
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = cursor.fetchall()
        
        print("Tables in the database:")
        for table in tables:
            print(table[0])
        
        cursor.close()
        conn.close()
    
    except Exception as e:
        print(f"Error: {e}")

list_tables()
 
def drop_table(table_name):
    """Drop the specified table if it exists."""
    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        print(f"Table '{table_name}' dropped successfully.")


drop_table('projects')
drop_table('votes')

list_tables()