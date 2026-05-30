# backend/app/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from app.core.security import sanitize_input
from app.services.agent_service import AgentManager
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
from app.services.query_service import QueryManager
from app.services.rag_service import RAGManager

app = FastAPI(title="AI SecOps Agent")
rag_manager = RAGManager()
# Initialize QueryManager (this loads the Vector DB)
query_manager = QueryManager()
agent_manager = AgentManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/agent")
async def run_agent(question: str):
    if not sanitize_input(question):
        raise HTTPException(status_code=400, detail="Security violation.")
    
    try:
        response = agent_manager.execute(question)
        
        return {"response": response}
    except Exception as e:
        print(f"Backend Executor Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), doc_type: str = Form(...)):
    # doc_type will be 'cv' or 'jd'
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # We pass doc_type into the manager
    num_chunks = rag_manager.process_document(file_path, doc_type)
    return {"message": f"Successfully indexed {file.filename} as {doc_type.upper()}.",
        "chunks": num_chunks}

@app.get("/query")
async def query_agent(question: str):
    # 1. Security Check
    if not sanitize_input(question):
        raise HTTPException(status_code=400, detail="Security violation: Malicious prompt detected.")
    
    # 2. Get Answer from RAG
    try:
        answer = query_manager.get_answer(question)
        return {
            "question": question,
            "answer": answer,
            "source": "internal_knowledge_base"
        }
    except Exception as e:
        # Check for the 429 error specifically
        if "insufficient_quota" in str(e):
            return {"error": "OpenAI API quota exceeded. Please check billing or use a local LLM."}
        raise HTTPException(status_code=500, detail=str(e))