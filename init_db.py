import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        name TEXT NOT NULL,
        program TEXT NOT NULL,
        year INTEGER NOT NULL,
        section TEXT NOT NULL,
        source TEXT DEFAULT 'Local'
    )
''')

# Check if the source column exists
cursor.execute("PRAGMA table_info(students)")
columns = [column[1] for column in cursor.fetchall()]

# Add the column if it is missing
if 'source' not in columns:
    cursor.execute(
        "ALTER TABLE students ADD COLUMN source TEXT DEFAULT 'Local'"
    )

# Remove old practice records
cursor.execute("DELETE FROM students")

students = [
    ('24-00248', 'Seth Claire Palec', 'BSIT', 3, 'B', 'Local'),
    ('24-00379', 'Crystal Mae Elizares', 'BSIT', 3, 'B', 'Local'),
    ('24-00125', 'Jezalyn Indic', 'BSIT', 3, 'A', 'Local'),
    ('24-00125', 'Jiza Mae Gubac', 'BSIT', 3, 'A', 'Local'),
    ('24-00125', 'Stephene Jeke Paclibar', 'BSIT', 3, '', 'Local')
]

cursor.executemany('''
    INSERT INTO students
    (student_id, name, program, year, section, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', students)


conn.commit()
conn.close()

print("Database created successfully.")
