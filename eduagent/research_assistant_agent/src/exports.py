"""Export utilities — Word document and JSON audit trail."""
import io
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional


# ── Word export ───────────────────────────────────────────────────────────────

def export_report_as_docx(
    research_summary: str,
    session_query: str,
    structured_papers: Optional[List[Dict]] = None,
) -> bytes:
    """Convert the markdown research report to a .docx file.

    Returns raw bytes suitable for st.download_button(data=...).
    """
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Title block
    title = doc.add_heading("EDU Deep Research Report", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(f"Query: {session_query}")
    doc.add_paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}")
    doc.add_paragraph("")

    # Report body — parse markdown headings into Word heading styles
    for line in research_summary.split("\n"):
        stripped = line.strip()
        if stripped.startswith("### "):
            doc.add_heading(stripped[4:], level=3)
        elif stripped.startswith("## "):
            doc.add_heading(stripped[3:], level=2)
        elif stripped.startswith("# "):
            doc.add_heading(stripped[2:], level=1)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            doc.add_paragraph(stripped[2:], style="List Bullet")
        elif stripped == "---" or stripped == "___":
            doc.add_paragraph("─" * 60)
        elif stripped:
            # Strip inline markdown bold/italic for plain Word paragraphs
            clean = re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", stripped)
            clean = re.sub(r"_{1,2}(.+?)_{1,2}", r"\1", clean)
            doc.add_paragraph(clean)

    # Data extraction appendix
    if structured_papers:
        doc.add_page_break()
        doc.add_heading("Data Extraction Table", level=1)
        table = doc.add_table(rows=1, cols=5)
        table.style = "Light Grid Accent 1"
        hdr = table.rows[0].cells
        for i, col in enumerate(["Title", "Outcome", "Study Measure", "Finding Direction", "Effect Size"]):
            hdr[i].text = col

        for p in structured_papers:
            row = table.add_row().cells
            row[0].text = p.get("title", "") or ""
            row[1].text = p.get("outcome", "") or ""
            row[2].text = p.get("measure", "") or ""
            row[3].text = p.get("finding_direction", "") or ""
            row[4].text = str(p.get("effect_size", "") or "")

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ── Audit trail export ────────────────────────────────────────────────────────

def export_audit_log_as_json(event_log: List[Dict[str, Any]]) -> str:
    """Serialize the streaming event log to a pretty-printed JSON string."""
    # Strip large metadata payloads to keep file readable; keep type/node/content
    slim_log = [
        {"type": e.get("type"), "node": e.get("node"), "content": e.get("content")}
        for e in event_log
        if e.get("type") not in ("token", "done")  # tokens are too verbose
    ]
    return json.dumps(
        {
            "generated_at": datetime.now().isoformat(),
            "event_count": len(event_log),
            "events": slim_log,
        },
        indent=2,
    )
