import os
import re
from docx import Document
from neo4j import GraphDatabase
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Setup Neo4j driver
# Replace 'your_password' with your actual Neo4j password
NEO4J_PASSWORD = 'diya@1307'
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", NEO4J_PASSWORD))

# Predefined skill list (expand as needed)
SKILL_LIST = [
    "Python", "Java", "C++", "SQL", "Excel", "Project Management", "Data Analysis",
    "Machine Learning", "Communication", "Leadership", "AWS", "Azure", "JavaScript",
    "HTML", "CSS", "Django", "Flask", "React", "Node.js", "Tableau", "Power BI"
]

# Function to extract text from a DOCX file
def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

# Enhanced extraction using spaCy and skills
def extract_candidate_info(text):
    doc = nlp(text)
    # Name extraction (first PERSON entity)
    name = None
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break
    # Phone (10+ digits)
    phone = re.search(r"\b\d{10,}\b", text)
    # Email
    email = re.search(r"\S+@\S+", text)
    # Age (e.g., 32 years)
    age = re.search(r"(\d{2})\s*years", text.lower())
    # Skills (from SKILL_LIST)
    skills = [skill for skill in SKILL_LIST if skill.lower() in text.lower()]
    return {
        "name": name,
        "phone": phone.group() if phone else None,
        "email": email.group() if email else None,
        "age": int(age.group(1)) if age else None,
        "skills": skills
    }

# Cypher insert (with skills as a list)
def insert_candidate(tx, name, phone, email, age, skills):
    tx.run("""
        CREATE (c:Candidate {
            name: $name,
            phone: $phone,
            email: $email,
            age: $age,
            skills: $skills
        })
    """, name=name, phone=phone, email=email, age=age, skills=skills)

# ParserAgent: Parse and store all resumes
def parse_and_store_all(folder):
    for filename in os.listdir(folder):
        if filename.endswith(".docx"):
            filepath = os.path.join(folder, filename)
            text = extract_text_from_docx(filepath)
            info = extract_candidate_info(text)
            print(f"Inserting: {info}")  # Debug print
            with driver.session() as session:
                session.write_transaction(
                    insert_candidate,
                    info['name'],
                    info['phone'],
                    info['email'],
                    info['age'],
                    info['skills']
                )

# QueryAgent: Map NL query to Cypher and run it
def query_agent(nl_query):
    q = nl_query.lower()
    cypher = None
    if "contact number" in q or "phone" in q:
        cypher = "MATCH (c:Candidate) RETURN c.name AS name, c.phone AS phone"
    elif "age above" in q:
        age = int(re.findall(r"age above (\d+)", q)[0])
        cypher = f"MATCH (c:Candidate) WHERE c.age > {age} RETURN c.name AS name, c.age AS age"
    elif "skill" in q:
        # e.g., "Show all candidates with skill Python"
        skill_match = re.search(r"skill (\w+)", q)
        if skill_match:
            skill = skill_match.group(1)
            cypher = f"MATCH (c:Candidate) WHERE '{skill}' IN c.skills RETURN c.name AS name, c.skills AS skills"
    elif "all candidates" in q:
        cypher = "MATCH (c:Candidate) RETURN c"
    else:
        print("Query not supported.")
        return []
    with driver.session() as session:
        result = session.run(cypher)
        return [record.data() for record in result]

# DisplayAgent: Format and print results
def display_agent(results):
    if not results:
        print("No results found.")
        return
    for record in results:
        print("-" * 40)
        # Handle both {'c': {...}} and flat dicts
        candidate = record.get('c', record)
        for field in ['name', 'age', 'email', 'phone', 'skills']:
            value = candidate.get(field)
            if value:
                if field == 'skills' and isinstance(value, list):
                    print(f"{field.capitalize()}: {', '.join(value)}")
                else:
                    print(f"{field.capitalize()}: {value}")
    print("-" * 40)

# Main integration loop
if __name__ == "__main__":
    print("1. Parsing resumes and populating Neo4j...")
    parse_and_store_all(os.path.join(os.path.dirname(__file__), "../resume_database"))
    print("Done populating database.\n")
    print("2. You can now enter natural language queries (type 'exit' to quit):")
    while True:
        nl_query = input("Query> ")
        if nl_query.strip().lower() == 'exit':
            break
        results = query_agent(nl_query)
        display_agent(results)
    driver.close()