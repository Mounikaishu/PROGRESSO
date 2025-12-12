from extensions import db

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    regno = db.Column(db.String(50), unique=True, nullable=False)

    github = db.Column(db.String(120))
    leetcode = db.Column(db.String(120))
    codeforces = db.Column(db.String(120))

    github_projects = db.Column(db.Integer, default=0)
    github_commits = db.Column(db.Integer, default=0)

    leetcode_solved = db.Column(db.Integer, default=0)

    cf_solved = db.Column(db.Integer, default=0)
    cf_rating = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Student {self.regno}>"
