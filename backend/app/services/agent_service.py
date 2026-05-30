# backend/app/services/agent_service.py
import os
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from app.services.tools import search_knowledge_base, create_tailored_cv_pdf, search_linkedin_jobs

class AgentManager:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0.1,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.tools = [search_knowledge_base, create_tailored_cv_pdf, search_linkedin_jobs]
        
        # Define the prompt for the agent
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are a professional CV Writer. Your goal is to output a FULL, READY-TO-USE CV.\n\n"
                "STEPS:\n"
                "1. Use 'search_knowledge_base' with doc_type='cv' to retrieve EVERY part of the user's original CV (Contact info, Summary, Work History, Education).\n"
                "2. Use 'search_knowledge_base' with doc_type='jd' to find the job's key requirements.\n"
                "3. RECONSTRUCT the entire CV text. Keep the original sections, but rewrite descriptions to include keywords from the JD.\n"
                "4. MANDATORY: You must pass the FULL text (the complete reconstructed CV) into the 'cv_content' tool. DO NOT summarize. DO NOT say 'Updated content here'. You must provide the actual 500-1000 words of the CV.\n"
                "5. The output PDF must look like a complete resume."
                "RULES FOR CONCLUDING:\n"
                "1. Once you call 'create_tailored_cv_pdf' and receive a SUCCESS message, you MUST STOP calling tools.\n"
                "2. Do not attempt to call the tool again with the same data.\n"
                "3. After a successful tool call, simply provide a friendly closing message to the user: "
                "confirm that the file is ready, explain what you improved, and give interview tips."
            )),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Construct the tool-calling agent
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True, handle_parsing_errors=True)

    def execute(self, user_input: str):
        response = self.agent_executor.invoke({"input": user_input})
        return response.get("output", "The agent processed the request but returned an empty structural layout.")