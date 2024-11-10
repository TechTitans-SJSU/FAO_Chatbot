from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb
import os
from typing import List, Dict
from pdf_reader import PdfReader
import logging


class IRSearchManager:
    def __init__(self, persist_directory: str = "./chroma_db", batch_size: int = 128, collection_name="SOFI_Pdf_Collection"):
        """Initialize the IR system with necessary components."""
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
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
        """
        Initialize vector store, loading existing if present
        """
        try:
            # Check if directory exists and contains data
            if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
                self.logger.info(f"Loading existing Chroma DB from {self.persist_directory}")
                self.client = chromadb.PersistentClient(path=self.persist_directory)

                # Check if collection exists
                try:
                    self.client.get_collection(self.collection_name)
                    self.vector_store = Chroma(
                        client=self.client,
                        collection_name=self.collection_name,
                        embedding_function=self.embeddings
                    )
                    collection_stats = self._get_collection_stats()
                    self.logger.info(f"Loaded existing collection with {collection_stats['document_count']} documents")
                except ValueError:
                    self.logger.info(f"No existing collection found with name {self.collection_name}")
                    self.vector_store = None
            else:
                self.logger.info("Initializing new Chroma DB")
                self.client = chromadb.PersistentClient(path=self.persist_directory)
                self.vector_store = Chroma(
                    client=self.client,
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings
                )

                # Create and persist vector store
                pdf_paths = ["SOFI-2023.pdf", "SOFI-2024.pdf"]
                documents = self._process_pdfs(pdf_paths)
                self._create_vector_store(documents)

        except Exception as e:
            self.logger.error(f"Error initializing vector store: {str(e)}")
            raise


    def _get_collection_stats(self) -> Dict:
        """
        Get statistics about the current collection
        """
        if self.vector_store is None:
            return {"document_count": 0, "status": "No collection initialized"}

        try:
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()
            return {
                "document_count": count,
                "status": "active",
                "collection_name": self.collection_name
            }
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {str(e)}")
            return {"error": str(e)}


    def _process_pdfs(self, pdf_paths: List[str]) -> List[Dict[str, str]]:
        """Process multiple PDF files and prepare them for embedding."""
        documents = []
        for pdf_path in pdf_paths:
            text = PdfReader(pdf_path).read_pdf()
            chunks = self.text_splitter.create_documents([text])

            # Create metadata for each chunk
            for i, chunk in enumerate(chunks):
                documents.append({
                    "content": chunk.page_content,
                    "metadata": {
                        "source": pdf_path,
                        "chunk_id": i
                    }
                })
        return documents

    def _create_vector_store(self, documents: List[Dict[str, str]], persist_directory: str = "chroma_db"):
        """Create and persist the vector store with document embeddings."""
        texts = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]

        total_docs = len(texts)
        for i in range(0, total_docs, self.batch_size):
            end_idx = min(i + self.batch_size, total_docs)
            batch_texts = texts[i:end_idx]
            batch_metadatas = metadatas[i:end_idx] if metadatas else None

            self.logger.info(f"Processing batch {i//self.batch_size + 1}: documents {i} to {end_idx}")

            self.vector_store.add_texts(
                    texts=batch_texts,
                    metadatas=batch_metadatas
                )

        return self.vector_store

    def query_documents(self, query: str, k: int = 3) -> List[Dict]:
        """Query the vector store and return relevant documents."""
        if not self.vector_store:
            raise ValueError("Vector store has not been initialized. Please create it first.")

        results = self.vector_store.similarity_search_with_score(query, k=k)

        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": score
            })

        return formatted_results

