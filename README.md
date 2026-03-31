# DBATU AI-Powered Study Material Assistant

A Flask-based academic portal for Dr. Babasaheb Ambedkar Technological University (DBATU) that provides intelligent study material management and AI-powered chatbot assistance.

## Features

- 2-step secure authentication (Student/Professor)
- AI chatbot with intelligent material search
- Professor admin panel for uploading materials
- Browse materials with advanced filters
- File download functionality
- Analytics dashboard
- Material bookmarking
- Upload history tracking

## Installation

1. Install dependencies:
`ash
pip install -r requirements.txt
`

2. Run the application:
`ash
python app.py
`

3. Access the portal at http://localhost:5000

## Default Credentials

- Username: dmin
- Password: dmin123
- Role: Professor

## Environment Configuration

Create a .env file in the project root:
`
SECRET_KEY=your_secure_secret_key_here
FLASK_ENV=production
DEBUG=False
`

## Database Reset

To reset the database and clear all user data:
`ash
python reset_database.py
`

## Project Structure

`
├── app.py                  # Main Flask application
├── reset_database.py       # Database reset utility
├── .env                    # Environment configuration (git-ignored)
├── database.db            # SQLite database (auto-created, git-ignored)
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/              # Stylesheets
│   ├── files/            # Uploaded materials
│   └── images/           # Static images
└── templates/            # HTML templates
`

## Tech Stack

- **Backend**: Python, Flask 3.0+
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Security**: Werkzeug (password hashing)
- **Configuration**: python-dotenv

## Supported File Formats

- PDF (.pdf)
- DOCX (.docx)

## Security Notes

- Passwords are securely hashed using Werkzeug
- Session-based authentication
- Environment variables for sensitive configuration
- CSRF protection via Flask sessions
