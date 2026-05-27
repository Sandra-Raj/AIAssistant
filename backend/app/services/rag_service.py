# backend/app/services/rag_service.py
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

class RAGManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )

    def process_document(self, file_path: str):
        # Load based on extension
        loader = PyPDFLoader(file_path) if file_path.endswith(".pdf") else TextLoader(file_path)
        docs = loader.load()
        
        # Chunking
        chunks = self.text_splitter.split_documents(docs)
        
        # Persist to ChromaDB
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory="./backend/data/chroma"
        )

        # Optional: Clean up the temp file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

        return len(chunks)