# DBATU AI-Powered Study Material Assistant

A Flask-based academic portal for Dr. Babasaheb Ambedkar Technological University (DBATU) that provides intelligent study material management and AI-powered chatbot assistance.

## Features

- 2-step authentication (Student/Professor)
- AI chatbot with intelligent material search
- Professor admin panel for uploading materials
- Browse materials with advanced filters
- File download functionality
- Analytics dashboard
- Material bookmarking
- Upload history tracking

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the portal at `http://localhost:5000`

## Default Credentials

- Username: `admin`
- Password: `admin123`
- Role: Professor

## Project Structure

```
├── app.py              # Main Flask application
├── database.py         # Database schema
├── database.db         # SQLite database (auto-created)
├── requirements.txt    # Python dependencies
├── static/
│   ├── css/           # Stylesheets
│   ├── files/         # Uploaded materials
│   └── images/        # Static images
└── templates/         # HTML templates
```

## Tech Stack

- Backend: Flask (Python)
- Database: SQLite3
- Frontend: HTML, CSS, JavaScript
- Authentication: Session-based

## Notes

- Supported file formats: PDF, DOCX
- Database auto-initializes on first run
- Admin account created automatically
- 40 pre-seeded QA questions for chatbot
