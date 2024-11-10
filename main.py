from pdf_reader import PdfReader
from orchestrator import Orchestrator

# Main execution
if __name__ == "__main__":
    # Step 1: Extract text from PDF files
    pdf_2023_text = PdfReader("SOFI-2023.pdf").read_pdf()
    pdf_2024_text = PdfReader("SOFI-2024.pdf").read_pdf()

    # Step 2: Create an App instance with PDF text
    app = Orchestrator(pdf_2023_text, pdf_2024_text)

    # Step 3: Define a query to test
    # query = "Compare list of Food insecurity reason in 2023 and 2024"

    # # Step 4: Get response based on query and relevant chunks
    # response = app.get_response_with_text(query)
    # print(response)

    query = "Explain quantitative differences in numbers"
    response = app.get_response_with_text(query)
    print(response)