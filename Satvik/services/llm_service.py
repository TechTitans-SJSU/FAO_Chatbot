from typing import List
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo",
            api_key=os.getenv(API KEY)
        )
        
        self.prompt_template = ChatPromptTemplate.from_template(
            """You are a helpful assistant that answers questions based only on the provided context. 
            If the answer cannot be found in the context, say "I cannot answer this question based on the provided information."
            
            Context: {context}
            
            Question: {question}
            
            Answer: """
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    async def generate_response(self, question: str, context: List[str]) -> str:
        try:
            # Combine context chunks into a single string
            combined_context = " ".join(context)
            
            # Generate response
            response = await self.chain.arun(
                context=combined_context,
                question=question
            )
            
            return response.strip()
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error while processing your question."
