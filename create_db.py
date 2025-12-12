# create_db.py
from app import app
from extensions import db
from models import Student

def main():
    with app.app_context():
        db.create_all()
        # add a sample student if not present
        regno = "1275"
        existing = Student.query.filter_by(regno=regno).first()
        if not existing:
            s = Student(
                regno=regno,
                github="Mounikaishu",
                leetcode="Mounika_kommireddyTaqai3",
                codeforces="Mounika_7897"
            )
            db.session.add(s)
            db.session.commit()
            print("Added sample student", regno)
        else:
            print("Sample student already exists:", regno)
        print("DB initialised at sqlite:///students.db")

if __name__ == "__main__":
    main()
