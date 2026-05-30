# backend/app/services/query_service.py
import os
from langchain_groq import ChatGroq  # New Import
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from app.services.rag_service import DB_DIR

class QueryManager:
    def __init__(self):
        # Local embeddings (Free)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        # Load your existing Vector DB
        self.vector_store = Chroma(
            persist_directory=DB_DIR, 
            embedding_function=self.embeddings
        )
        
        # Swapping OpenAI for Groq (Free & Fast)
        # Llama-3.1-70b is excellent for complex reasoning
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def get_answer(self, question: str):
        system_prompt = (
            "You are an expert Security Operations (SecOps) assistant. "
            "Use the provided context to answer the user's question accurately. "
            "If the answer isn't in the context, say you don't know. "
            "\n\n"
            "Context: {context}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        # Create the modern RAG chain
        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        rag_chain = create_retrieval_chain(self.vector_store.as_retriever(), question_answer_chain)

        response = rag_chain.invoke({"input": question})
        return response["answer"]