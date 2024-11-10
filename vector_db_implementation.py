from transformers import AutoTokenizer, AutoModel
import torch
import PyPDF2
import chromadb

def extract_text(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def chunk_text(text, chunk_size=512):
    # Split text into smaller chunks
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def generate_embeddings(chunks, model_name="bert-base-uncased"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    
    embeddings = []
    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors="pt", padding=True, truncation=True)
        outputs = model(**inputs)
        embeddings.append(outputs.last_hidden_state.mean(dim=1))
    
    return embeddings

def store_in_vectordb(chunks, embeddings, collection):
    # Convert embeddings to list format
    embeddings_list = [e.detach().numpy().flatten().tolist() for e in embeddings]
    
    # Generate IDs for each chunk
    ids = [str(i) for i in range(len(chunks))]
    
    # Add to ChromaDB collection
    collection.add(
        embeddings=embeddings_list,
        documents=chunks,
        ids=ids
    )

def query_similar(query_text, collection):
    # Generate embedding for query
    query_embedding = generate_embeddings([query_text])[0]
    
    # Search in collection
    results = collection.query(
        query_embeddings=[query_embedding.detach().numpy().flatten().tolist()],
        n_results=3
    )
    return results

# Test extraction
text = extract_text("SOFI-2024.pdf")
print(f"Extracted text length: {len(text)}")

# Test chunking
chunks = chunk_text(text)
print(f"Number of chunks: {len(chunks)}")

# Test embedding generation
embeddings = generate_embeddings(chunks[:2])  # Test with just 2 chunks
print(f"Embedding shape: {embeddings[0].shape}")

# Initialize ChromaDB
chroma_client = chromadb.Client()
collection = chroma_client.create_collection("pdf_embeddings")
# Test vector storage
store_in_vectordb(chunks[:2], embeddings, collection)