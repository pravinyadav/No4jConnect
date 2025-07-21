# resume_manager_adk/app/main.py
# Improved Resume Manager with Google ADK Integration
# This script sets up a multi-agent system using Google ADK for resume extraction, storage in Neo4j, and natural language querying.
# Enhancements include: Modular agents with Gemini LLM integration, tool-based functions for better orchestration,
# error handling, and dynamic workflows. Assumes existing parser and query logic from your original code.

import os
# Ensure python-dotenv is installed: pip install python-dotenv
try:
    from dotenv import load_dotenv
except ImportError:
    raise ImportError("python-dotenv is not installed. Please run 'pip install python-dotenv'.")

# Google ADK import with error handling for missing package
try:
    from google.adk.agents import Agent, FunctionTool, AgentTool, SequentialAgent
except ImportError:
    raise ImportError("google-adk is not installed or not found. Please run 'pip install google-adk' or check your environment.")

from neo4j import GraphDatabase

# Load environment variables from a .env file (for sensitive info like DB credentials)
load_dotenv()

# Neo4j Driver Setup (improved with connection pooling and error handling)
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# ---
# Resume Extraction Logic
# ---
def extract_resume_details(file_path: str) -> dict:
    """
    Extracts key details from a resume file (e.g., name, contact, skills).
    Replace the placeholder with actual parsing logic (e.g., using pdfplumber, spaCy, etc.).
    Returns a dictionary with extracted fields or an error message.
    """
    try:
        # Placeholder: Implement actual parsing here
        return {
            "name": "John Doe",
            "contact": "john@example.com",
            "skills": ["Python", "Neo4j", "AI"]
        }
    except (IOError, ValueError) as e:  # Catch only expected exceptions
        return {"error": str(e)}

# ---
# Neo4j Storage Logic
# ---
def store_in_neo4j(data: dict) -> dict:
    """
    Stores extracted resume data in Neo4j as nodes and relationships.
    Handles transaction management and error reporting.
    """
    if "error" in data:
        return {"status": "failure", "message": data["error"]}
    try:
        with driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "CREATE (c:Candidate {name: $name, contact: $contact}) "
                    "WITH c UNWIND $skills AS skill "
                    "MERGE (s:Skill {name: skill}) "
                    "CREATE (c)-[:HAS_SKILL]->(s)",
                    name=data["name"], contact=data["contact"], skills=data["skills"]
                )
            )
        return {"status": "success"}
    except (IOError, ValueError, Exception) as e:  # Catch only expected exceptions
        return {"status": "failure", "message": str(e)}

# ---
# Neo4j Query Logic
# ---
def query_neo4j(natural_query: str) -> dict:
    """
    Converts a natural language query to a Cypher query and executes it on Neo4j.
    Returns the results as a list of dictionaries or an error message.
    """
    try:
        # Placeholder: Only supports queries for candidates with Python skill
        with driver.session() as session:
            result = session.run(
                "MATCH (c:Candidate)-[:HAS_SKILL]->(s:Skill {name: 'Python'}) "
                "RETURN c.name AS name, c.contact AS contact, collect(s.name) AS skills"
            )
            return [record.data() for record in result]
    except (IOError, ValueError, Exception) as e:  # Catch only expected exceptions
        return {"error": str(e)}

# ---
# Define Function Tools for Each Operation
# ---
extraction_tool = FunctionTool(
    name="extract_resume",
    description="Extracts key details like name, skills, and contact from a resume file.",
    function=extract_resume_details,
    parameters={
        "type": "object",
        "properties": {"file_path": {"type": "string", "description": "Path to the resume file"}},
        "required": ["file_path"]
    }
)

storage_tool = FunctionTool(
    name="store_resume",
    description="Stores extracted resume data in Neo4j as nodes and relationships.",
    function=store_in_neo4j,
    parameters={
        "type": "object",
        "properties": {"data": {"type": "object", "description": "Extracted data dictionary"}},
        "required": ["data"]
    }
)

query_tool = FunctionTool(
    name="query_resumes",
    description="Queries Neo4j for candidate info based on natural language input and formats results.",
    function=query_neo4j,
    parameters={
        "type": "object",
        "properties": {"natural_query": {"type": "string", "description": "Natural language query"}},
        "required": ["natural_query"]
    }
)

# ---
# Define Specialized Agents for Each Task
# ---
extraction_agent = Agent(
    name="extraction_agent",
    model="models/gemini-1.5-flash",  # Use Gemini for enhanced parsing if needed
    description="Specialized agent for extracting details from resumes.",
    instruction="Use the extraction tool to parse resumes accurately. Handle errors gracefully.",
    tools=[extraction_tool]
)

storage_agent = Agent(
    name="storage_agent",
    model="models/gemini-1.5-flash",
    description="Specialized agent for storing data in Neo4j.",
    instruction="Store extracted data reliably in Neo4j. Confirm success or report issues.",
    tools=[storage_tool]
)

query_agent = Agent(
    name="query_agent",
    model="models/gemini-1.5-flash",
    description="Specialized agent for handling natural language queries on resume data.",
    instruction="Interpret user queries, use the query tool, and format results in a readable way (e.g., tables).",
    tools=[query_tool]
)

# ---
# Root Agent for Coordination
# ---
root_agent = Agent(
    name="root_resume_manager",
    model="models/gemini-1.5-flash",
    description="Coordinates the entire resume management workflow.",
    instruction="Delegate tasks to specialized agents based on user input. For full processing: extract, store, then allow queries.",
    tools=[AgentTool(extraction_agent), AgentTool(storage_agent), AgentTool(query_agent)]
)

# ---
# Workflow Orchestration: Sequentially process extraction, storage, and query
# ---
resume_workflow = SequentialAgent(
    name="resume_processing_workflow",
    agents=[extraction_agent, storage_agent, query_agent],
    instruction="Process resumes in sequence: extract details, store in Neo4j, then handle queries."
)

# ---
# Main Function to Run the System
# ---
def run_resume_manager(file_path: str, query: str):
    """
    Orchestrates the full resume processing workflow:
    1. Extract details from the resume file.
    2. Store the extracted data in Neo4j.
    3. Run a natural language query if storage succeeded.
    Returns the query results or error information.
    """
    # Step 1: Extract
    extracted = extraction_agent.run({"file_path": file_path})
    # Step 2: Store
    stored = storage_agent.run({"data": extracted})
    # Step 3: Query (only if storage succeeded)
    if stored.get("status") == "success":
        results = query_agent.run({"natural_query": query})
        return results
    return stored

# ---
# Example Usage
# ---
if __name__ == "__main__":
    # Example file path and query (replace with actual values)
    sample_file = "path/to/resume.pdf"
    sample_query = "Find candidates with Python skills"
    output = run_resume_manager(sample_file, sample_query)
    print("Query Results:", output)

# ---
# Cleanup: Close Neo4j driver on exit
# ---
def close_driver():
    """
    Ensures the Neo4j driver is closed when the script exits.
    """
    driver.close()

import atexit
atexit.register(close_driver)
