from flask import Flask, render_template, request, redirect, session, send_from_directory, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import sqlite3
import os
import random
import datetime
import logging

load_dotenv()

# ===== LOGGING =====
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secure_key_change_in_production")

UPLOAD_FOLDER = "static/files"
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ===== DATABASE INITIALIZATION =====
def init_db():
    conn = sqlite3.connect("database.db")
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

    # Create default admin user with hashed password
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        hashed_password = generate_password_hash("admin123")
        c.execute("""
        INSERT INTO users(full_name,role,username,password)
        VALUES('Admin','professor',?,?)
        """, ("admin", hashed_password))

    # Seed QA mapping with common questions
    c.execute("SELECT COUNT(*) FROM qa_mapping")
    if c.fetchone()[0] == 0:
        seed_qa_data(c)

    conn.commit()
    conn.close()


def seed_qa_data(cursor):
    """Seed common theory questions for QA mapping"""
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


init_db()


# ===== AUTH PAGE (2-STEP FLOW) =====
@app.route("/", methods=["GET","POST"])
def auth():
    error = ""
    step = request.args.get("step", "1")

    if request.method == "POST":
        action = request.form.get("action")
        
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # STEP 1: Basic auth
        if action in ["login_step1", "register_step1"]:
            role = request.form.get("role")
            username = request.form.get("username")
            password = request.form.get("password")
            
            if not role:
                error = "Please select your role (Student or Faculty Member) to continue."
                conn.close()
                return render_template("auth.html", error=error, step=step)
            
            if not username:
                error = "Username is required. Please enter your username."
                conn.close()
                return render_template("auth.html", error=error, step=step)
            
            if not password:
                error = "Password is required. Please enter your password."
                conn.close()
                return render_template("auth.html", error=error, step=step)
            
            if len(username) < 3:
                error = "Username must be at least 3 characters long. Please try again."
                conn.close()
                return render_template("auth.html", error=error, step=step)
            
            if len(password) < 6:
                error = "Password must be at least 6 characters long. Please use a stronger password."
                conn.close()
                return render_template("auth.html", error=error, step=step)
            
            session["temp_role"] = role
            session["temp_username"] = username
            session["temp_password"] = password
            session["temp_action"] = action
            
            conn.close()
            return redirect("/?step=2")

        # STEP 2: Additional info
        elif action in ["login_step2", "register_step2"]:
            role = session.get("temp_role")
            username = session.get("temp_username")
            password = session.get("temp_password")
            original_action = session.get("temp_action")

            if not role or not username or not password:
                error = "Your session has expired. Please start again from the Sign In page."
                session.clear()
                conn.close()
                return redirect("/")

            if original_action == "register_step1":
                full_name = request.form.get("full_name")
                prn = request.form.get("prn") if role == "student" else None
                year = request.form.get("year") if role == "student" else None
                subject = request.form.get("subject") if role == "professor" else None

                if not full_name:
                    error = "Full name is required. Please enter your full name as per university records."
                    conn.close()
                    return render_template("auth.html", error=error, step="2", 
                                         temp_role=role, temp_action=original_action)
                
                if role == "student" and not prn:
                    error = "PRN is required. Please enter your Permanent Registration Number."
                    conn.close()
                    return render_template("auth.html", error=error, step="2", 
                                         temp_role=role, temp_action=original_action)
                
                if role == "student" and not year:
                    error = "Please select your current academic year to continue."
                    conn.close()
                    return render_template("auth.html", error=error, step="2", 
                                         temp_role=role, temp_action=original_action)
                
                if role == "professor" and not subject:
                    error = "Please enter your primary subject area to complete registration."
                    conn.close()
                    return render_template("auth.html", error=error, step="2", 
                                         temp_role=role, temp_action=original_action)

                try:
                    hashed_password = generate_password_hash(password)
                    c.execute("""
                    INSERT INTO users(full_name,role,prn,year,subject,username,password)
                    VALUES(?,?,?,?,?,?,?)
                    """,(full_name,role,prn,year,subject,username,hashed_password))
                    conn.commit()
                    error = "Account created successfully! You can now sign in with your credentials."
                    session.clear()
                    conn.close()
                    return redirect("/")
                except Exception as e:
                    error = "This username is already in use. Please choose a different username and try again."
                    session.clear()
                    conn.close()
                    return redirect("/")

            elif original_action == "login_step1":
                c.execute("""
                SELECT role,full_name,password FROM users
                WHERE username=?
                """,(username,))
                user = c.fetchone()

                if user and check_password_hash(user[2], password):
                    session.clear()
                    session["user"] = username
                    session["role"] = user[0]
                    session["name"] = user[1]

                    conn.close()
                    if user[0] == "professor":
                        return redirect("/admin")
                    else:
                        return redirect("/dashboard")
                else:
                    error = "Incorrect username or password. Please verify your credentials and try again."
                    session.clear()
                    conn.close()
                    return redirect("/")

        conn.close()

    # Pass session data to template
    temp_role = session.get("temp_role", "")
    temp_action = session.get("temp_action", "")
    
    return render_template("auth.html", error=error, step=step, 
                         temp_role=temp_role, temp_action=temp_action)


# ===== STUDENT DASHBOARD =====
@app.route("/dashboard")
def dashboard():
    if "user" not in session or session.get("role") != "student":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Stats
    c.execute("SELECT COUNT(*) FROM materials")
    total_materials = c.fetchone()[0]

    c.execute("SELECT COUNT(DISTINCT subject) FROM materials")
    total_subjects = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM materials WHERE date(uploaded_on) >= date('now', '-7 days')")
    recent_materials = c.fetchone()[0]

    conn.close()

    return render_template("dashboard.html",
                           name=session["name"],
                           total_materials=total_materials,
                           total_subjects=total_subjects,
                           recent_materials=recent_materials)


# ===== STUDENT AI CHATBOT (UPGRADED LOGIC) =====
@app.route("/student", methods=["GET","POST"])
def student():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        msg = request.form["message"].lower()

        intro = random.choice([
            "Analyzing your request…",
            "Searching DBATU materials… 📚",
            "Checking academic resources… 🔎"
        ])

        # ===== STEP 1: CHECK QA MAPPING TABLE =====
        c.execute("""
        SELECT qa.question, m.id, m.subject, m.unit_number, m.unit_name, 
               m.material_type, m.filename, m.reference_url
        FROM qa_mapping qa
        JOIN materials m ON qa.material_id = m.id
        WHERE LOWER(qa.question) LIKE ?
        LIMIT 5
        """, (f"%{msg}%",))
        
        qa_results = c.fetchall()

        if qa_results:
            # Found in QA mapping
            response = f"{intro}<br><br>📚 <strong>Found relevant materials:</strong><br><br>"
            
            for qa in qa_results:
                mat_id, subject, unit_num, unit_name, mat_type, filename, ref_url = qa[1:]
                
                # Badge color
                badge_color = {"NOTES": "blue", "ASSIGNMENT": "orange", "PYQ": "red", "REFERENCE": "purple"}.get(mat_type.upper(), "gray")
                
                response += f"<div class='material-card'>"
                response += f"<span class='badge badge-{badge_color}'>{mat_type}</span> "
                response += f"<strong>{subject} - Unit {unit_num}: {unit_name}</strong><br>"
                
                if filename:
                    response += f"<a href='/download/{mat_id}' class='download-link'>📥 Download {filename}</a><br>"
                
                if ref_url:
                    response += f"<a href='{ref_url}' target='_blank' class='ref-link'>🔗 Open Reference Link</a><br>"
                
                response += "</div><br>"
                
                # Track analytics
                c.execute("""
                INSERT INTO analytics(material_id, action_type, username, timestamp)
                VALUES(?,?,?,?)
                """, (mat_id, "view", session["user"], str(datetime.datetime.now())))

        else:
            # ===== STEP 2: FALLBACK TO KEYWORD SEARCH =====
            found_subject = None
            found_type = None
            found_semester = None
            found_unit = None

            # Detect subject
            c.execute("SELECT DISTINCT subject FROM materials")
            subjects = [row[0].lower() for row in c.fetchall()]
            for s in subjects:
                if s in msg:
                    found_subject = s.upper()

            # Detect type
            if "pyq" in msg or "previous year" in msg:
                found_type = "PYQ"
            elif "notes" in msg or "note" in msg:
                found_type = "NOTES"
            elif "assignment" in msg:
                found_type = "ASSIGNMENT"
            elif "reference" in msg:
                found_type = "REFERENCE"

            # Detect semester
            for i in range(1, 9):
                if f"sem {i}" in msg or f"semester {i}" in msg:
                    found_semester = str(i)

            # Detect unit
            for i in range(1, 7):
                if f"unit {i}" in msg:
                    found_unit = str(i)

            # Build query
            query = """
            SELECT id, subject, semester, unit_number, unit_name, 
                   material_type, filename, reference_url
            FROM materials WHERE 1=1
            """
            params = []

            if found_subject:
                query += " AND subject=?"
                params.append(found_subject)
            if found_type:
                query += " AND material_type=?"
                params.append(found_type)
            if found_semester:
                query += " AND semester=?"
                params.append(found_semester)
            if found_unit:
                query += " AND unit_number=?"
                params.append(found_unit)

            c.execute(query, params)
            materials = c.fetchall()

            if materials:
                response = f"{intro}<br><br>📚 <strong>Found {len(materials)} material(s):</strong><br><br>"
                
                for mat in materials:
                    mat_id, subject, semester, unit_num, unit_name, mat_type, filename, ref_url = mat
                    
                    badge_color = {"NOTES": "blue", "ASSIGNMENT": "orange", "PYQ": "red", "REFERENCE": "purple"}.get(mat_type.upper(), "gray")
                    
                    response += f"<div class='material-card'>"
                    response += f"<span class='badge badge-{badge_color}'>{mat_type}</span> "
                    response += f"<strong>{subject} - Sem {semester} - Unit {unit_num}: {unit_name}</strong><br>"
                    
                    if filename:
                        response += f"<a href='/download/{mat_id}' class='download-link'>📥 Download {filename}</a><br>"
                    
                    if ref_url:
                        response += f"<a href='{ref_url}' target='_blank' class='ref-link'>🔗 Open Reference Link</a><br>"
                    
                    response += "</div><br>"
                    
                    # Track analytics
                    c.execute("""
                    INSERT INTO analytics(material_id, action_type, username, timestamp)
                    VALUES(?,?,?,?)
                    """, (mat_id, "view", session["user"], str(datetime.datetime.now())))
            else:
                response = f"{intro}<br><br>❌ No matching material found. Try different keywords."

        conn.commit()

        # Save chat
        c.execute("""
        INSERT INTO chats(username,message,response,time)
        VALUES(?,?,?,?)
        """,(session["user"],msg,response,str(datetime.datetime.now())))
        conn.commit()

    # Load chats
    c.execute("""
    SELECT message,response FROM chats
    WHERE username=?
    ORDER BY id ASC
    """,(session["user"],))

    chat_history = c.fetchall()

    conn.close()

    return render_template("student.html",
                           chats=chat_history,
                           name=session["name"])


# ===== ADMIN ERP (UPDATED) =====
@app.route("/admin", methods=["GET","POST"])
def admin():
    if session.get("role") != "professor":
        return redirect("/")

    success = ""
    error = ""

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        subject = request.form["subject"].upper()
        semester = request.form["semester"]
        unit_number = request.form["unit_number"]
        unit_name = request.form["unit_name"]
        material_type = request.form["material_type"].upper()
        reference_url = request.form.get("reference_url", "")
        academic_year = request.form["academic_year"]

        file = request.files.get("file")
        
        if file and file.filename:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                
                c.execute("""
                INSERT INTO materials(subject,semester,unit_number,unit_name,material_type,
                                     filename,reference_url,academic_year,uploaded_on)
                VALUES(?,?,?,?,?,?,?,?,?)
                """,(subject,semester,unit_number,unit_name,material_type,
                     filename,reference_url,academic_year,str(datetime.datetime.now())))
                
                conn.commit()
                success = "Material uploaded successfully and is now available to students."
            else:
                error = "Invalid file format. Only PDF and DOCX files are accepted. Please check your file and try again."
        elif reference_url:
            # Reference-only upload (no file)
            c.execute("""
            INSERT INTO materials(subject,semester,unit_number,unit_name,material_type,
                                 filename,reference_url,academic_year,uploaded_on)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,(subject,semester,unit_number,unit_name,material_type,
                 "",reference_url,academic_year,str(datetime.datetime.now())))
            
            conn.commit()
            success = "Reference link added successfully and is now available to students."
        else:
            error = "Please upload a file (PDF or DOCX) or provide a reference URL before submitting."

    # Stats
    c.execute("SELECT COUNT(*) FROM materials")
    total_files = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM chats")
    total_queries = c.fetchone()[0]

    # Upload history (last 10)
    c.execute("""
    SELECT id, subject, unit_number, material_type, uploaded_on
    FROM materials
    ORDER BY id DESC
    LIMIT 10
    """)
    upload_history = c.fetchall()

    conn.close()

    return render_template("admin.html",
                           success=success,
                           error=error,
                           total_files=total_files,
                           total_queries=total_queries,
                           upload_history=upload_history,
                           name=session["name"])


# ===== FILE DOWNLOAD ROUTE =====
@app.route("/download/<int:material_id>")
def download_file(material_id):
    if "user" not in session:
        return redirect("/")
    
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    
    c.execute("SELECT filename FROM materials WHERE id=?", (material_id,))
    result = c.fetchone()
    
    if result and result[0]:
        filename = result[0]
        
        # Track download analytics
        c.execute("""
        INSERT INTO analytics(material_id, action_type, username, timestamp)
        VALUES(?,?,?,?)
        """, (material_id, "download", session["user"], str(datetime.datetime.now())))
        conn.commit()
        conn.close()
        
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    
    conn.close()
    return "File not found", 404


# ===== BROWSE MATERIALS PAGE =====
@app.route("/browse", methods=["GET"])
def browse():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get filter parameters
    semester = request.args.get("semester", "")
    subject = request.args.get("subject", "")
    unit = request.args.get("unit", "")
    material_type = request.args.get("material_type", "")

    # Build query
    query = """
    SELECT id, subject, semester, unit_number, unit_name, 
           material_type, filename, reference_url, academic_year
    FROM materials WHERE 1=1
    """
    params = []

    if semester:
        query += " AND semester=?"
        params.append(semester)
    if subject:
        query += " AND subject=?"
        params.append(subject.upper())
    if unit:
        query += " AND unit_number=?"
        params.append(unit)
    if material_type:
        query += " AND material_type=?"
        params.append(material_type.upper())

    query += " ORDER BY semester, unit_number"

    c.execute(query, params)
    materials = c.fetchall()

    # Get distinct values for filters
    c.execute("SELECT DISTINCT semester FROM materials ORDER BY semester")
    semesters = [row[0] for row in c.fetchall()]

    c.execute("SELECT DISTINCT subject FROM materials ORDER BY subject")
    subjects = [row[0] for row in c.fetchall()]

    c.execute("SELECT DISTINCT material_type FROM materials ORDER BY material_type")
    types = [row[0] for row in c.fetchall()]

    conn.close()

    return render_template("browse.html",
                           name=session["name"],
                           materials=materials,
                           semesters=semesters,
                           subjects=subjects,
                           types=types,
                           selected_semester=semester,
                           selected_subject=subject,
                           selected_unit=unit,
                           selected_type=material_type)


# ===== BOOKMARK MATERIAL =====
@app.route("/bookmark/<int:material_id>", methods=["POST"])
def bookmark(material_id):
    if "user" not in session:
        return jsonify({"success": False}), 401

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Check if already bookmarked
    c.execute("""
    SELECT id FROM bookmarks WHERE username=? AND material_id=?
    """, (session["user"], material_id))
    
    if c.fetchone():
        # Remove bookmark
        c.execute("""
        DELETE FROM bookmarks WHERE username=? AND material_id=?
        """, (session["user"], material_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "action": "removed"})
    else:
        # Add bookmark
        c.execute("""
        INSERT INTO bookmarks(username, material_id, bookmarked_on)
        VALUES(?,?,?)
        """, (session["user"], material_id, str(datetime.datetime.now())))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "action": "added"})


# ===== DELETE MATERIAL (PROFESSOR) =====
@app.route("/delete/<int:material_id>", methods=["POST"])
def delete_material(material_id):
    if session.get("role") != "professor":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get filename to delete from disk
    c.execute("SELECT filename FROM materials WHERE id=?", (material_id,))
    result = c.fetchone()
    
    if result and result[0]:
        filename = result[0]
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    # Delete from database
    c.execute("DELETE FROM materials WHERE id=?", (material_id,))
    c.execute("DELETE FROM bookmarks WHERE material_id=?", (material_id,))
    c.execute("DELETE FROM analytics WHERE material_id=?", (material_id,))
    
    conn.commit()
    conn.close()

    return redirect("/admin")


# ===== ANALYTICS PAGE (PROFESSOR) =====
@app.route("/analytics")
def analytics():
    if session.get("role") != "professor":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Most downloaded materials
    c.execute("""
    SELECT m.subject, m.unit_name, m.material_type, COUNT(a.id) as downloads
    FROM analytics a
    JOIN materials m ON a.material_id = m.id
    WHERE a.action_type = 'download'
    GROUP BY a.material_id
    ORDER BY downloads DESC
    LIMIT 10
    """)
    most_downloaded = c.fetchall()

    # Most searched questions (from chats)
    c.execute("""
    SELECT message, COUNT(*) as count
    FROM chats
    GROUP BY message
    ORDER BY count DESC
    LIMIT 10
    """)
    most_searched = c.fetchall()

    conn.close()

    return render_template("analytics.html",
                           name=session["name"],
                           most_downloaded=most_downloaded,
                           most_searched=most_searched)


@app.route("/logout")
def logout():
    log.info(f"User '{session.get('user', 'unknown')}' logged out.")
    session.clear()
    return redirect("/")


# ===== GLOBAL ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(e):
    log.warning(f"404 on {request.path}")
    return jsonify({"error": "Not found", "path": request.path}), 404


@app.errorhandler(500)
def internal_error(e):
    log.error(f"500 on {request.path}: {e}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)