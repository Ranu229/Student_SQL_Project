"""
=============================================================================
         STUDENT SQL DATABASE - WEB DASHBOARD (Flask Backend)
=============================================================================
This web application connects your SQLite database (`students.db`) to a 
modern, interactive browser dashboard.

Configured for both local development and Vercel serverless deployment!
=============================================================================
"""

import os
import shutil
import sqlite3
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

app = Flask(__name__, template_folder=TEMPLATE_DIR)

# Configure database path for local vs. Vercel serverless environment
if os.environ.get("VERCEL"):
    DB_NAME = "/tmp/students.db"
    local_db = os.path.join(BASE_DIR, "students.db")
    if os.path.exists(local_db) and not os.path.exists(DB_NAME):
        try:
            shutil.copy2(local_db, DB_NAME)
        except Exception:
            pass
else:
    DB_NAME = os.path.join(BASE_DIR, "students.db")


def get_db_connection():
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database and table if not already created."""
    with get_db_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            grade TEXT,
            email TEXT UNIQUE
        );
        """)
        conn.commit()


# Automatically initialize DB on import/start
init_db()


# -------------------------------------------------------------
# 1. FRONTEND ROUTE
# -------------------------------------------------------------
@app.route("/")
def index():
    """Renders the main dashboard page."""
    return render_template("index.html")


# -------------------------------------------------------------
# 2. READ (SELECT) API
# -------------------------------------------------------------
@app.route("/api/students", methods=["GET"])
def get_students():
    """Returns all students as JSON."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, age, grade, email FROM students ORDER BY id ASC;")
            rows = cursor.fetchall()
            students = [dict(row) for row in rows]
            return jsonify({"success": True, "students": students})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# -------------------------------------------------------------
# 3. CREATE (INSERT) API
# -------------------------------------------------------------
@app.route("/api/students", methods=["POST"])
def add_student():
    """Inserts a new student record."""
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    age = data.get("age")
    grade = data.get("grade", "").strip()
    email = data.get("email", "").strip()

    if not name or not email or age is None or not grade:
        return jsonify({"success": False, "error": "All fields are required."}), 400

    try:
        age = int(age)
    except ValueError:
        return jsonify({"success": False, "error": "Age must be a valid number."}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO students (name, age, grade, email) VALUES (?, ?, ?, ?);",
                (name, age, grade, email),
            )
            conn.commit()
            return jsonify({"success": True, "id": cursor.lastrowid})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": f"Email '{email}' is already registered."}), 409
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# -------------------------------------------------------------
# 4. UPDATE API
# -------------------------------------------------------------
@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    """Updates an existing student's details."""
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    age = data.get("age")
    grade = data.get("grade", "").strip()
    email = data.get("email", "").strip()

    if not name or not email or age is None or not grade:
        return jsonify({"success": False, "error": "All fields are required."}), 400

    try:
        age = int(age)
    except ValueError:
        return jsonify({"success": False, "error": "Age must be a valid number."}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE students SET name = ?, age = ?, grade = ?, email = ? WHERE id = ?;",
                (name, age, grade, email, student_id),
            )
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"success": False, "error": "Student not found."}), 404
            return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": f"Email '{email}' is already in use by another student."}), 409
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# -------------------------------------------------------------
# 5. DELETE API
# -------------------------------------------------------------
@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    """Deletes a student by ID."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id = ?;", (student_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"success": False, "error": "Student not found."}), 404
            return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# -------------------------------------------------------------
# 6. RAW SQL QUERY EXECUTION API
# -------------------------------------------------------------
@app.route("/api/execute-sql", methods=["POST"])
def execute_sql():
    """Allows running raw SQL queries directly from the web interface."""
    data = request.get_json() or {}
    query = (data.get("query") or "").strip()

    if not query:
        return jsonify({"success": False, "error": "Query cannot be empty."}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            first_word = query.split()[0].upper()

            if first_word in ("INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"):
                conn.commit()
                return jsonify({"success": True, "message": f"{first_word} successful. Rows affected: {cursor.rowcount}"})
            else:
                rows = cursor.fetchall()
                results = [dict(row) for row in rows]
                return jsonify({"success": True, "rows": results, "message": f"Returned {len(results)} rows."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


def open_browser():
    """Opens the web browser automatically after server starts."""
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print(" [START] STUDENT DATABASE WEB APPLICATION")
    print("=" * 65)
    print(" Access the website at: http://127.0.0.1:5000")
    print(" Opening browser automatically in 1 second...")
    print(" Press Ctrl + C in terminal to stop the server.")
    print("=" * 65 + "\n")

    threading.Timer(1.2, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
