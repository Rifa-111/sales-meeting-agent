from fpdf import FPDF
import re


def brief_to_pdf(markdown_text: str) -> bytes:
    """Convert markdown brief to PDF bytes."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(20, 20, 20)

    # Strip markdown syntax for clean PDF output
    lines = markdown_text.split("\n")

    for line in lines:
        # H1
        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(30, 30, 60)
            text = line[2:].strip()
            pdf.multi_cell(0, 8, text)
            pdf.ln(2)
        # H2
        elif line.startswith("## "):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(50, 50, 120)
            text = line[3:].strip()
            pdf.ln(3)
            pdf.multi_cell(0, 7, text)
            pdf.ln(1)
        # H3
        elif line.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(70, 70, 70)
            text = line[4:].strip()
            pdf.ln(2)
            pdf.multi_cell(0, 6, text)
        # HR
        elif line.startswith("---"):
            pdf.set_draw_color(180, 180, 200)
            pdf.line(20, pdf.get_y() + 2, 190, pdf.get_y() + 2)
            pdf.ln(4)
        # Bullet
        elif line.startswith("- ") or line.startswith("* "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", line[2:].strip())
            text = re.sub(r"_(.+?)_", r"\1", text)
            pdf.multi_cell(0, 5.5, f"  • {text}")
        # Numbered list
        elif re.match(r"^\d+\. ", line):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            text = re.sub(r"^\d+\. ", "", line)
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
            pdf.multi_cell(0, 5.5, f"  {line[:2].strip()} {text}")
        # Blockquote
        elif line.startswith(">"):
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(80, 80, 80)
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", line[1:].strip())
            pdf.multi_cell(0, 5.5, f"    {text}")
        # Bold line
        elif line.startswith("**"):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(40, 40, 40)
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
            text = re.sub(r"_(.+?)_", r"\1", text)
            pdf.multi_cell(0, 5.5, text)
        # Empty line
        elif line.strip() == "":
            pdf.ln(2)
        # Normal paragraph
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
            text = re.sub(r"_(.+?)_", r"\1", text)
            text = re.sub(r"`(.+?)`", r"\1", text)
            pdf.multi_cell(0, 5.5, text)

    return bytes(pdf.output())
