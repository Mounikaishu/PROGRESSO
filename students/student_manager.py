# students/student_manager.py
import csv
from pathlib import Path
from extensions import db
from models import Student

STUDENTS_CSV = Path("students/students.csv")

def load_students():
    students = {}
    if not STUDENTS_CSV.exists():
        return students

    with open(STUDENTS_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            regno = (row.get("regno") or row.get("RegNo") or "").strip()
            github = (row.get("github") or row.get("GitHub") or "").strip()
            leetcode = (row.get("leetcode") or row.get("LeetCode") or "").strip()
            codeforces = (row.get("codeforces") or row.get("Codeforces") or "").strip()

            if not regno:
                continue

            students[regno] = {
                "github": github,
                "leetcode": leetcode,
                "codeforces": codeforces
            }
    return students

def get_student_platform_usernames(regno):
    all_students = load_students()
    return all_students.get(regno)

def add_student_to_db(regno, github="", leetcode="", codeforces=""):
    """Helper to add a Student record to the DB (use inside app.app_context())."""
    existing = Student.query.filter_by(regno=regno).first()
    if existing:
        existing.github = github
        existing.leetcode = leetcode
        existing.codeforces = codeforces
    else:
        s = Student(regno=regno, github=github, leetcode=leetcode, codeforces=codeforces)
        db.session.add(s)
    db.session.commit()

def generate_summary_csv(all_student_data):
    SUMMARY_CSV = Path("reports/summary_report.csv")
    SUMMARY_CSV.parent.mkdir(exist_ok=True)
    with open(SUMMARY_CSV, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["RegNo", "GitHub", "LeetCode", "Codeforces", "No. of Projects", "Total Commits", "LC solved", "CF solved", "CF rating"])
        for row in all_student_data:
            usernames = row.get("usernames", {})
            writer.writerow([
                row.get("regno", ""),
                usernames.get("github", ""),
                usernames.get("leetcode", ""),
                usernames.get("codeforces", ""),
                row.get("repos_count", 0),
                row.get("total_commits", 0),
                row.get("leetcode_total_solved", 0),
                row.get("cf_solved_count", 0),
                row.get("cf_rating", "NA")
            ])
    print(f"✔️ Summary CSV generated at {SUMMARY_CSV}")
