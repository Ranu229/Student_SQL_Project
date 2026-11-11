"""
Student Database Management System
-----------------------------------
This script demonstrates how to perform CRUD (Create, Read, Update, Delete)
operations on an SQL database (SQLite) using Python's built-in sqlite3 module.
"""

import sqlite3
import os

DB_NAME = "students.db"


def get_connection(db_name=DB_NAME):
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(db_name)
    # Enable foreign keys and row factory for dictionary-like column access
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# 1. CREATE TABLE
# ==========================================
def create_table():
    """
    Creates the 'students' table if it does not already exist.
    Columns:
      - id: Primary Key (auto-incrementing unique integer)
      - name: Student's name (text, required)
      - age: Student's age (integer)
      - grade: Student's grade/class (text)
      - email: Student's email address (text, unique)
    """
    sql_query = """
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        grade TEXT,
        email TEXT UNIQUE
    );
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        conn.commit()
    print(" Table 'students' is ready.")


# ==========================================
# 2. CREATE (INSERT) OPERATION
# ==========================================
def insert_student(name: str, age: int, grade: str, email: str):
    """
    Inserts a new student record into the database.
    Uses parameterized query (?) to prevent SQL injection.
    """
    sql_query = """
    INSERT INTO students (name, age, grade, email)
    VALUES (?, ?, ?, ?);
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query, (name, age, grade, email))
            conn.commit()
            new_id = cursor.lastrowid
            print(f"[INSERT] Added student '{name}' with ID: {new_id}")
            return new_id
    except sqlite3.IntegrityError as e:
        print(f"[ERROR] Could not insert student: {e}")
        return None


# ==========================================
# 3. READ (SELECT) OPERATIONS
# ==========================================
def read_all_students():
    """Fetches and returns all student records from the database."""
    sql_query = "SELECT id, name, age, grade, email FROM students ORDER BY id ASC;"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        return rows


def read_student_by_id(student_id: int):
    """Fetches a single student by their ID."""
    sql_query = "SELECT id, name, age, grade, email FROM students WHERE id = ?;"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql_query, (student_id,))
        return cursor.fetchone()


def display_students(rows):
    """Formats and prints rows nicely in a table format in the terminal."""
    if not rows:
        print("  No student records found.")
        return

    print("\n" + "=" * 65)
    print(f"{'ID':<5} | {'Name':<20} | {'Age':<5} | {'Grade':<8} | {'Email':<20}")
    print("-" * 65)
    for row in rows:
        print(f"{row['id']:<5} | {row['name']:<20} | {row['age']:<5} | {row['grade']:<8} | {row['email']:<20}")
    print("=" * 65 + "\n")


# ==========================================
# 4. UPDATE OPERATION
# ==========================================
def update_student(student_id: int, name=None, age=None, grade=None, email=None):
    """
    Updates the fields of an existing student by ID.
    Only provided fields (non-None) will be updated.
    """
    # Verify the student exists
    existing = read_student_by_id(student_id)
    if not existing:
        print(f"[ERROR] Student with ID {student_id} not found.")
        return False

    fields = []
    values = []

    if name is not None:
        fields.append("name = ?")
        values.append(name)
    if age is not None:
        fields.append("age = ?")
        values.append(age)
    if grade is not None:
        fields.append("grade = ?")
        values.append(grade)
    if email is not None:
        fields.append("email = ?")
        values.append(email)

    if not fields:
        print("[WARNING] No fields provided to update.")
        return False

    values.append(student_id)
    sql_query = f"UPDATE students SET {', '.join(fields)} WHERE id = ?;"

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query, tuple(values))
            conn.commit()
            print(f"[UPDATE] Successfully updated student ID: {student_id}")
            return True
    except sqlite3.IntegrityError as e:
        print(f"[ERROR] Could not update student: {e}")
        return False


# ==========================================
# 5. DELETE OPERATION
# ==========================================
def delete_student(student_id: int):
    """Deletes a student record by ID."""
    existing = read_student_by_id(student_id)
    if not existing:
        print(f"[ERROR] Student with ID {student_id} does not exist.")
        return False

    sql_query = "DELETE FROM students WHERE id = ?;"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql_query, (student_id,))
        conn.commit()
        print(f"[DELETE] Successfully deleted student ID: {student_id} ({existing['name']})")
        return True


# ==========================================
# DEMO WALKTHROUGH
# ==========================================
def run_demo():
    """Runs a step-by-step demonstration of all CRUD operations."""
    print("\n==============================================")
    print("      RUNNING SQL CRUD OPERATIONS DEMO        ")
    print("==============================================")

    # Step 1: Create Table
    print("\n--- STEP 1: Creating database table ---")
    create_table()

    # Step 2: Insert (Create) sample students
    print("\n--- STEP 2: Inserting (CREATE) sample student records ---")
    insert_student("Alice Johnson", 20, "A", "alice@example.com")
    insert_student("Bob Smith", 22, "B", "bob@example.com")
    insert_student("Charlie Brown", 19, "A+", "charlie@example.com")
    insert_student("Diana Prince", 21, "B+", "diana@example.com")

    # Step 3: Read (Select) all students
    print("\n--- STEP 3: Reading (SELECT) all students from database ---")
    all_students = read_all_students()
    display_students(all_students)

    # Step 4: Update a student's grade and age
    print("\n--- STEP 4: Updating (UPDATE) Bob Smith (ID: 2) ---")
    print("Changing Bob's grade from 'B' to 'A+' and age to 23...")
    update_student(student_id=2, grade="A+", age=23)

    print("\nVerifying update for Bob:")
    updated_bob = read_student_by_id(2)
    display_students([updated_bob])

    # Step 5: Delete a student
    print("\n--- STEP 5: Deleting (DELETE) student with ID: 3 (Charlie Brown) ---")
    delete_student(student_id=3)

    # Step 6: Final check
    print("\n--- STEP 6: Final Table Contents after CRUD operations ---")
    display_students(read_all_students())
    print(" Demo completed successfully!\n")


# ==========================================
# INTERACTIVE CLI MENU
# ==========================================
def interactive_menu():
    """Interactive console menu for manual database operations."""
    create_table()
    while True:
        print("\n=== STUDENT DATABASE MANAGEMENT ===")
        print("1. View all students (READ)")
        print("2. Add a new student (INSERT / CREATE)")
        print("3. Update student details (UPDATE)")
        print("4. Delete a student (DELETE)")
        print("5. Run automatic demo (ALL CRUD)")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            students = read_all_students()
            display_students(students)

        elif choice == "2":
            name = input("Enter name: ").strip()
            age_str = input("Enter age: ").strip()
            grade = input("Enter grade: ").strip()
            email = input("Enter email: ").strip()

            try:
                age = int(age_str)
                insert_student(name, age, grade, email)
            except ValueError:
                print("[ERROR] Age must be an integer number.")

        elif choice == "3":
            id_str = input("Enter student ID to update: ").strip()
            try:
                s_id = int(id_str)
                student = read_student_by_id(s_id)
                if not student:
                    print(f"Student with ID {s_id} not found.")
                    continue

                print(f"Updating student: {student['name']}. (Press Enter to leave unchanged)")
                new_name = input(f"New name [{student['name']}]: ").strip() or None
                new_age_str = input(f"New age [{student['age']}]: ").strip()
                new_grade = input(f"New grade [{student['grade']}]: ").strip() or None
                new_email = input(f"New email [{student['email']}]: ").strip() or None

                new_age = int(new_age_str) if new_age_str else None
                update_student(s_id, name=new_name, age=new_age, grade=new_grade, email=new_email)
            except ValueError:
                print("[ERROR] Invalid number entered.")

        elif choice == "4":
            id_str = input("Enter student ID to delete: ").strip()
            try:
                s_id = int(id_str)
                delete_student(s_id)
            except ValueError:
                print("[ERROR] ID must be an integer.")

        elif choice == "5":
            run_demo()

        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose between 1 and 6.")


if __name__ == "__main__":
    import sys
    # If passed '--demo', run demo directly, otherwise interactive menu
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        # Default to running the demo first, then giving menu
        print("Welcome to the Student SQL Database Query Tool!")
        print("Running an initial demonstration of CRUD operations...")
        run_demo()
        print("You can now explore the interactive menu to run your own queries:")
        interactive_menu()
