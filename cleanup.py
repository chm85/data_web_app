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



def init_db():
    """ Ensure tables exist and initialize the database. """
    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE,
                innovation INTEGER DEFAULT 0,
                presentation INTEGER DEFAULT 0,
                business_impact INTEGER DEFAULT 0,
                total_votes INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                innovation INTEGER NOT NULL,
                presentation INTEGER NOT NULL,
                business_impact INTEGER NOT NULL,
                UNIQUE (project_id, session_id)  -- Prevent duplicate votes per user
            )
        ''')
        default_projects = [("AI Vision",), ("RPA",), ("AI Data Analyst",), ("Note App",)]
        cursor.executemany("INSERT INTO projects (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", default_projects)
        conn.commit()

init_db()

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

list_tables()