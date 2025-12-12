import requests
import io
from pypdf import PdfWriter, PdfReader

def create_dummy_pdf(text_content):
    # pypdf doesn't easily Create text-based PDFs from scratch (it's mostly for manipulation), 
    # but we can try to use reportlab if available, or just skip and hope the user has a pdf.
    # actually, for the sake of this test, let's assume we can upload a text file masquerading as PDF 
    # IF we mocked the extractor, but we are using real extractor.
    
    # We will try to import reportlab, if not present we fail gracefully or try another way.
    try:
        from reportlab.pdfgen import canvas
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, text_content)
        p.save()
        buffer.seek(0)
        return buffer
    except ImportError:
        print("Reportlab not found. Please install reportlab to generate dummy PDF or provide a path.")
        return None

def main():
    # 1. content
    text = "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize nutrients from carbon dioxide and water."
    
    # Try to generate
    pdf_file = create_dummy_pdf(text)
    if not pdf_file:
        # Fallback: create a dummy file that might fail extraction but test the endpoint reachability
        # OR just install reportlab. 
        # let's try to install reportlab in the script execution or just assume successful pypdf install implies we can do something.
        # Actually pypdf can't write text easily.
        # We will terminate early.
        print("Skipping PDF generation test - reportlab missing.")
        return

    url = "http://127.0.0.1:8000/generate/pdf"
    
    files = {
        'file': ('test.pdf', pdf_file, 'application/pdf')
    }
    data = {
        'subject': 'Science',
        'grade': '10',
        'medium': 'English',
        'chapter_id': 'ch01',
        'chapter_name': 'Photosynthesis'
    }
    
    print(f"Uploading PDF to {url}...")
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response JSON:")
            print(response.json())
        else:
            print("Error Response:")
            print(response.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()
