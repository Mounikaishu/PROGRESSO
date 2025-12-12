# reports/pdf_report.py
from fpdf import FPDF
from pathlib import Path

PDF_DIR = Path("reports")
PDF_DIR.mkdir(parents=True, exist_ok=True)

# Unicode-safe font
FONT_PATH = Path("fonts/DejaVuSans.ttf")


class PDF(FPDF):
    pass


def load_font(pdf):
    """Load Unicode DejaVu or safely fall back to Arial."""
    if FONT_PATH.exists():
        try:
            pdf.add_font("DejaVu", "", str(FONT_PATH), uni=True)
            pdf.set_font("DejaVu", size=10)
            return "DejaVu"
        except:
            pass

    pdf.set_font("Arial", size=10)
    return "Arial"


def shorten(pdf, text, max_width):
    """Shorten text to fit inside cell width."""
    if pdf.get_string_width(text) <= max_width:
        return text

    ell = "..."
    for cut in range(len(text), 0, -1):
        new = text[:cut] + ell
        if pdf.get_string_width(new) <= max_width:
            return new

    return text


def draw_header(pdf, x, y, widths, headers, h):
    pdf.set_xy(x, y)
    pdf.set_font_size(11)
    for i, header in enumerate(headers):
        pdf.cell(widths[i], h, header, border=1, align="C")
    pdf.ln(h)
    pdf.set_font_size(10)


def generate_student_pdf(regno, mapping, repos):
    pdf = PDF(orientation="L", unit="mm", format="A4")
    margin = 10
    pdf.set_margins(margin, margin, margin)
    pdf.set_auto_page_break(auto=False)

    font = load_font(pdf)
    pdf.add_page()

    page_w = pdf.w - 2 * margin

    # Column widths
    w_name = 90
    w_commits = 30
    w_last = 40
    w_url = page_w - (w_name + w_commits + w_last)

    widths = [w_name, w_commits, w_last, w_url]
    headers = ["Name / Project", "Commits", "Last Update", "URL"]
    row_h = 6

    x = margin
    y_start = margin + 12

    # TITLE
    pdf.set_font(font, size=14)
    pdf.set_xy(x, margin)
    pdf.cell(0, 8, f"Student Coding Report - {regno}", ln=True)

    # HEADER
    pdf.set_font(font, size=10)
    draw_header(pdf, x, y_start, widths, headers, row_h)

    y = y_start + row_h

    def need_page(extra_h):
        nonlocal y
        if y + extra_h > pdf.h - margin:
            pdf.add_page()
            pdf.set_font(font, size=14)
            pdf.set_xy(x, margin)
            pdf.cell(0, 8, f"Student Coding Report - {regno} (cont.)", ln=True)

            pdf.set_font(font, size=10)
            draw_header(pdf, x, margin + 12, widths, headers, row_h)
            y = margin + 12 + row_h

    for r in repos:
        name = str(r.get("name", ""))
        commits = str(r.get("commits_count", ""))
        last = str(r.get("last_commit_date", ""))
        url = str(r.get("html_url", ""))

        # Estimate row height based on name + last
        name_lines = max(1, int(pdf.get_string_width(name) / (w_name - 2)) + 1)
        last_lines = max(1, int(pdf.get_string_width(last) / (w_last - 2)) + 1)

        lines = max(name_lines, last_lines)
        h = max(6, lines * 5)

        need_page(h)

        # NAME
        pdf.set_xy(x, y)
        pdf.multi_cell(w_name, 5, name, border=1)

        # COMMITS
        pdf.set_xy(x + w_name, y)
        pdf.multi_cell(w_commits, 5, commits, border=1, align="C")

        # LAST DATE
        pdf.set_xy(x + w_name + w_commits, y)
        pdf.multi_cell(w_last, 5, last, border=1, align="C")

        # URL (Short version)
        short_url = shorten(pdf, url, w_url - 4)

        pdf.set_xy(x + w_name + w_commits + w_last, y)
        pdf.multi_cell(w_url, 5, short_url, border=1)

        y += h

    # Output
    out = PDF_DIR / f"{regno}_report.pdf"
    pdf.output(str(out))

    return str(out)
