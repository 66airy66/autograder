import os
import io
import csv
from datetime import date

from flask import (
    Flask, render_template, request, redirect, session, flash, Response
)
import mysql.connector

# --- package-relative imports (important) ---
from .config import db_config, SECRET_KEY, DEBUG
from .utils.hash_util import hash_password, verify_password
from .utils.grading import grade_submission  # stub or real grader
# -------------------------------------------

# Ensure Flask can always find templates/static no matter where it's launched
BASE_DIR = os.path.dirname(__file__)
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.secret_key = SECRET_KEY


def get_db():
    """Create a new DB connection."""
    return mysql.connector.connect(**db_config)


@app.route("/")
def index():
    return redirect("/login")


# ------------- Auth -------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        pw_hash = hash_password(request.form["password"])

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO students (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, pw_hash),
            )
            conn.commit()
            flash("Account created. Please log in.")
            return redirect("/login")
        finally:
            cur.close()
            conn.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        pw = request.form["password"]

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM students WHERE email=%s", (email,))
            student = cur.fetchone()
            if student and verify_password(pw, student["password_hash"]):
                session["student_id"] = student["id"]
                return redirect("/submit")
            else:
                flash("Invalid email or password.")
        finally:
            cur.close()
            conn.close()

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
# --------------------------------


# ------------- Core flows -------------
@app.route("/submit", methods=["GET", "POST"])
def submit():
    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM questions LIMIT 1")
        question = cur.fetchone()
        if not question:
            return "No questions available.", 404

        if request.method == "POST":
            submitted_sql = request.form["sql"]
            score = grade_submission(submitted_sql, question["id"])

            cur2 = conn.cursor()
            try:
                cur2.execute(
                    "INSERT INTO submissions (student_id, question_id, submitted_sql, score) "
                    "VALUES (%s, %s, %s, %s)",
                    (session["student_id"], question["id"], submitted_sql, score),
                )
                conn.commit()
            finally:
                cur2.close()

            return redirect("/dashboard")

        return render_template("submit.html", question=question)
    finally:
        cur.close()
        conn.close()


@app.route("/dashboard")
def dashboard():
    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT s.id, q.prompt, s.submitted_sql, s.score, s.submitted_at
            FROM submissions s
            JOIN questions q ON s.question_id = q.id
            WHERE s.student_id = %s
            ORDER BY s.submitted_at DESC
            """,
            (session["student_id"],),
        )
        submissions = cur.fetchall()
        return render_template("dashboard.html", submissions=submissions)
    finally:
        cur.close()
        conn.close()


@app.route("/resubmit/<int:submission_id>", methods=["GET", "POST"])
def resubmit(submission_id):
    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT * FROM submissions WHERE id=%s AND student_id=%s",
            (submission_id, session["student_id"]),
        )
        old = cur.fetchone()
        if not old:
            return "Submission not found or unauthorized", 404

        cur.execute("SELECT * FROM questions WHERE id=%s", (old["question_id"],))
        question = cur.fetchone()
        if not question:
            return "Question not found", 404

        if request.method == "POST":
            sql_input = request.form["sql"]
            raw_score = grade_submission(sql_input, question["id"])
            penalty = 0.5 if date.today() > question["due_date"] else 1.0
            score = int(raw_score * penalty)

            cur2 = conn.cursor()
            try:
                cur2.execute(
                    "INSERT INTO submissions (student_id, question_id, submitted_sql, score) "
                    "VALUES (%s, %s, %s, %s)",
                    (session["student_id"], question["id"], sql_input, score),
                )
                conn.commit()
            finally:
                cur2.close()

            return redirect("/dashboard")

        return render_template("resubmit.html", question=question, old=old)
    finally:
        cur.close()
        conn.close()
# -------------------------------------


# ------------- Reports / Extras -------------
@app.route("/leaderboard")
def leaderboard():
    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT
                s.id,
                s.name,
                AVG(best_submissions.best_score) AS average_score
            FROM students s
            JOIN (
                SELECT student_id, question_id, MAX(score) AS best_score
                FROM submissions
                GROUP BY student_id, question_id
            ) AS best_submissions
              ON s.id = best_submissions.student_id
            GROUP BY s.id, s.name
            ORDER BY average_score DESC
            """
        )
        rankings = cur.fetchall()

        for i, r in enumerate(rankings):
            r["rank"] = i + 1

        student_id = session["student_id"]
        current_student = next((r for r in rankings if r["id"] == student_id), None)

        top4 = rankings[:4]
        return render_template(
            "leaderboard.html",
            rankings=rankings,
            top4=top4,
            current_student=current_student,
        )
    finally:
        cur.close()
        conn.close()


@app.route("/history")
def history():
    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT q.prompt, q.due_date, q.max_score,
                   s.submitted_sql, s.score, s.submitted_at
            FROM submissions s
            JOIN questions q ON s.question_id = q.id
            WHERE s.student_id = %s
            ORDER BY s.submitted_at DESC
            """,
            (session["student_id"],),
        )
        records = cur.fetchall()
        return render_template("history.html", records=records)
    finally:
        cur.close()
        conn.close()


@app.route("/regrade/all")
def regrade_all():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT s.id as submission_id, s.submitted_sql, s.submitted_at,
                   q.id as question_id, q.due_date, q.max_score
            FROM submissions s
            JOIN questions q ON s.question_id = q.id
            """
        )
        all_submissions = cur.fetchall()

        for sub in all_submissions:
            raw_score = grade_submission(sub["submitted_sql"], sub["question_id"])
            penalty = 0.5 if sub["submitted_at"].date() > sub["due_date"] else 1.0
            new_score = int(raw_score * penalty)
            cur.execute(
                "UPDATE submissions SET score=%s WHERE id=%s",
                (new_score, sub["submission_id"]),
            )

        conn.commit()
        return render_template("regrade_result.html", updated=len(all_submissions))
    finally:
        cur.close()
        conn.close()


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "student_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        current_pw = request.form["current_password"]
        new_pw = request.form["new_password"]

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT password_hash FROM students WHERE id = %s",
                (session["student_id"],),
            )
            student = cur.fetchone()

            if student and verify_password(current_pw, student["password_hash"]):
                new_hash = hash_password(new_pw)
                cur2 = conn.cursor()
                try:
                    cur2.execute(
                        "UPDATE students SET password_hash = %s WHERE id = %s",
                        (new_hash, session["student_id"]),
                    )
                    conn.commit()
                finally:
                    cur2.close()
                flash("Password changed successfully.")
            else:
                flash("Current password incorrect.")
        finally:
            cur.close()
            conn.close()

        return redirect("/change_password")

    return render_template("change_password.html")
# ---------------------------------------------


@app.route("/export_submissions")
def export_submissions():
    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT q.prompt, q.due_date, q.max_score,
                   s.submitted_sql, s.score, s.submitted_at,
                   CASE
                       WHEN DATE(s.submitted_at) > q.due_date AND s.score = q.max_score * 0.5 THEN 'Correct (Late)'
                       WHEN s.score = q.max_score THEN 'Correct'
                       ELSE 'Wrong'
                   END as status,
                   CASE
                       WHEN DATE(s.submitted_at) > q.due_date THEN 'Late'
                       ELSE 'On Time'
                   END as timing
            FROM submissions s
            JOIN questions q ON s.question_id = q.id
            WHERE s.student_id = %s
            ORDER BY s.submitted_at DESC
            """,
            (session["student_id"],),
        )
        rows = cur.fetchall()

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow(
            ["Prompt", "Due Date", "Submitted SQL", "Score", "Submitted At", "Status", "Timing"]
        )

        for row in rows:
            writer.writerow([row[0], row[1], row[3], row[4], row[5], row[6], row[7]])

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=submissions.csv"},
        )
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=DEBUG, host="127.0.0.1", port=5000)