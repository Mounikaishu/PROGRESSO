import base64
from pathlib import Path

FONT_DATA = b"""
AAEAAAASAQAABAAgR0RFRrRCsIIAAAC8AAAAYGNtYXAAogBsAAABHAAAAExnYXNwAAAAEAAAAXAAAAAIZ2x5ZrYkYd4AAAGgAAABNGhlYWQK1x+oAAAB8AAAADZoaGVhB8gCwwAAAfQAAAAkaG10eBEOA00AAAIAAAAAIGxvY2EDswUKAAACJAAAAAxtYXhwABoALgAAAjQAAAAgbmFtZQEBAQkAAAI4AAABwnBvc3QAAwAAAAAD4AAAACBwcmVwAAEAAAAABAAAAAIAAQAAC4LwvwA...
"""

def create_font():
    path = Path("reports/DejaVuSans.ttf")
    decoded = base64.b64decode(FONT_DATA)
    with open(path, "wb") as f:
        f.write(decoded)
    print("Font created:", path)
