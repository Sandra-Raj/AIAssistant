# backend/app/services/rag_service.py
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
from pathlib import Path

# 1. Get the absolute path of THIS file
# 2. Go up: services -> app -> backend
# .parent.parent.parent is the cleanest way using pathlib

# This gets the 'backend' folder path accurately
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = str(BACKEND_DIR / "data" / "chroma")

class RAGManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        # Initialize vector_store as None; we'll load/create it in process_document
        self.vector_store = None
        
    def process_document(self, file_path: str, doc_type: str):
        # Load based on extension
        loader = PyPDFLoader(file_path) if file_path.endswith(".pdf") else TextLoader(file_path)
        docs = loader.load()
        
        # Add metadata to each page/document
        for doc in docs:
            doc.metadata["doc_type"] = doc_type
            doc.metadata["source"] = os.path.basename(file_path)

        # Chunking
        chunks = self.text_splitter.split_documents(docs)
        
        # Persist to ChromaDB
        if os.path.exists(DB_DIR) and os.listdir(DB_DIR):
            self.vector_store = Chroma(
                embedding_function=self.embeddings,
                persist_directory=DB_DIR
            )
            self.vector_store.add_documents(chunks)
        else:
            self.vector_store = Chroma.from_documents(documents=chunks, embedding=self.embeddings, persist_directory=DB_DIR)
        
        print(f"--- SUCCESS: Vector DB updated at {DB_DIR} ---")
        # Optional: Clean up the temp file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

        return len(chunks)