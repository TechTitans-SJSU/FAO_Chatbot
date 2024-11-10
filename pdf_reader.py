import PyPDF2

class PdfReader:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def read_pdf(self):
        """
        Extracts text from each page of a PDF and returns it as a single string.
        """
        with open(self.pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
