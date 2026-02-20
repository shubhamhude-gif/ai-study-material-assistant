from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/files"

# ================= HOME (CHATBOT) =================
@app.route("/", methods=["GET", "POST"])
def home():

    chat_history = []

    if request.method == "POST":

        user_message = request.form["message"].lower()

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        found_subject = None
        found_type = None
        found_year = None

        # Get subjects dynamically
        cursor.execute("SELECT DISTINCT subject FROM materials")
        subjects = [row[0].lower() for row in cursor.fetchall()]

        # Detect subject
        for s in subjects:
            if s in user_message:
                found_subject = s.upper()

        # Detect type
        if "pyq" in user_message:
            found_type = "PYQ"
        elif "notes" in user_message:
            found_type = "NOTES"

        # Detect year
        for word in user_message.split():
            if word.isdigit():
                found_year = word

        query = "SELECT file_name FROM materials WHERE 1=1"
        params = []

        if found_subject:
            query += " AND subject=?"
            params.append(found_subject)

        if found_type:
            query += " AND type=?"
            params.append(found_type)

        if found_year:
            query += " AND year=?"
            params.append(found_year)

        cursor.execute(query, params)
        result = cursor.fetchall()

        if result:
            response = "Found files:<br>" + "<br>".join(
                [f"<a href='/static/files/{r[0]}' target='_blank'>{r[0]}</a>" for r in result]
            )
        else:
            cursor.execute("SELECT DISTINCT subject, type FROM materials")
            suggestions = cursor.fetchall()

            suggestion_text = "<br>".join(
                [f"{s[0]} {s[1]}" for s in suggestions]
            )

            response = "No material found.<br><br>Try these:<br>" + suggestion_text

        conn.close()

        chat_history.append(("You", user_message))
        chat_history.append(("Bot", response))

    return render_template("index.html", chat_history=chat_history)


# ================= ADMIN PANEL =================
@app.route("/admin", methods=["GET", "POST"])
def admin():

    success_message = ""

    if request.method == "POST":

        subject = request.form["subject"].upper()
        material_type = request.form["type"].upper()
        year = request.form["year"]

        file = request.files["file"]
        filename = file.filename

        # Save file to folder
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        # Save to database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO materials (subject, type, year, file_name)
        VALUES (?, ?, ?, ?)
        """, (subject, material_type, year, filename))

        conn.commit()
        conn.close()

        success_message = "Upload successful!"

    return render_template(
        "admin.html",
        success_message=success_message
    )


# ================= RUN APP =================
if __name__ == "__main__":
    app.run(debug=True)
