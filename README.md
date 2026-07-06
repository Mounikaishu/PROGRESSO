# Student Progress Tracker

A small Flask application for tracking student coding progress across GitHub, LeetCode, and Codeforces.

## Features

- Add students by registration number and platform usernames
- View students in a simple web interface
- Generate a summary CSV report for all or a limited number of students
- Generate a PDF report for an individual student with GitHub repo info and platform stats
- Fetch GitHub repository and commit counts, LeetCode solved count, and Codeforces solved count + rating
- Optional GitHub API token support for higher rate limits

## Requirements

- Python 3.10+ (recommended)
- Flask
- Flask-SQLAlchemy
- Requests
- python-dotenv
- fpdf

## Setup

1. Create a virtual environment

```bash
python -m venv venv
```

2. Activate the virtual environment

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Initialize the database and create a sample student

```bash
python create_db.py
```

## Environment Variables

The app supports these environment variables:

- `FLASK_SECRET` - secret key for Flask session encryption (defaults to `secret-for-dev`)
- `GITHUB_TOKEN` - optional GitHub personal access token for authenticated API requests

## Running the App

Set the Flask app and start the server:

Windows PowerShell:

```powershell
$env:FLASK_APP = "app.py"
flask run
```

Then open `http://127.0.0.1:5000/` in your browser.

## How It Works

- `app.py` defines the Flask routes for adding, updating, deleting students, generating a summary CSV, generating PDF reports, and exposing a simple API endpoint.
- `students/student_manager.py` loads student platform usernames from `students/students.csv`, creates summary CSV files, and provides helper functions.
- `apis/collectors.py` fetches data from GitHub, LeetCode, and Codeforces, including retries and rate-limited API handling.
- `reports/pdf_report.py` builds a PDF report using `fpdf` and saves it to `reports/`.
- `create_db.py` creates the SQLite database and adds a sample student record.

## Project Structure

- `app.py` - Flask application entry point
- `create_db.py` - database initialization script
- `extensions.py` - database extension initialization
- `models.py` - SQLAlchemy models
- `students/student_manager.py` - student loading and summary CSV generation
- `apis/collectors.py` - platform data collectors
- `reports/pdf_report.py` - PDF report generation
- `templates/index.html` - web UI template
- `requirements.txt` - Python dependencies

## Notes

- Student records are loaded from `students/students.csv`.
- Reports are saved to the `reports/` folder.
- The API endpoint `/api/student/<regno>` returns student platform mappings in JSON.

## Troubleshooting

- If GitHub API requests fail, set `GITHUB_TOKEN` and restart the app.
- If the app cannot find `students/students.csv`, create the file with columns: `regno,github,leetcode,codeforces`.
- Use `pip install -r requirements.txt` again if dependencies are missing.
