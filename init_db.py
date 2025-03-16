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