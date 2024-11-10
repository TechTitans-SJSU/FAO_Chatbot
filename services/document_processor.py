from pypdf import PdfReader
from typing import List, Dict
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=200,
            length_function=len,
        )

    # async def process_pdf(self, file) -> List[str]:
    #     """Process PDF file and return chunks of text"""
    #     content = await self._extract_text(file)
    #     chunks = self._split_into_chunks(content)
    #     return chunks

    async def process_pdf(self, file) -> List[Dict[str, str]]:
        """Process single PDF files and prepare them for embedding."""
        documents = []
        text = await self._extract_text(file)
        chunks = self.text_splitter.create_documents([text])

        # Create metadata for each chunk
        for i, chunk in enumerate(chunks):
            documents.append({
                "content": chunk.page_content,
                "metadata": {
                    "source": file.filename,
                    "chunk_id": i
                }
            })
        return documents

    async def _extract_text(self, file) -> str:
        """Extract text from PDF file"""
        # Save uploaded file temporarily
        contents = await file.read()
        with open("temp.pdf", "wb") as f:
            f.write(contents)

        # Extract text from PDF
        reader = PdfReader("temp.pdf")
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Clean up
        import os
        os.remove("temp.pdf")
        
        return self._clean_text(text)

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()

    def _split_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks of approximately equal size"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0

        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1  # +1 for space

            if current_size >= self.chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks