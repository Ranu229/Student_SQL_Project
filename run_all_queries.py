"""
=============================================================================
           RUN ALL SQL CRUD QUERIES AT ONCE (Step-by-Step Demo)
=============================================================================
This script runs ALL 4 major SQL queries in order:
  1. INSERT (Create)  -> Adds a new student record
  2. SELECT (Read)    -> Reads and displays all students
  3. UPDATE (Update)  -> Updates that student's grade and age
  4. DELETE (Delete)  -> Removes that student from the database
  5. SELECT (Final)   -> Shows the final table to confirm deletion
=============================================================================
"""

import sqlite3

DB_NAME = "students.db"


def print_table(cursor, title):
    """Helper function to fetch and print the table with a clean header."""
    cursor.execute("SELECT id, name, age, grade, email FROM students ORDER BY id ASC;")
    rows = cursor.fetchall()

    print("\n" + "=" * 68)
    print(f" {title}")
    print("=" * 68)
    print(f"{'ID':<5} | {'Name':<20} | {'Age':<5} | {'Grade':<8} | {'Email':<22}")
    print("-" * 68)
    if not rows:
        print("  (Database table is empty)")
    else:
        for row in rows:
            print(f"{row[0]:<5} | {row[1]:<20} | {row[2]:<5} | {row[3]:<8} | {row[4]:<22}")
    print("=" * 68 + "\n")


def run_all_queries():
    # Connect to database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Step 0: Ensure table exists
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

    print("\n" + "#" * 68)
    print("           STARTING ALL 4 SQL QUERIES EXECUTION")
    print("#" * 68)

    # -------------------------------------------------------------
    # QUERY 1: INSERT (Create a new student)
    # -------------------------------------------------------------
    print("\n--- [QUERY 1 - INSERT]: Adding a new student 'Rahul Sharma' ---")
    sql_insert = """
    INSERT INTO students (name, age, grade, email)
    VALUES (?, ?, ?, ?);
    """

    # We remove Rahul first if he already exists so this script can be re-run safely anytime
    cursor.execute("DELETE FROM students WHERE email = 'rahul@example.com';")
    conn.commit()

    # Execute the INSERT
    cursor.execute(sql_insert, ("Rahul Sharma", 21, "B", "rahul@example.com"))
    conn.commit()
    new_student_id = cursor.lastrowid
    print(f"[SUCCESS] Inserted 'Rahul Sharma' with ID: {new_student_id}")

    # -------------------------------------------------------------
    # QUERY 2: SELECT (Read all students)
    # -------------------------------------------------------------
    print("\n--- [QUERY 2 - SELECT / READ]: Fetching all students from database ---")
    print_table(cursor, "TABLE AFTER INSERT (Rahul is now in the database)")

    # -------------------------------------------------------------
    # QUERY 3: UPDATE (Update Rahul's grade from 'B' to 'A+' and age to 22)
    # -------------------------------------------------------------
    print(f"\n--- [QUERY 3 - UPDATE]: Updating Rahul's grade to 'A+' and age to 22 ---")
    sql_update = """
    UPDATE students 
    SET grade = ?, age = ? 
    WHERE id = ?;
    """
    cursor.execute(sql_update, ("A+", 22, new_student_id))
    conn.commit()
    print("[SUCCESS] Record updated.")
    print_table(cursor, "TABLE AFTER UPDATE (Notice Rahul's Grade is now A+ and Age is 22)")

    # -------------------------------------------------------------
    # QUERY 4: DELETE (Delete Rahul from the database)
    # -------------------------------------------------------------
    print(f"\n--- [QUERY 4 - DELETE]: Deleting student ID {new_student_id} ('Rahul Sharma') ---")
    sql_delete = "DELETE FROM students WHERE id = ?;"
    cursor.execute(sql_delete, (new_student_id,))
    conn.commit()
    print(f"[SUCCESS] Deleted student ID: {new_student_id}")

    # -------------------------------------------------------------
    # FINAL SELECT: Verify deletion
    # -------------------------------------------------------------
    print("\n--- [FINAL SELECT]: Checking the table after deletion ---")
    print_table(cursor, "FINAL TABLE (Notice Rahul is now deleted)")

    print("#" * 68)
    print("   ALL 4 QUERIES (INSERT, READ, UPDATE, DELETE) FINISHED SUCCESSFULLY!")
    print("#" * 68 + "\n")

    conn.close()


if __name__ == "__main__":
    run_all_queries()
