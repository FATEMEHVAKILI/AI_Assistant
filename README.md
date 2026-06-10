# AI Assistant MVP

AI Assistant is a FastAPI-based MVP for handling lead and support messages. It receives a user message, detects the user intent, assigns a simple segment, retrieves relevant context from a vector knowledge base, generates a reply, and stores the conversation history.

The current product scope covers questions about VIP services, exchange registration, KOL collaboration, general service information, and support cases that should be handed over to a human.

## Technologies Used

- Python 3.10
- FastAPI and Uvicorn
- SQLAlchemy with SQLite
- ChromaDB as the Vector DB
- OpenAI SDK for real API mode
- Ollama support for local LLM mode
- Mock LLM fallback for running without API keys
- Docker and Docker Compose
- Pytest and FastAPI TestClient

## Features

- `POST /message` endpoint for assistant replies
- `GET /users` endpoint for stored users
- `GET /users/{user_id}/messages` endpoint for message history
- Intent detection with rule-based logic plus optional LLM check
- User segmentation based on intent
- ChromaDB vector search over files in `app/knowledge_base`
- SQLite persistence for users and messages
- Simple in-memory rate limit middleware
- Structured error handling for empty messages and server errors
- Basic endpoint tests

## Project Structure

```text
app/
  main.py                 FastAPI app setup, services, rate limit middleware
  config.py               Environment-based settings
  database.py             SQLAlchemy engine and session
  models.py               User and Message database models
  schemas.py              Pydantic request/response schemas
  routers/
    messages.py           /message endpoint
    users.py              user and message-history endpoints
  services/
    intent_service.py     intent and segment detection
    kb_service.py         ChromaDB knowledge-base loading/search
    llm_service.py        API/local/mock LLM client
  knowledge_base/         text documents loaded into ChromaDB
tests/
  test_endpoints.py       simple endpoint tests
```

## Environment

Create a `.env` file from the sample:

```bash
cp .env.example .env
```

Example:

```env
DATABASE_URL=sqlite:///./ai_assistant.db
LLM_PROVIDER=mock
OPENAI_API_KEY=
CLAUDE_API_KEY=
ANTHROPIC_API_KEY=
CHROMA_DIR=./chroma_db
KB_DIR=./app/knowledge_base
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60
```

Do not commit real API keys.

## Local Installation and Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

## Docker Run

Build and run with Docker:

```bash
docker build -t ai-assistant .
docker run --env-file .env -p 8000:8000 ai-assistant
```

Run with Docker Compose:

```bash
docker compose up --build
```

The compose file mounts `logs/` and `chroma_db/` so logs and vector data can persist between container runs.

## Tests

Run the basic endpoint tests:

```bash
pytest
```

If `pytest` is not available globally, run it through the local virtual environment:

```bash
.\.venv\Scripts\python.exe -m pytest
```

Current tests are in `tests/test_endpoints.py` and use FastAPI `TestClient`. These are API-level tests: they call the FastAPI app directly, without starting Uvicorn or opening a real network port.

Test coverage included:

- `test_message_endpoint_returns_intent_and_reply`: sends a valid `POST /message` request with `What is VIP?` and verifies `200 OK`, intent `vip_question`, segment `vip_interest`, `needs_human_support=false`, and a non-empty assistant reply.
- `test_empty_message_is_rejected`: sends `POST /message` with an empty message and verifies `400 Bad Request` with `Message cannot be empty`.

The test setup uses `LLM_PROVIDER=mock`, a temporary SQLite database, a temporary ChromaDB directory, and a stubbed knowledge-base search result. This keeps tests fast, isolated, and runnable without real API keys.

## Sample Requests and Responses

Endpoint:

```text
POST /message
Content-Type: application/json
```

### 1. خدمات VIP چیه؟

Request:

```json
{
  "user_id": "user_001",
  "name": "Ali",
  "message": "خدمات VIP چیه؟"
}
```

Response example:

```json
{
  "reply": "VIP services include priority 24/7 support, advanced AI features, custom workflow integrations, dedicated account management, and faster response times.",
  "intent": "vip_question",
  "user_segment": "vip_interest",
  "needs_human_support": false
}
```

### 2. چطور در صرافی ثبت نام کنم؟

Request:

```json
{
  "user_id": "user_002",
  "name": "Sara",
  "message": "چطور در صرافی ثبت نام کنم؟"
}
```

Response example:

```json
{
  "reply": "To register on the exchange, please visit the sign-up page, provide your email and phone number, verify your identity (KYC), and set up two-factor authentication (2FA).",
  "intent": "exchange_registration",
  "user_segment": "exchange_signup",
  "needs_human_support": false
}
```

### 3. می خوام KOL بشم.

Request:

```json
{
  "user_id": "user_003",
  "name": "Reza",
  "message": "می خوام KOL بشم."
}
```

Response example:

```json
{
  "reply": "The KOL program offers collaboration opportunities for influencers. Benefits include exclusive commission rates, promotional materials, and direct support.",
  "intent": "kol_collaboration",
  "user_segment": "kol_candidate",
  "needs_human_support": false
}
```

### 4. پول دادم ولی اشتراکم فعال نشده.

Request:

```json
{
  "user_id": "user_004",
  "name": "Mina",
  "message": "پول دادم ولی اشتراکم فعال نشده."
}
```

Response example:

```json
{
  "reply": "I understand this needs support. Please send the payment time, tracking number, and account details so the support team can check it.",
  "intent": "support_request",
  "user_segment": "support_needed",
  "needs_human_support": true
}
```

### 5. Trade Assist چیست؟

Request:

```json
{
  "user_id": "user_005",
  "name": "Nima",
  "message": "Trade Assist چیست؟"
}
```

Response example:

```json
{
  "reply": "Trade Assist is part of the assistant services. It helps users get guidance from the available knowledge base. For exact product details, add the related document to app/knowledge_base.",
  "intent": "general_info",
  "user_segment": "general_question",
  "needs_human_support": false
}
```

Actual wording may change depending on `LLM_PROVIDER`, the available knowledge-base documents, and whether a real API key is configured.

## Architecture

The app uses a simple layered architecture:

- Routers receive HTTP requests and return API responses.
- Services handle intent detection, LLM calls, and knowledge-base retrieval.
- ChromaDB stores embeddings for text files in `app/knowledge_base`.
- SQLite stores users and message history.
- The LLM client chooses a provider based on configuration: API, local Ollama, or mock.

Flow:

```text
Client -> FastAPI router -> IntentService -> KBService/ChromaDB -> LLMClient -> SQLite -> Response
```

## LLM Mode: Real or Mock?

By default, `.env.example` uses:

```env
LLM_PROVIDER=mock
```

This means the project can run without a real API key. The mock mode uses keyword and context-aware fallback logic.

Supported modes:

- `mock`: no external LLM; safest for local testing and review
- `api`: uses OpenAI when `OPENAI_API_KEY` is set
- `local`: uses Ollama at `http://localhost:11434` with model `llama3`
- `auto`: chooses API if keys exist, then local Ollama if available, otherwise mock

The current real API implementation calls OpenAI. `CLAUDE_API_KEY` / `ANTHROPIC_API_KEY` is included in env configuration for future provider expansion.

## Rate Limit

A simple in-memory rate limiter is enabled in `app/main.py`.

Default:

```env
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60
```

This is enough for an MVP, but it resets when the process restarts and is not shared across multiple replicas.

## Limitations and Future Work

Current limitations:

- The rate limiter is in-memory and not production-grade.
- `needs_human_support` is mostly based on intent and fallback conditions.
- Knowledge-base documents are small text files and need richer real product content.
- Real LLM support is implemented for OpenAI; Claude/Anthropic config is present but not fully wired as a separate provider.
- SQLite is suitable for MVP/local use, not high-scale production traffic.
- Mock responses are deterministic and less natural than a real LLM.

If there were more time, I would improve:

- more accurate `needs_human_support` detection with confidence scoring
- richer architecture documentation and sequence diagrams
- more endpoint and service-level tests
- Redis-based distributed rate limiting
- admin tooling for adding/updating knowledge-base documents
- stronger retrieval quality with chunking, metadata filters, and evaluation cases
- separate production configuration for PostgreSQL and managed Vector DB
- full Anthropic/Claude provider implementation

## Submission Checklist

- GitHub link or ZIP file: submit the project repository or a ZIP of this folder.
- README file: this file.
- `.env.example`: included with safe placeholder values only.
- Run command:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- Docker command:

```bash
docker compose up --build
```

- Sample requests/responses: included above.
