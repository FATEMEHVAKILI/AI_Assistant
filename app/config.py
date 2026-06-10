import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///./ai_assistant.db")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LLM_PROVIDER: str = os.getenv(
        "LLM_PROVIDER", "auto")  # auto, api, local, mock
    CHROMA_DIR: str = os.getenv("CHROMA_DIR", "./chroma_db")
    KB_DIR: str = os.getenv("KB_DIR", "./app/knowledge_base")


settings = Settings()
