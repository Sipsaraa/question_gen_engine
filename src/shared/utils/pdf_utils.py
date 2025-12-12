from pypdf import PdfReader
from io import BytesIO

def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extracts all text from a PDF file content.
    """
    try:
        reader = PdfReader(BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
