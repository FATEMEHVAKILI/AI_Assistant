from fastapi import FastAPI
from fastapi.responses import JSONResponse
from collections import defaultdict, deque
from time import time
from .database import engine, Base
from .routers import messages, users
from .services.llm_service import LLMClient
from .services.intent_service import IntentService
from .services.kb_service import KBService
from .utils.logger import setup_logger
from .config import settings

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

request_history = defaultdict(deque)


@app.middleware("http")
async def simple_rate_limit(request, call_next):
    client_host = request.client.host if request.client else "unknown"
    now = time()
    window_start = now - settings.RATE_LIMIT_WINDOW_SECONDS
    history = request_history[client_host]

    while history and history[0] < window_start:
        history.popleft()

    if len(history) >= settings.RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."},
        )

    history.append(now)
    return await call_next(request)

# Include routers
app.include_router(messages.router)
app.include_router(users.router)
