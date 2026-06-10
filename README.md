# AI Assistant MVP

## 1. Project Description
This is a clean, production-ready MVP for an AI-driven Lead & Support Assistant. It receives user messages, identifies their intent, classifies their user segment, retrieves context from an internal Vector Knowledge Base (ChromaDB), and generates a smart response. It features a robust 3-tier LLM fallback system and strict error logging.

## 2. Technologies Used
* **Backend:** Python 3.10, FastAPI
* **Database:** SQLite (via SQLAlchemy ORM)
* **Vector DB:** ChromaDB (for semantic search in the Knowledge Base)
* **AI/LLM:** OpenAI API, Ollama (Local), and a custom Mock engine
* **Containerization:** Docker & Docker Compose

## 3. Installation and Execution (Local)
1. Clone the repository and navigate to the folder.
2. Create a virtual environment: `python -m venv venv` and activate it.
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your API keys (optional).
5. Run the server: 
   ```bash
   uvicorn app.main:app --reload