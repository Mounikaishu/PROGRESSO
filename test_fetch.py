# test_fetch.py
from students.student_manager import load_students, get_student_platform_usernames
from apis.collectors import fetch_all_for_student
import json

students = load_students()
print("Loaded students:", students)
regno = "1275"
mapping = get_student_platform_usernames(regno)
print("Mapping for", regno, "=", mapping)
combined = fetch_all_for_student(mapping, parallel=False)
print("Combined result:")
print(json.dumps(combined, indent=2, ensure_ascii=False))
