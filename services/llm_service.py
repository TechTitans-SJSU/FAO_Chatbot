from typing import List
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from typing import Dict, Optional
from openai import OpenAI
from openai import AsyncOpenAI
from pydantic import BaseModel 
load_dotenv()

class ChatResponse(BaseModel):
    answer: str
    source: Optional[str] = None

class LLMService:
    
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        """
        Initialize the RAG LLM module.
        
        Args:
            api_key (str): OpenAI API key
            model (str): OpenAI model to use (default: gpt-4-turbo-preview)
        """
        api_key=os.getenv("API_KEY")
        self.model = model
        self.async_client = AsyncOpenAI(api_key=api_key)


    def prepare_context(self, documents: List[Dict], score_threshold: float = 0.8) -> str:
        """
        Prepare context from ChromaDB query results.
        """
        context_parts = []
        
        # Sort documents by relevance score (lower is better in ChromaDB)
        sorted_docs = sorted(documents, key=lambda x: x['relevance_score'])
        
        for doc in sorted_docs:
            if doc['relevance_score'] > score_threshold:
                continue
            
            metadata_str = " | ".join([f"{k}: {v}" for k, v in doc['metadata'].items()])
            context_parts.append(f"[Source: {metadata_str}]\n{doc['content']}\n")
        
        return "\n\n".join(context_parts)
        
    def generate_system_prompt(self, context: str) -> str:
        """
        Generate the system prompt with context information.
        """
        return f"""You are a helpful assistant that answers questions based on the provided context.
        Use ONLY the information from the context to answer questions. If the context doesn't contain
        enough information to answer fully, acknowledge what you don't know.
        When referring to information, cite the source using the metadata provided in square brackets.
        
        Context information:
        {context}
        """
    
    async def generate_response(self, 
                              query: str,
                              documents: List[Dict],
                              temperature: float = 0.7,
                              max_tokens: int = 500,
                              score_threshold: float = 0.8) -> Dict:
        """
        Generate a response using the OpenAI API based on the query and ChromaDB results.
        Returns a ChatResponse object.
        """
        try:
            context = self.prepare_context(documents, score_threshold)
            
            messages = [
                {"role": "system", "content": self.generate_system_prompt(context)},
                {"role": "user", "content": query}
            ]
            
            # print(messages)
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                n=1,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Return a proper ChatResponse even in case of error
            print(f"Error generating response: {str(e)}")
            return ChatResponse(
                answer=f"An error occurred: {str(e)}",
                source=""
            )

