import psycopg2
import os
import uuid

def get_db_connection(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT):
    """ Connect to PostgreSQL database """
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


def get_or_create_session(session : str):
    """ Generate or retrieve a unique session ID per user session. """
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())  # Generate a unique session ID
        session.permanent = True  # Ensure it persists across refreshes
    return session['session_id']


def get_projects(session : str):
    """ Fetch all projects and check if the current user has voted. """
    session_id = session.get('session_id')  # Get current session ID

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Fetch projects and check if the current user has voted for each one
        cursor.execute("""
            SELECT p.id, p.name, p.total_votes,
                   COALESCE(v.innovation, NULL), COALESCE(v.presentation, NULL), COALESCE(v.business_impact, NULL)
            FROM projects p
            LEFT JOIN votes v ON p.id = v.project_id AND v.session_id = %s
            ORDER BY p.id ASC
        """, (session_id,))
        projects = cursor.fetchall()

    return projects
