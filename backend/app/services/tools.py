# backend/app/services/tools.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.tools import tool
import os
from tavily import TavilyClient
from pathlib import Path
import json
from fpdf import FPDF

# Ensure these are distinct Path objects
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = BACKEND_DIR / "reports"
DB_DIR = str(BACKEND_DIR / "data" / "chroma")

# Create the reports folder safely if it doesn't exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

@tool
def create_tailored_cv_pdf(cv_content: str, filename: str = "tailored_cv.pdf") -> str:
    """
    Creates a PDF file from the provided CV text.
    Use this once the CV has been rewritten to match a job description.
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=11) # Helvetica handles formatting bugs better
        
        # Clean the string to avoid encoding crashes with special bullet points
        clean_text = str(cv_content).encode('latin-1', 'replace').decode('latin-1')
        
        # Write text to PDF
        pdf.multi_cell(0, 6, txt=clean_text, align='L')
        
        # Clean Path joining
        file_path = REPORTS_DIR / filename
        pdf.output(str(file_path))
        
        # We add a clear 'Instruction' inside the return string
        return (f"FINAL RESULT: The PDF has been successfully written to {file_path}. "
                "Task complete. Please summarize the improvements for the user.")
    except Exception as e:
        return f"ERROR generating PDF: {str(e)}"

@tool
def search_linkedin_jobs(query: str):
    """
    Searches for current job openings on LinkedIn. 
    Query should include the job title and location.
    """
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    # We force the search to focus on LinkedIn job postings
    search_query = f"{query} site:linkedin.com/jobs"
    results = tavily.search(search_query, search_depth="advanced")
    
    return results['results']

@tool
def search_knowledge_base(query: str, doc_type: str = None) -> str:
    """
    Look up information from the user's uploaded CV, documents, or job descriptions.
    Use this to find specific skills, experiences, or project details.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    
    # If the AI specifies a doc_type, we filter the results!
    search_kwargs = {}
    if doc_type:
        search_kwargs["filter"] = {"doc_type": doc_type}
        
    # Retrieve top 4 relevant chunks
    docs = vector_store.similarity_search(query, k=5, **search_kwargs)
    return "\n---\n".join([d.page_content for d in docs])

# @tool
# def generate_security_report(analysis_summary: str):
#     """
#     Use this tool to format a formal Security Analysis Report.
#     Input should be a string summary of the findings.
#     """
#     # In a real app, this could save a PDF or send an email.
#     # For now, it returns a structured JSON string.
#     report_data = {
#         "report_type": "Internal Security Assessment",
#         "status": "Final",
#         "summary": analysis_summary,
#         "recommendation": "Review credentials and project history for role fit."
#     }
#     # Save the file physically
#     file_path = REPORTS_DIR / "latest_security_report.json"
#     with open(file_path, "w") as f:
#         json.dump(report_data, f, indent=4)
    
#     # Returning this string tells the LLM the job is DONE
#     return f"SUCCESS: Report has been saved to {file_path}. Do not call this tool again for the same request."

# @tool
# def calculate_risk_score(experience_years: int):
#     """
#     Calculates a mock risk score based on years of experience.
#     """
#     score = "Low" if experience_years > 5 else "Medium"
#     return f"The calculated risk score is: {score}"