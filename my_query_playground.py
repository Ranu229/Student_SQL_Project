"""
=================================================================================
                 SQL QUERY PLAYGROUND & LIVE VIEWER
=================================================================================
This file is your scratchpad! You can write ANY SQL query in the variable below,
run this file, and immediately watch the database update in real time.

Instructions:
  1. Change the query inside `MY_QUERY` below.
  2. Click the ▶ Play button in the top-right of VS Code (or press F5).
  3. Look at the terminal below to watch the updated table!
  4. (Bonus) Click on 'students.db' in the left VS Code Explorer to see the
     live visual spreadsheet table inside VS Code!
=================================================================================
"""

import sqlite3

# -------------------------------------------------------------------------------
# WRITE YOUR SQL QUERY HERE (Try INSERT, UPDATE, DELETE, or SELECT):
# -------------------------------------------------------------------------------

MY_QUERY = """
UPDATE students 
SET grade = 'A++', age = 26 
WHERE name = 'John Doe';
"""

# OTHER EXAMPLES YOU CAN TRY (copy & paste into MY_QUERY above):
#
# --- UPDATE EXAMPLE ---
# UPDATE students SET grade = 'A++', age = 26 WHERE name = 'John Doe';
#
# --- DELETE EXAMPLE ---
# DELETE FROM students WHERE name = 'John Doe';
#
# --- SELECT SPECIFIC STUDENTS ---
# SELECT * FROM students WHERE age >= 21;
#
# --- SORT STUDENTS BY AGE ---
# SELECT * FROM students ORDER BY age DESC;
# -------------------------------------------------------------------------------


def execute_and_watch(query: str, db_name="students.db"):
    clean_query = query.strip()
    if not clean_query:
        print("[WARNING] The query is empty. Please write a query in MY_QUERY!")
        return

    print("=" * 70)
    print(" EXECUTING YOUR SQL QUERY:")
    print("=" * 70)
    print(clean_query)
    print("=" * 70 + "\n")

    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(clean_query)
        first_word = clean_query.split()[0].upper()

        if first_word in ("INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"):
            conn.commit()
            print(f" Success! Rows affected: {cursor.rowcount}")
            print("\n Live Database Table ('students') After Your Change:")
            show_all_students(cursor)
        else:
            # Query like SELECT or PRAGMA
            results = cursor.fetchall()
            print(f" Query returned {len(results)} row(s):\n")
            display_rows(results)

    except sqlite3.Error as e:
        print(f" [SQL ERROR]: {e}")
    finally:
        conn.close()


def show_all_students(cursor):
    """Fetches and prints the entire students table."""
    cursor.execute("SELECT id, name, age, grade, email FROM students ORDER BY id ASC;")
    display_rows(cursor.fetchall())


def display_rows(rows):
    """Prints rows in a clean terminal table."""
    if not rows:
        print("  (No records found)")
        return

    print("-" * 70)
    print(f"{'ID':<5} | {'Name':<20} | {'Age':<5} | {'Grade':<8} | {'Email':<25}")
    print("-" * 70)
    for row in rows:
        r_id = row['id'] if 'id' in row.keys() else '-'
        name = row['name'] if 'name' in row.keys() else '-'
        age = row['age'] if 'age' in row.keys() else '-'
        grade = row['grade'] if 'grade' in row.keys() else '-'
        email = row['email'] if 'email' in row.keys() else '-'
        print(f"{r_id:<5} | {name:<20} | {age:<5} | {grade:<8} | {email:<25}")
    print("-" * 70 + "\n")


if __name__ == "__main__":
    execute_and_watch(MY_QUERY)
