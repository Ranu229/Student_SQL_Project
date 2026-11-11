# Python & SQL Student Database (CRUD Operations)

This project demonstrates how to connect Python with a SQL database (**SQLite**) and execute the four fundamental database operations:
- **C**reate (INSERT)
- **R**ead (SELECT)
- **U**pdate (UPDATE)
- **D**elete (DELETE)

---

## 1. What Are We Doing?

1. **Database Engine**: We use **SQLite** (via Python's built-in `sqlite3` library).
   - SQLite requires **no separate server installation** (unlike MySQL or PostgreSQL).
   - The database is stored locally in a single file called `students.db`.
2. **Database Schema**: We create a table called `students` with the following structure:
   | Column Name | Data Type | Constraint | Description |
   | :--- | :--- | :--- | :--- |
   | `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique identifier for each student |
   | `name` | `TEXT` | `NOT NULL` | Student full name |
   | `age` | `INTEGER` | | Student age |
   | `grade` | `TEXT` | | Student letter grade or class (e.g. 'A', 'B+') |
   | `email` | `TEXT` | `UNIQUE` | Unique email address |

---

## 2. SQL Queries & Python Explanation

### A. Creating the Table
```sql
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    grade TEXT,
    email TEXT UNIQUE
);
```
- **In Python**:
  ```python
  cursor.execute(sql_query)
  conn.commit()  # Saves changes to disk
  ```

---

### B. INSERT (Create)
Inserts a new record into the table.
```sql
INSERT INTO students (name, age, grade, email)
VALUES (?, ?, ?, ?);
```
- **In Python**:
  ```python
  cursor.execute(sql_query, (name, age, grade, email))
  conn.commit()
  new_id = cursor.lastrowid
  ```
  > **Note**: We use `?` placeholders instead of string formatting (`f"INSERT ... {name}"`). This is known as a **parameterized query**, which prevents **SQL Injection attacks**.

---

### C. SELECT (Read)
Fetches data from the table.
- **Get all students**:
  ```sql
  SELECT id, name, age, grade, email FROM students ORDER BY id ASC;
  ```
- **Get a student by ID**:
  ```sql
  SELECT id, name, age, grade, email FROM students WHERE id = ?;
  ```
- **In Python**:
  ```python
  cursor.execute(sql_query)
  rows = cursor.fetchall()  # Returns all matching rows
  ```

---

### D. UPDATE
Modifies existing rows in the database.
```sql
UPDATE students
SET grade = ?, age = ?
WHERE id = ?;
```
- **In Python**:
  ```python
  cursor.execute(sql_query, (new_grade, new_age, student_id))
  conn.commit()
  ```

---

### E. DELETE
Removes a specific record from the database.
```sql
DELETE FROM students WHERE id = ?;
```
- **In Python**:
  ```python
  cursor.execute(sql_query, (student_id,))
  conn.commit()
  ```

---

## 3. How to Run the Code

1. Make sure Python is installed on your Windows machine:
   - Check with: `python --version`
   - If not installed, you can install Python easily via PowerShell:
     ```powershell
     winget install Python.Python.3.12
     ```
2. Navigate to this folder and run:
   ```powershell
   python student_db.py
   ```
   Or to run just the automated demo without menu prompt:
   ```powershell
   python student_db.py --demo
   ```
