"""PDF text extraction for supplementary studies."""
import io
from pypdf import PdfReader


def extract_text_from_bytes(file_bytes: bytes) -> str:
    """Extract plain text from a PDF given its raw bytes."""
    reader = PdfReader(io.BytesIO(file_bytes))
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(texts)
