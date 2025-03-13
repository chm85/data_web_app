from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)

# Use persistent storage in Azure
DB_PATH = "/home/votes.db"

def init_db():
    """ Initialize the database and ensure the table exists. """
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS projects (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT UNIQUE,
                                innovation INTEGER DEFAULT 0,
                                presentation INTEGER DEFAULT 0,
                                business_impact INTEGER DEFAULT 0,
                                total_votes INTEGER DEFAULT 0)''')
            conn.commit()
            cursor.executemany("INSERT OR IGNORE INTO projects (name) VALUES (?)", 
                               [("AI Vision",), ("RPA",), ("AI Data Analyst",), ("Note App",)])
            conn.commit()
    else:
        print("Database already exists at:", DB_PATH)

def get_db_connection():
    """ Get a connection to the database. """
    return sqlite3.connect(DB_PATH)

def get_projects():
    """ Fetch all projects from the database. """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, innovation, presentation, business_impact, total_votes FROM projects ORDER BY id ASC")
        return cursor.fetchall()

def update_vote(project_id, innovation, presentation, business_impact):
    """ Update the vote for a project without increasing total votes on edit. """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT total_votes FROM projects WHERE id = ?", (project_id,))
        total_votes = cursor.fetchone()[0]
        if total_votes == 0:
            cursor.execute("UPDATE projects SET innovation = ?, presentation = ?, business_impact = ?, total_votes = 1 WHERE id = ?", 
                            (innovation, presentation, business_impact, project_id))
        else:
            cursor.execute("UPDATE projects SET innovation = ?, presentation = ?, business_impact = ? WHERE id = ?", 
                            (innovation, presentation, business_impact, project_id))
        conn.commit()

def edit_vote(project_id, innovation, presentation, business_impact):
    """ Allow editing votes without increasing total votes. """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET innovation = ?, presentation = ?, business_impact = ? WHERE id = ?", 
                        (innovation, presentation, business_impact, project_id))
        conn.commit()

def get_leaderboard_data():
    """ Retrieve leaderboard data sorted by score. """
    projects = get_projects()
    leaderboard_data = [{
        "name": p[1],
        "average_score": round((p[2] + p[3] + p[4]) / (3 * max(1, p[5])), 2) if p[5] > 0 else 0,
        "total_votes": p[5]
    } for p in projects]
    return sorted(leaderboard_data, key=lambda x: x['average_score'], reverse=True)

@app.route('/')
def index():
    projects = get_projects()
    return render_template('index.html', projects=projects)

@app.route('/vote', methods=['POST'])
def vote():
    project_id = request.form.get("project_id")
    innovation = int(request.form.get("innovation", 0))
    presentation = int(request.form.get("presentation", 0))
    business_impact = int(request.form.get("business_impact", 0))
    if project_id:
        update_vote(project_id, innovation, presentation, business_impact)
    return redirect(url_for('index'))

@app.route('/edit_vote', methods=['POST'])
def edit_vote_route():
    project_id = request.form.get("project_id")
    innovation = int(request.form.get("innovation", 0))
    presentation = int(request.form.get("presentation", 0))
    business_impact = int(request.form.get("business_impact", 0))
    if project_id:
        edit_vote(project_id, innovation, presentation, business_impact)
    return redirect(url_for('index'))

@app.route('/add_project', methods=['POST'])
def add_project():
    project_name = request.form.get("project_name")
    if project_name:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO projects (name) VALUES (?)", (project_name,))
            conn.commit()
    return redirect(url_for('index'))

@app.route('/leaderboard_data', methods=['GET'])
def leaderboard_data():
    return jsonify(get_leaderboard_data())

if __name__ == '__main__':
    init_db()  # Ensure database is initialized
    app.run(host="0.0.0.0", port=8000, debug=True)
