import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create table only
cursor.execute("""
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    type TEXT NOT NULL,
    year TEXT NOT NULL,
    file_name TEXT NOT NULL
)
""")

# Clear old data
cursor.execute("DELETE FROM materials")

conn.commit()
conn.close()

print("Empty database created successfully!")