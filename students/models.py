# students/models.py
from extensions import db

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    regno = db.Column(db.String(50), unique=True, nullable=False)

    github = db.Column(db.String(120), nullable=True)
    leetcode = db.Column(db.String(120), nullable=True)
    codeforces = db.Column(db.String(120), nullable=True)

    # cached stats (optional — can be updated later)
    github_projects = db.Column(db.Integer, default=0)
    github_commits = db.Column(db.Integer, default=0)

    leetcode_solved = db.Column(db.Integer, default=0)

    cf_solved = db.Column(db.Integer, default=0)
    cf_rating = db.Column(db.Integer, default=0)

    def to_mapping(self):
        """Return platform mapping used by collectors.fetch_all_for_student"""
        return {
            "github": self.github or "",
            "leetcode": self.leetcode or "",
            "codeforces": self.codeforces or ""
        }

    def __repr__(self):
        return f"<Student {self.regno}>"
