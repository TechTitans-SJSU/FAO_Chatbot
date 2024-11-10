import openai
from dotenv import load_dotenv
import os
import re
from concurrent.futures import ThreadPoolExecutor
from sklearn.metrics.pairwise import cosine_similarity

from chat_client import ChatClient

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Optional: load the OpenAI API for embeddings if you choose to use them.
USE_EMBEDDINGS = False  # Set to True to use embeddings for retrieval


class Orchestrator:
    
    def __init__(self, pdf_2023_text, pdf_2024_text):
        self.chunks_2023 = self.split_text_into_chunks(pdf_2023_text)
        self.chunks_2024 = self.split_text_into_chunks(pdf_2024_text)
        self.chat_client = ChatClient()

    def split_text_into_chunks(self, text, max_words=1500):
        """
        Splits the text into smaller chunks based on word count.
        """
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= max_words:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def get_embedding(self, text, model="text-embedding-ada-002"):
        """
        Generates embeddings for a given text using OpenAI's API.
        """
        response = openai.Embedding.create(input=text, model=model)
        return response['data'][0]['embedding']

    def analyze_query(self, query):
        """
        Analyzes the query to dynamically extract keywords based on intent.
        """
        keywords = set(query.lower().split())
        if "reasons" in keywords or "causes" in keywords or "factors" in keywords:
            keywords.update(["reason", "cause", "factor", "contribution", "influence"])
        return keywords

    def find_relevant_chunks(self, query, chunks, top_k=5):
        """
        Finds the most relevant chunks for a query based on dynamic keyword matching and optional embeddings.
        """
        query_keywords = self.analyze_query(query)
        relevance_scores = []
        query_embedding = get_embedding(query) if USE_EMBEDDINGS else None

        for chunk in chunks:
            chunk_text = chunk.lower()
            chunk_words = set(chunk_text.split())
            
            # Score based on keyword overlap
            score = len(query_keywords.intersection(chunk_words))

            # If embeddings are enabled, add similarity score to the relevance
            if USE_EMBEDDINGS and query_embedding is not None:
                chunk_embedding = get_embedding(chunk)
                similarity = cosine_similarity([query_embedding], [chunk_embedding])[0][0]
                score += similarity  # Combine similarity score with keyword score

            relevance_scores.append((chunk, score))

        # Sort chunks by relevance score in descending order and get the top_k
        most_relevant_chunks = sorted(relevance_scores, key=lambda x: x[1], reverse=True)[:top_k]
        return [chunk for chunk, _ in most_relevant_chunks]

    def get_years_from_query(self, query):
        """
        Extracts all years mentioned in the query.
        Returns a list of years found.
        """
        years = re.findall(r'\b(2023|2024)\b', query)
        return list(set(years))  # Remove duplicates

    def get_response_with_text(self, query):
        """
        Determines the appropriate PDF chunks to use based on the query
        and returns a response based on relevant chunks.
        """
        mentioned_years = self.get_years_from_query(query)

        # If comparing years is mentioned in the query
        if "comparing" in query.lower() or "comparison" in query.lower() or len(mentioned_years) > 1:
            relevant_chunks_2023 = self.find_relevant_chunks(query, self.chunks_2023)
            relevant_chunks_2024 = self.find_relevant_chunks(query, self.chunks_2024)
            
            # Generate separate responses for each year
            response_2023 = self.chat_client.get_response_with_embeddings(query, "\n\n".join(relevant_chunks_2023), "2023")
            response_2024 = self.chat_client.get_response_with_embeddings(query, "\n\n".join(relevant_chunks_2024), "2024")
            
            # Combine responses with clear separation
            combined_response = (
                "Comparison between 2023 and 2024 SOFI reports:\n\n"
                f"2023 Report Analysis:\n{response_2023}\n\n"
                f"2024 Report Analysis:\n{response_2024}\n\n"
            )
            return combined_response
        
        # If only one year is mentioned
        elif len(mentioned_years) == 1:
            year = mentioned_years[0]
            chunks = self.chunks_2023 if year == "2023" else self.chunks_2024
            relevant_chunks = self.find_relevant_chunks(query, chunks)
            response = self.chat_client.get_response_with_embeddings(query, "\n\n".join(relevant_chunks), year)
            return f"Response based on SOFI {year} PDF:\n{response}"
        
        # If no specific year is mentioned
        else:
            # Use both years' data but focus on the most recent information
            relevant_chunks_2024 = self.find_relevant_chunks(query, self.chunks_2024)
            response = self.chat_client.get_response_with_embeddings(query, "\n\n".join(relevant_chunks_2024))
            return f"Response based on most recent SOFI 2024 PDF:\n{response}"
    


