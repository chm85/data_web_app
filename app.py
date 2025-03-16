from flask import Flask, session, render_template, request, redirect, url_for, jsonify
import psycopg2
import os
import uuid

app = Flask(__name__)

# Set a secret key for session encryption (store securely in Azure)
app.secret_key = os.getenv("SECRET_KEY")

# Temp update to  vault
# PostgreSQL Connection Details (Replace with your own Azure DB info)
DB_HOST = os.getenv("PGHOST", "hackathon-fun-server.postgres.database.azure.com")
DB_NAME =  os.getenv("PGDATABASE", "postgres")
DB_USER = os.getenv("PGUSER", "lfcqxcirwp")
DB_PASSWORD = os.getenv("PGPASSWORD") 
DB_PORT = os.getenv("PGPORT", "5432")


def get_db_connection():
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
    """Ensure the projects and votes tables exist."""
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


def get_projects():
    """ Fetch all projects from PostgreSQL. """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, innovation, presentation, business_impact, total_votes FROM projects ORDER BY id ASC")
        return cursor.fetchall()


@app.route('/')
def index():
    projects = get_projects()
    return render_template('index.html', projects=projects)


def get_or_create_session():
    """ Generate or retrieve a unique session ID for the user. """
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())  # Generate a unique session ID
    return session['session_id']


@app.route('/vote', methods=['POST'])
def vote():
    """ Handles voting while preventing multiple votes per user. """
    project_id = request.form.get("project_id")
    innovation = int(request.form.get("innovation", 0))
    presentation = int(request.form.get("presentation", 0))
    business_impact = int(request.form.get("business_impact", 0))
    session_id = get_or_create_session()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if the user has already voted for this project
        cursor.execute("SELECT * FROM votes WHERE project_id = %s AND session_id = %s", (project_id, session_id))
        existing_vote = cursor.fetchone()

        if existing_vote:
            return "❌ You have already voted for this project!", 403  # Prevent duplicate votes

        # Insert the vote with the session ID
        cursor.execute(
            "INSERT INTO votes (project_id, innovation, presentation, business_impact, session_id) VALUES (%s, %s, %s, %s, %s)",
            (project_id, innovation, presentation, business_impact, session_id)
        )

        # Update total votes count for the project
        cursor.execute("UPDATE projects SET total_votes = total_votes + 1 WHERE id = %s", (project_id,))
        conn.commit()

    return redirect(url_for('index'))


@app.route('/edit_vote', methods=['POST'])
def edit_vote():
    """ Allow editing votes instead of creating new ones. """
    project_id = request.form.get("project_id")
    innovation = int(request.form.get("innovation", 0))
    presentation = int(request.form.get("presentation", 0))
    business_impact = int(request.form.get("business_impact", 0))
    session_id = session.get('session_id')  # Get session ID

    if not session_id:
        return "❌ You have not voted yet!", 403  # Prevent edits if no session exists

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if the user has already voted
        cursor.execute("SELECT * FROM votes WHERE project_id = %s AND session_id = %s", (project_id, session_id))
        existing_vote = cursor.fetchone()

        if not existing_vote:
            return "❌ You have not voted yet!", 403  # Ensure user has voted

        # Update vote
        cursor.execute(
            "UPDATE votes SET innovation = %s, presentation = %s, business_impact = %s WHERE project_id = %s AND session_id = %s",
            (innovation, presentation, business_impact, project_id, session_id)
        )
        conn.commit()

    return redirect(url_for('index'))


@app.route('/leaderboard_data', methods=['GET'])
def leaderboard_data():
    """ Retrieve leaderboard data sorted by score. """
    projects = get_projects()
    leaderboard_data = [{
        "name": p[1],
        "average_score": round((p[2] + p[3] + p[4]) / (3 * max(1, p[5])), 2) if p[5] > 0 else 0,
        "total_votes": p[5]
    } for p in projects]
    return jsonify(leaderboard_data)


if __name__ == '__main__':
    init_db()  # Ensure database is initialized
    print("Connecting to PostgreSQL at:", DB_HOST)
    app.run(host="0.0.0.0", port=8000, debug=True)
