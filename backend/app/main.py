# backend/app/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.core.security import sanitize_input

load_dotenv()

from app.services.rag_service import RAGManager

app = FastAPI(title="AI SecOps Agent")
rag_manager = RAGManager()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Save file temporarily
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    num_chunks = rag_manager.process_document(file_path)
    return {"message": f"Processed {num_chunks} chunks successfully."}

@app.get("/query")
async def query_agent(question: str):
    # 1. Security Check
    if not sanitize_input(question):
        raise HTTPException(status_code=400, detail="Security violation: Malicious prompt detected.")
    
    # 2. Logic (To be expanded with Agent Tool Calling on Day 2)
    return {"response": "RAG pipeline ready. Waiting for Agent Orchestrator."}