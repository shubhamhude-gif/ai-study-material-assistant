import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Updated materials table with new fields
cursor.execute("""
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    semester TEXT,
    unit_number TEXT,
    unit_name TEXT,
    material_type TEXT,
    filename TEXT,
    reference_url TEXT,
    academic_year TEXT,
    uploaded_on TEXT
)
""")

# QA Mapping table for common questions
cursor.execute("""
CREATE TABLE IF NOT EXISTS qa_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    subject TEXT,
    unit_number TEXT,
    material_id INTEGER,
    FOREIGN KEY (material_id) REFERENCES materials(id)
)
""")

# Updated users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    role TEXT,
    username TEXT UNIQUE,
    password TEXT,
    prn TEXT,
    year TEXT,
    subject TEXT
)
""")

# Chats table
cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    message TEXT,
    response TEXT,
    time TEXT
)
""")

# Bookmarks table
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    material_id INTEGER,
    bookmarked_on TEXT,
    FOREIGN KEY (material_id) REFERENCES materials(id)
)
""")

# Analytics table
cursor.execute("""
CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER,
    action_type TEXT,
    username TEXT,
    timestamp TEXT,
    FOREIGN KEY (material_id) REFERENCES materials(id)
)
""")

conn.commit()
conn.close()

print("Database ready with all tables.")