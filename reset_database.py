#!/usr/bin/env python3
"""
Reset Database Script
Clears all user data and resets the database to a clean state.
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash

def reset_database():
    db_path = "database.db"
    
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✓ Deleted existing database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        role TEXT,
        prn TEXT,
        year TEXT,
        subject TEXT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS materials(
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
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS qa_mapping(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        subject TEXT,
        unit_number TEXT,
        material_id INTEGER,
        FOREIGN KEY (material_id) REFERENCES materials(id)
    )
    """)
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        message TEXT,
        response TEXT,
        time TEXT
    )
    """)
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS bookmarks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        material_id INTEGER,
        bookmarked_on TEXT,
        FOREIGN KEY (material_id) REFERENCES materials(id)
    )
    """)
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS analytics(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_id INTEGER,
        action_type TEXT,
        username TEXT,
        timestamp TEXT,
        FOREIGN KEY (material_id) REFERENCES materials(id)
    )
    """)
    
    hashed_password = generate_password_hash("admin123")
    c.execute("""
    INSERT INTO users(full_name,role,username,password)
    VALUES('Admin','professor',?,?)
    """, ("admin", hashed_password))
    
    seed_qa_data(c)
    
    conn.commit()
    conn.close()
    
    print("✓ Database schema created successfully")
    print("✓ Default admin user created (username: admin, password: admin123)")
    print("✓ QA mapping seeded with common questions")
    print("\n✅ Database reset completed!")


def seed_qa_data(cursor):
    common_questions = [
        ("What is data structure?", "DSA", "1", 1),
        ("Explain array data structure", "DSA", "1", 1),
        ("What is linked list?", "DSA", "2", 1),
        ("Difference between stack and queue", "DSA", "3", 1),
        ("What is binary tree?", "DSA", "4", 1),
        ("Explain graph traversal algorithms", "DSA", "5", 1),
        ("What is sorting algorithm?", "DSA", "6", 1),
        ("What is computer organization?", "COA", "1", 1),
        ("Explain CPU architecture", "COA", "2", 1),
        ("What is memory hierarchy?", "COA", "3", 1),
        ("Explain cache memory", "COA", "3", 1),
        ("What is pipelining?", "COA", "4", 1),
        ("Explain instruction set architecture", "COA", "2", 1),
        ("What is management information system?", "MIS", "1", 1),
        ("Explain decision support system", "MIS", "2", 1),
        ("What is database management system?", "MIS", "3", 1),
        ("Explain ERP system", "MIS", "4", 1),
        ("What is supply chain management?", "MIS", "5", 1),
        ("Explain business intelligence", "MIS", "2", 1),
        ("What is data mining?", "DSA", "6", 1),
        ("Explain hashing technique", "DSA", "5", 1),
        ("What is recursion?", "DSA", "2", 1),
        ("Explain dynamic programming", "DSA", "6", 1),
        ("What is greedy algorithm?", "DSA", "6", 1),
        ("Explain divide and conquer", "DSA", "6", 1),
        ("What is time complexity?", "DSA", "1", 1),
        ("Explain space complexity", "DSA", "1", 1),
        ("What is Big O notation?", "DSA", "1", 1),
        ("Explain assembly language", "COA", "2", 1),
        ("What is virtual memory?", "COA", "3", 1),
        ("Explain interrupt handling", "COA", "4", 1),
        ("What is DMA?", "COA", "4", 1),
        ("Explain bus architecture", "COA", "1", 1),
        ("What is RISC and CISC?", "COA", "2", 1),
        ("Explain information system", "MIS", "1", 1),
        ("What is transaction processing system?", "MIS", "2", 1),
        ("Explain knowledge management system", "MIS", "3", 1),
        ("What is enterprise system?", "MIS", "4", 1),
        ("Explain cloud computing in MIS", "MIS", "5", 1),
        ("What is data warehouse?", "MIS", "3", 1),
    ]
    
    for q, subj, unit, mat_id in common_questions:
        cursor.execute("""
        INSERT INTO qa_mapping(question, subject, unit_number, material_id)
        VALUES(?,?,?,?)
        """, (q, subj, unit, mat_id))


if __name__ == "__main__":
    reset_database()
