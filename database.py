import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    type TEXT,
    year TEXT,
    file_name TEXT
)
""")

# Clear old data (important)
cursor.execute("DELETE FROM materials")

# Insert clean uppercase data
materials = [
    ('DSA', 'PYQ', '2022', 'dsa_pyq_2022.pdf'),
    ('DBMS', 'NOTES', '2023', 'dbms_notes.pdf'),
    ('DSA', 'NOTES', '2023', 'dsa_notes_2023.pdf'),
    ('DBMS', 'PYQ', '2022', 'dbms_pyq_2022.pdf'),
    ('OS', 'PYQ', '2023', 'os_pyq_2023.pdf')
]

cursor.executemany("""
INSERT INTO materials (subject, type, year, file_name)
VALUES (?, ?, ?, ?)
""", materials)

conn.commit()
conn.close()

print("Database created successfully!")
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    type TEXT,
    year TEXT,
    file_name TEXT
)
""")

# Clear old data (important)
cursor.execute("DELETE FROM materials")

# Insert clean uppercase data
materials = [
    ('DSA', 'PYQ', '2022', 'dsa_pyq_2022.pdf'),
    ('DBMS', 'NOTES', '2023', 'dbms_notes.pdf'),
    ('DSA', 'NOTES', '2023', 'dsa_notes_2023.pdf'),
    ('DBMS', 'PYQ', '2022', 'dbms_pyq_2022.pdf'),
    ('OS', 'PYQ', '2023', 'os_pyq_2023.pdf')
]

cursor.executemany("""
INSERT INTO materials (subject, type, year, file_name)
VALUES (?, ?, ?, ?)
""", materials)

conn.commit()
conn.close()

print("Database created successfully!")
