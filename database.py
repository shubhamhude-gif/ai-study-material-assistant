import sqlite3

# Connect database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    type TEXT NOT NULL,
    year TEXT NOT NULL,
    file_name TEXT NOT NULL
)
""")

# OPTIONAL: clear old data (remove if not needed)
cursor.execute("DELETE FROM materials")

# Sample data (you can remove later)
materials = [
    ('DSA', 'PYQ', '2022', 'dsa_pyq_2022.pdf'),
    ('DBMS', 'NOTES', '2023', 'dbms_notes.pdf'),
    ('OS', 'PYQ', '2023', 'os_pyq_2023.pdf')
]

cursor.executemany("""
INSERT INTO materials (subject, type, year, file_name)
VALUES (?, ?, ?, ?)
""", materials)

conn.commit()
conn.close()

print("Database created successfully!")