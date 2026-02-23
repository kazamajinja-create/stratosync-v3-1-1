
# pdf_generator.py

from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import json

def generate_pdf_from_json(json_path, output_path="output_agastya_report.pdf"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    for chapter in data.get("chapters", []):
        title = chapter.get("title", "No Title")
        content = chapter.get("content", "No Content")
        story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        story.append(Paragraph(content, styles["BodyText"]))
        story.append(PageBreak())

    doc.build(story)
