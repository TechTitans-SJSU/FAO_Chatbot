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
from services.llm_service import LLMService, ChatResponse
from services.ir_service import IRService

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
ir_service = IRService()
cache_service = RedisCache()
llm_service = LLMService()

class QuestionRequest(BaseModel):
    question: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: QuestionRequest):
    try:
        # Check cache first
        cached_response = await cache_service.get(request.question)
        if cached_response:
            return ChatResponse(answer=cached_response, source="cache")

        # Get relevant context from IR
        context = ir_service.query_documents(request.question)
        # for c in context:
            # print(c)
        # print(context)

        # Generate response using LLM
        response = await llm_service.generate_response(request.question, context)
        # print(response)
        
        # Cache the response
        await cache_service.set(request.question, response)
        
        return ChatResponse(answer=response, source="llm")
    
    except Exception as e:
        print("Error in chat endpoint:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Process PDF and generate embeddings
        content = await doc_processor.process_pdf(file)
        # embedding_service.generate_embeddings(content)
        ir_service.add_document(content)
        return {"message": "PDF processed successfully"}
    
    except Exception as e:
        print("Error in upload endpoint:", e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)