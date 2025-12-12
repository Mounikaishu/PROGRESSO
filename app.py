# app.py
import os
from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from pathlib import Path

# Local modules
from extensions import db
from models import Student

from students.student_manager import load_students, get_student_platform_usernames, generate_summary_csv
from apis.collectors import fetch_all_for_student
from reports.pdf_report import generate_student_pdf

# ------------------------------------------------------------
# FLASK + DATABASE SETUP
# ------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "secret-for-dev")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------
@app.route("/")
def index():
    students = load_students()
    return render_template("index.html", students=students)


# ------------------------------------------------------------
# ADD STUDENT
# ------------------------------------------------------------
@app.route("/add-student", methods=["POST"])
def route_add_student():
    regno = request.form.get("regno").strip()
    github = request.form.get("github").strip()
    leetcode = request.form.get("leetcode").strip()
    codeforces = request.form.get("codeforces").strip()

    if not regno:
        flash("RegNo is required.", "danger")
        return redirect(url_for("index"))

    existing = Student.query.filter_by(regno=regno).first()
    if existing:
        flash("Student already exists!", "warning")
        return redirect(url_for("index"))

    s = Student(regno=regno, github=github, leetcode=leetcode, codeforces=codeforces)
    db.session.add(s)
    db.session.commit()

    flash("Student added successfully!", "success")
    return redirect(url_for("index"))


# ------------------------------------------------------------
# UPDATE STUDENT
# ------------------------------------------------------------
@app.route("/update-student", methods=["POST"])
def route_update_student():
    regno = request.form.get("regno")
    github = request.form.get("github", "")
    leetcode = request.form.get("leetcode", "")
    codeforces = request.form.get("codeforces", "")

    student = Student.query.filter_by(regno=regno).first()
    if not student:
        flash("Student not found!", "danger")
        return redirect(url_for("index"))

    student.github = github
    student.leetcode = leetcode
    student.codeforces = codeforces
    db.session.commit()

    flash("Student updated!", "success")
    return redirect(url_for("index"))


# ------------------------------------------------------------
# DELETE STUDENT
# ------------------------------------------------------------
@app.route("/delete-student/<regno>", methods=["POST"])
def route_delete_student(regno):
    student = Student.query.filter_by(regno=regno).first()
    if not student:
        flash("Student not found!", "danger")
        return redirect(url_for("index"))

    db.session.delete(student)
    db.session.commit()

    flash("Student deleted!", "success")
    return redirect(url_for("index"))


# ------------------------------------------------------------
# SUMMARY CSV
# ------------------------------------------------------------
@app.route("/generate-summary", methods=["POST"])
def generate_summary():
    count_raw = request.form.get("count")
    try:
        count = int(count_raw) if count_raw else None
    except:
        count = None

    students = load_students()
    items = list(students.items())
    if count:
        items = items[:count]

    all_data = []
    for regno, mapping in items:
        try:
            combined = fetch_all_for_student(mapping, parallel=True)
            gh = combined.get("github", {})
            lc = combined.get("leetcode", {})
            cf = combined.get("codeforces", {})

            all_data.append({
                "regno": regno,
                "usernames": mapping,
                "repos_count": gh.get("repos_count", 0),
                "total_commits": gh.get("total_commits_estimate", 0),
                "leetcode_total_solved": lc.get("total_solved", 0),
                "cf_solved_count": cf.get("solved_count", 0),
                "cf_rating": cf.get("rating", "NA")
            })
        except Exception as e:
            print("ERROR:", e)

    generate_summary_csv(all_data)
    return send_file("reports/summary_report.csv", as_attachment=True)


# ------------------------------------------------------------
# PDF GENERATION
# ------------------------------------------------------------
@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    regno = request.form.get("regno").strip()
    mapping = get_student_platform_usernames(regno)

    if not mapping:
        flash("Student not found", "danger")
        return redirect(url_for("index"))

    combined = fetch_all_for_student(mapping, parallel=True)
    repo_list = []

    # GitHub
    gh = combined.get("github", {})
    for repo in gh.get("repos", []):
        repo_list.append({
            "name": repo.get("name", ""),
            "commits_count": repo.get("commits_count", 0),
            "last_commit_date": repo.get("last_commit_date", ""),
            "html_url": repo.get("html_url", "")
        })

    # LeetCode
    lc = combined.get("leetcode", {})
    repo_list.append({
        "name": f"LeetCode — Solved: {lc.get('total_solved', 0)}",
        "commits_count": lc.get("total_solved", 0),
        "last_commit_date": "",
        "html_url": f"https://leetcode.com/{mapping.get('leetcode', '')}"
    })

    # Codeforces
    cf = combined.get("codeforces", {})
    repo_list.append({
        "name": f"Codeforces — Solved: {cf.get('solved_count', 0)} | Rating: {cf.get('rating', 'NA')}",
        "commits_count": cf.get("solved_count", 0),
        "last_commit_date": "",
        "html_url": f"https://codeforces.com/profile/{mapping.get('codeforces', '')}"
    })

    pdf_path = generate_student_pdf(regno, mapping, repo_list)
    return send_file(pdf_path, as_attachment=True)


# ------------------------------------------------------------
# API ENDPOINT
# ------------------------------------------------------------
@app.route("/api/student/<regno>")
def api_student(regno):
    mapping = get_student_platform_usernames(regno)
    if not mapping:
        return jsonify({"error": "not found"}), 404

    combined = fetch_all_for_student(mapping, parallel=True)
    return jsonify({"regno": regno, "usernames": mapping, "platforms": combined})


# ------------------------------------------------------------
# MAIN RUN
# ------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
