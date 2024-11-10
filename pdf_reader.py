import fitz  # PyMuPDF for PDF text extraction

class PdfReader:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def read_pdf(self):
        """
        Extracts text from each page of a PDF and returns it as a single string.
        """
        text_content = []
        with fitz.open(self.pdf_path) as pdf:
            for page_num in range(pdf.page_count):
                page = pdf[page_num]
                text_content.append(page.get_text())
        return " ".join(text_content)
