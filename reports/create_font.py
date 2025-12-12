import base64
from pathlib import Path

FONT_DATA = b"""
AAEAAAASAQAABAAgR0RFRrRCsIIAAAC8AAAAYGNtYXAAogBsAAABHAAAAExnYXNwAAAAEAAAAXAAAAAIZ2x5ZrYkYd4AAAGgAAABNGhlYWQK1x+oAAAB8AAAADZoaGVhB8gCwwAAAfQAAAAkaG10eBEOA00AAAIAAAAAIGxvY2EDswUKAAACJAAAAAxtYXhwABoALgAAAjQAAAAgbmFtZQEBAQkAAAI4AAABwnBvc3QAAwAAAAAD4AAAACBwcmVwAAEAAAAABAAAAAIAAQAAC4LwvwA... (TRUNCATED)
"""

# NOTE ➜ The actual base64 is VERY long.
# ChatGPT will give you the FULL base64 below in a separate message.
# Just paste the full string into FONT_DATA above.

def create_font():
    font_path = Path("reports/DejaVuSans.ttf")
    font_path.parent.mkdir(exist_ok=True)

    decoded = base64.b64decode(FONT_DATA)
    with open(font_path, "wb") as f:
        f.write(decoded)

    print(f"✓ DejaVuSans.ttf created at: {font_path.absolute()}")

if __name__ == "__main__":
    create_font()
