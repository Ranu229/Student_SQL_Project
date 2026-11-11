import os
import sqlite3
from flask import Flask, render_template, request, jsonify

# Get current directory of index.py (inside /api)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

app = Flask(__name__, template_folder=TEMPLATE_DIR)

# SQLite path: On Vercel, root is read-only, so use /tmp
if os.environ.get("VERCEL"):
    DB_NAME = "/tmp/students.db"
else:
    # Local fallback
    ROOT_DIR = os.path.dirname(BASE_DIR)
    DB_NAME = os.path.join(ROOT_DIR, "students.db")


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database and table, and seeds with sample records if empty."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            grade TEXT,
            email TEXT UNIQUE
        );
        """)
        conn.commit()

        # Seed sample data if table is brand new/empty
        cursor.execute("SELECT COUNT(*) FROM students;")
        count = cursor.fetchone()[0]
        if count == 0:
            sample_students = [
                ("Alice Johnson", 20, "A", "alice@example.com"),
                ("Bob Smith", 23, "A+", "bob@example.com"),
                ("Diana Prince", 21, "B+", "diana@example.com"),
                ("Charlie Brown", 19, "A+", "charlie@example.com"),
                ("John Doe", 25, "A", "john.doe@example.com"),
                ("Emma Watson", 22, "A+", "emma@example.com")
            ]
            cursor.executemany(
                "INSERT OR IGNORE INTO students (name, age, grade, email) VALUES (?, ?, ?, ?);",
                sample_students
            )
            conn.commit()


# Initialize table on startup
init_db()


# -------------------------------------------------------------
# 1. FRONTEND ROUTE (Matches /, /api, /api/index, /index)
# -------------------------------------------------------------
@app.route("/")
@app.route("/api")
@app.route("/api/index")
@app.route("/index")
def index():
    init_db()
    return render_template("index.html")


# -------------------------------------------------------------
# 2. READ (SELECT) API
# -------------------------------------------------------------
@app.route("/api/students", methods=["GET"])
@app.route("/students", methods=["GET"])
def get_students():
    try:
        init_db()
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
@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    age = data.get("age")
    grade = (data.get("grade") or "").strip()
    email = (data.get("email") or "").strip()

    if not name or not email or age is None or not grade:
        return jsonify({"success": False, "error": "All fields are required."}), 400

    try:
        age = int(age)
    except ValueError:
        return jsonify({"success": False, "error": "Age must be a valid number."}), 400

    try:
        init_db()
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
@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    age = data.get("age")
    grade = (data.get("grade") or "").strip()
    email = (data.get("email") or "").strip()

    if not name or not email or age is None or not grade:
        return jsonify({"success": False, "error": "All fields are required."}), 400

    try:
        age = int(age)
    except ValueError:
        return jsonify({"success": False, "error": "Age must be a valid number."}), 400

    try:
        init_db()
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
@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    try:
        init_db()
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
@app.route("/execute-sql", methods=["POST"])
def execute_sql():
    data = request.get_json() or {}
    query = (data.get("query") or "").strip()

    if not query:
        return jsonify({"success": False, "error": "Query cannot be empty."}), 400

    try:
        init_db()
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


# Support local execution if index.py is run directly
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
