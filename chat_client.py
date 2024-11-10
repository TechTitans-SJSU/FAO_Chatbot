import openai

from dotenv import load_dotenv
import os
import re
from concurrent.futures import ThreadPoolExecutor
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Optional: load the OpenAI API for embeddings if you choose to use them.
USE_EMBEDDINGS = False  # Set to True to use embeddings for retrieval

class ChatClient:
    def create_prompt(self, query, knowledge, year=None):
        """
        Structure the prompt with the user query and relevant information.
        Include the year context if provided.
        """
        year_context = f" for the year {year}" if year else ""
        return f"User's question: {query}\n\nRelevant information{year_context}:\n{knowledge}\n\nAnswer:"

    def get_response_with_embeddings(self, query, knowledge, year=None):
        """
        Generate a response using OpenAI's ChatCompletion API based on the query and knowledge.
        """
        prompt = self.create_prompt(query, knowledge, year)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant that provides information based on the given context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response['choices'][0]['message']['content'].strip()
        except openai.error.InvalidRequestError as e:
            return f"An error occurred: {e}"




