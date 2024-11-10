from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict
import logging

class IRService:
    def __init__(self, persist_directory: str = "./chroma_db", batch_size: int = 128, collection_name="SOFI_Pdf_Collection"):
        """Initialize the IR system with necessary components."""
        # Use ChromaDB's default embedding function
        self.embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.batch_size = batch_size
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize or load existing database
        self._initialize_vector_store()

    def _initialize_vector_store(self) -> None:
        """Initialize vector store, loading existing if present"""
        try:
            self.logger.info("Initializing new Chroma DB")
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            # Get or create collection with the embedding function
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embeddings
            )
        except Exception as e:
            self.logger.error(f"Error initializing vector store: {str(e)}")
            raise

    def add_document(self, documents: List[Dict[str, str]]) -> None:
        """Add documents to the collection in batches"""
        try:
            texts = [doc["content"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            # Generate unique IDs for documents
            ids = [f"doc_{i}" for i in range(len(texts))]

            total_docs = len(texts)
            for i in range(0, total_docs, self.batch_size):
                end_idx = min(i + self.batch_size, total_docs)
                batch_texts = texts[i:end_idx]
                batch_metadatas = metadatas[i:end_idx] if metadatas else None
                batch_ids = ids[i:end_idx]

                self.logger.info(f"Processing batch {i//self.batch_size + 1}: documents {i} to {end_idx}")
                # Use ChromaDB's native add method
                self.collection.add(
                    documents=batch_texts,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                
        except Exception as e:
            self.logger.error(f"Error adding documents: {str(e)}")
            raise

    def query_documents(self, query: str, k: int = 50) -> List[Dict]:
        """Query the collection and return relevant documents with similarity scores"""
        try:
            if not self.collection:
                raise ValueError("Collection has not been initialized. Please create it first.")

            # Use ChromaDB's native query method
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )

            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    # Convert L2 distance to similarity score (0-1 range)
                    distance = results['distances'][0][i]
                    similarity_score = 1 / (1 + distance)  # Alternative similarity conversion

                    formatted_results.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "relevance_score": float(similarity_score)
                    })

            # Sort by relevance score in descending order
            formatted_results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return formatted_results

        except Exception as e:
            self.logger.error(f"Error querying documents: {str(e)}")
            raise

    def _get_collection_stats(self) -> Dict:
        """Get statistics about the current collection"""
        if not self.collection:
            return {"document_count": 0, "status": "No collection initialized"}

        try:
            count = self.collection.count()
            return {
                "document_count": count,
                "status": "active",
                "collection_name": self.collection_name
            }
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {str(e)}")
            return {"error": str(e)}