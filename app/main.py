from fastapi import FastAPI
from .database import engine, Base
from .routers import messages, users
from .services.llm_service import LLMClient
from .services.intent_service import IntentService
from .services.kb_service import KBService
from .utils.logger import setup_logger

# Setup logging first
logger = setup_logger()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Assistant MVP")

# Initialize services
llm_client = LLMClient()
intent_service = IntentService(llm_client)
kb_service = KBService()

# Attach services to app state for dependency injection
app.state.llm_client = llm_client
app.state.intent_service = intent_service
app.state.kb_service = kb_service

# Include routers
app.include_router(messages.router)
app.include_router(users.router)