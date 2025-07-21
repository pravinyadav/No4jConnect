# Resume Manager with Google ADK & Neo4j

## Overview
This project is a modular, agent-based system for extracting information from resumes, storing it in a Neo4j graph database, and enabling natural language queries. It leverages Google ADK for agent orchestration, Gemini LLM for enhanced parsing and reasoning, and is designed for extensibility and robustness.

---

## Features
- **Multi-Agent Architecture:** Specialized agents for extraction, storage, and querying.
- **Google ADK Integration:** Uses FunctionTool, AgentTool, and SequentialAgent for modular workflows.
- **Gemini LLM:** Powers intelligent extraction and query interpretation.
- **Neo4j Graph Database:** Stores candidates and their skills as nodes and relationships.
- **Natural Language Querying:** Supports user-friendly queries for candidate search.
- **Error Handling:** Robust error reporting and transaction management.

---

## Setup Instructions

### Prerequisites
- Python 3.8+
- Neo4j (running locally or remotely)
- Google ADK Python SDK
- Required Python packages:
  - `python-dotenv`
  - `neo4j`
  - `google-adk` (or your custom ADK package)

### Installation
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd No4jConnect
   ```
2. **Install dependencies:**
   ```bash
   pip install python-dotenv neo4j google-adk
   ```
3. **Set up Neo4j:**
   - Install and start Neo4j (https://neo4j.com/download/)
   - Create a `.env` file in the project root with:
     ```env
     NEO4J_URI=bolt://localhost:7687
     NEO4J_USERNAME=neo4j
     NEO4J_PASSWORD=your_password
     ```
4. **Prepare resumes:**
   - Place your resume files in a known location for testing (update the file path in the example usage).

---

## Usage
1. **Run the script:**
   ```bash
   python main.py
   ```
2. **The script will:**
   - Extract details from the specified resume file.
   - Store the extracted data in Neo4j.
   - Run a natural language query and display the results.
3. **Example usage in code:**
   ```python
   output = run_resume_manager("path/to/resume.pdf", "Find candidates with Python skills")
   print("Query Results:", output)
   ```

---

## Code Structure and Detailed Explanation

### 1. Environment and Database Setup
- Loads environment variables from `.env` for secure credential management.
- Connects to Neo4j using the official driver with connection pooling.

### 2. Extraction Logic
- `extract_resume_details(file_path)`: Extracts name, contact, and skills from a resume file. (Replace the placeholder with your actual parsing logic.)

### 3. Storage Logic
- `store_in_neo4j(data)`: Stores candidate and skills in Neo4j as nodes and relationships. Handles errors and transaction management.

### 4. Query Logic
- `query_neo4j(natural_query)`: Converts a natural language query to Cypher and executes it. (Currently supports queries for candidates with Python skill; extend as needed.)

### 5. Tool Definitions
- **FunctionTool:** Wraps each core function (extraction, storage, query) for agent use, with parameter validation and descriptions.

### 6. Agent Definitions
- **extraction_agent:** Uses Gemini LLM for parsing resumes.
- **storage_agent:** Handles storing data in Neo4j.
- **query_agent:** Interprets and executes user queries.
- **root_agent:** Delegates tasks to specialized agents.

### 7. Workflow Orchestration
- **SequentialAgent:** Chains extraction, storage, and query agents for end-to-end processing.

### 8. Main Function
- `run_resume_manager(file_path, query)`: Orchestrates the workflow: extract → store → query. Returns results or error info.

### 9. Cleanup
- Ensures the Neo4j driver is closed on exit using `atexit`.

---

## Example Workflow
1. Place a resume file at your chosen path.
2. Run `python main.py`.
3. The script will extract, store, and query as per the example usage.
4. View the results in the terminal.

---

## Extending the Project
- **Improve Extraction:** Replace the placeholder in `extract_resume_details` with advanced parsing (e.g., spaCy, pdfplumber).
- **Support More Query Types:** Enhance `query_neo4j` to map more natural language queries to Cypher.
- **Add More Agents:** For tasks like resume ranking, feedback, or analytics.

---

## Troubleshooting
- **Neo4j Connection Errors:** Ensure Neo4j is running and credentials are correct in `.env`.
- **No Results Found:** Check that the resume file path is correct and the extraction logic is implemented.
- **Missing Packages:** Install all required dependencies as listed above.

---

## License
This project is for educational and demonstration purposes. Adapt and extend as needed for your use case. 