from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from services.document_processor import DocumentProcessor
from typing import List

# Import custom modules
from services.document_processor import DocumentProcessor
from services.embedding_service import EmbeddingService
from services.cache_service import RedisCache
from services.llm_service import LLMService

# Load environment variables
load_dotenv()

app = FastAPI(title="PDF Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
doc_processor = DocumentProcessor()
embedding_service = EmbeddingService()
cache_service = RedisCache()
llm_service = LLMService()

class QuestionRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    source: Optional[str] = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: QuestionRequest):
    try:
        # Check cache first
        cached_response = await cache_service.get(request.question)
        if cached_response:
            return ChatResponse(answer=cached_response, source="cache")

        # Get relevant context from embeddings
        context = embedding_service.search_similar_chunks(request.question)
        
        # Generate response using LLM
        response = await llm_service.generate_response(request.question, context)
        
        # Cache the response
        await cache_service.set(request.question, response)
        
        return ChatResponse(answer=response, source="llm")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Process PDF and generate embeddings
        content = await doc_processor.process_pdf(file)
        embedding_service.generate_embeddings(content)
        return {"message": "PDF processed successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)