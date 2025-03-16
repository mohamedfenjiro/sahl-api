import io
from pdfminer.high_level import extract_text

def parse_pdf(pdf_bytes: bytes) -> str:
    """
    Converts PDF bytes into a text string.
    """
    pdf_stream = io.BytesIO(pdf_bytes)
    return extract_text(pdf_stream)