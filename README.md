# SQL Autograder

A Flask-based web application for submitting and automatically grading SQL queries against a predefined database.

## 📂 Project Structure

tcx2003project/
├── autograder/
│   ├── flask_app.py        # Main Flask application – handles routes, database logic, and authentication.
│   ├── templates/          # HTML templates rendered by Flask.
│   │   ├── layout.html     # Base layout file (navbar, flash messages, page structure).
│   │   ├── login.html      # Login page for students.
│   │   ├── register.html   # Student registration page.
│   │   ├── dashboard.html  # Dashboard showing student’s progress and stats.
│   │   ├── submit.html     # SQL submission form.
│   │   ├── history.html    # Page showing all previous submissions for the student.
│   │   └── leaderboard.html# Displays top students by score.
│   ├── static/             # Static files (CSS, JS, images).
│   │   └── css/
│   │       └── style.css   # Main stylesheet for all pages.
├── config.py               # Configuration file (DB credentials, secret key, debug flag).
├── requirements.txt        # Python dependencies.
├── kanhampujar_pythonanywhere_com_wsgi.py
│                           # WSGI entry point for PythonAnywhere hosting.
└── README.md               # This file.

## ⚙️ How It Works

1. **Authentication**
   - Students can register, log in, and change their password.
   - Session data is used to track logged-in users.

2. **Submitting Queries**
   - Students can submit SQL queries for predefined questions.
   - The app runs the query on the MySQL database and compares results with the expected answer.

3. **Grading**
   - Compares query output to expected output.
   - Marks the submission as correct or incorrect.

4. **History**
   - Students can view their previous submissions.

5. **Leaderboard**
   - Displays top students based on scores.

## 🗄 Database Structure

The database contains:

- **students** – Stores login credentials and profile info.
- **questions** – Contains SQL challenges.
- **expected_answers** – Stores expected query results for grading.
- **submissions** – Stores each submission and whether it was correct.

## 🚀 Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   
2. **Set environment variables (for production)**
  export DB_HOST="your-db-host"
  export DB_USER="your-db-user"
  export DB_PASSWORD="your-db-pass"
  export DB_NAME="your-db-name"
  export SECRET_KEY="some-random-secret"

3. **Run locally**
   flask run

4. **Deploy on PythonAnywhere**
  •	Upload files.
	•	Set environment variables in the Web tab.
	•	Point the WSGI file to import app from flask_app.py.
