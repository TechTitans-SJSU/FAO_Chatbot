# services/document_processor.py
from pypdf import PdfReader
from typing import List
import re

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size

    async def process_pdf(self, file) -> List[str]:
        """Process PDF file and return chunks of text"""
        content = await self._extract_text(file)
        chunks = self._split_into_chunks(content)
        return chunks

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