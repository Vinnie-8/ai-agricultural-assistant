# AI Agricultural Assistant — Project Structure

This project consists of three independently-run services that communicate
over HTTP:

1. **`backend/`** — FastAPI service handling authentication, diagnosis
   persistence, and orchestration (calls the AI service on behalf of the
   frontend).
2. **`ai-service/`** — FastAPI service running the crop disease
   classification model and the LLM-powered chat agent (RAG + weather
   tool via LangGraph).
3. **`frontend/`** — Flask web application providing the user interface.

---

## 1. `backend/`

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                  # Shared dependencies (get_current_user, get_auth_service)
│   │   └── v1/
│   │       ├── auth.py              # POST /register, /login, /refresh
│   │       ├── users.py             # User-related endpoints
│   │       ├── diagnosis.py         # POST /diagnosis/predict
│   │       └── chat.py              # POST /chat
│   ├── core/
│   │   └── config.py                # Settings (DATABASE_URL, SECRET_KEY, AI_SERVICE_URL, etc.)
│   ├── database/
│   │   ├── base.py                  # SQLAlchemy declarative Base
│   │   ├── dependencies.py          # get_db() session dependency
│   │   ├── session.py               # Engine + sessionmaker
│   │   └── migrations/              # Alembic migrations
│   │       ├── env.py
│   │       └── versions/
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── base_model.py            # Abstract base: id, created_at, updated_at
│   │   ├── user.py                  # User
│   │   ├── diagnosis.py             # Diagnosis
│   │   └── chat_history.py          # ChatHistory
│   ├── repositories/                # Data access layer
│   │   ├── user_repository.py
│   │   ├── diagnosis_repository.py
│   │   └── chat_repository.py
│   ├── schemas/                     # Pydantic request/response models
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── diagnosis.py
│   │   └── chat.py
│   ├── services/                    # Business logic
│   │   ├── auth_service.py          # Register/login logic
│   │   ├── diagnosis_service.py     # Image save + ML inference (ViT model)
│   │   └── ai_client.py             # HTTP client calling the AI service
│   ├── utils/
│   │   ├── jwt.py                   # Access/refresh token creation & decoding
│   │   └── security.py              # Password hashing/verification
│   └── main.py                      # FastAPI app instance, router registration
├── uploads/                          # Saved diagnosis images
├── requirements.txt
└── .env                              # DATABASE_URL, SECRET_KEY, AI_SERVICE_URL, etc.
```

**Responsibilities:** user authentication (JWT access/refresh tokens),
running crop image classification, persisting diagnoses and chat history
to PostgreSQL, and proxying chat requests to the AI service.

**Key architectural decisions:**
- Fully synchronous throughout (SQLAlchemy `Session`, not `AsyncSession`)
  for consistency and simplicity.
- Diagnosis endpoint is currently public (no auth required) to simplify
  testing; chat endpoint requires authentication.
- Uses `wambugu71/crop_leaf_diseases_vit`, a pretrained Vision Transformer
  from Hugging Face, covering Corn, Potato, Rice, and Wheat — no custom
  training required for these crops.

---

## 2. `ai-service/`

```
ai-service/
├── app/
│   ├── agents/
│   │   └── farming_agent.py         # LangGraph ReAct agent (OpenAI-backed)
│   ├── api/
│   │   ├── chat.py                  # POST /api/v1/chat
│   │   └── schemas.py               # ChatRequest / ChatResponse
│   ├── config/
│   │   └── settings.py              # OPENAI_API_KEY, WEATHER_API_KEY, Chroma config
│   ├── prompts/
│   │   └── system_prompt.py         # Agent system prompt & guidelines
│   ├── rag/
│   │   ├── ingest.py                # Builds the Chroma vector store from knowledge_base/
│   │   └── retriever.py             # Loads the persisted vector store for querying
│   ├── tools/
│   │   ├── knowledge_base_tool.py   # search_knowledge_base — RAG retrieval tool
│   │   └── weather_tool.py          # get_weather_forecast — WeatherAPI.com integration
│   └── main.py                      # FastAPI app instance
├── checkpoints/                     # (reserved for future custom-trained model artifacts)
├── knowledge_base/                  # Markdown reference docs (disease, fertilizer, pesticide info)
├── ml/                               # Custom training pipeline (maize model, currently unused
│   ├── datasets/                    #  in favor of the pretrained ViT model, kept for reference)
│   ├── models/model_def.py          # MobileNetV2 transfer-learning model definition
│   ├── preprocessing/dataset.py     # Dataset loading, augmentation, train/val split
│   ├── training/train.py            # Training loop
│   └── utils/export_onnx.py         # ONNX export for inference
├── vector_db/                        # Persisted Chroma vector store (generated by ingest.py)
├── requirements.txt
└── .env                               # OPENAI_API_KEY, WEATHER_API_KEY
```

**Responsibilities:** runs the conversational AI agent that answers
farmer questions, grounding its responses in a curated knowledge base via
Retrieval-Augmented Generation (RAG), and factoring in live weather data
when relevant (e.g. advising against spraying fungicide before rain).

**Key architectural decisions:**
- LangGraph's `create_react_agent` lets the LLM (GPT-4o-mini via
  `langchain-openai`) decide when to call each tool, rather than a fixed
  pipeline — e.g. it only checks weather when the farmer's question
  actually relates to timing or treatment application.
- ChromaDB stores document embeddings locally (via
  `sentence-transformers`, no external API calls needed for retrieval
  itself); only the final response generation calls OpenAI.
- Conversation memory is per-session (`thread_id` = `session_id`) via
  LangGraph's `InMemorySaver` — memory persists only for the life of the
  running process, not across restarts.
- The `ml/` training pipeline (MobileNetV2, transfer learning, CPU-
  feasible) was built and is functional, but the project ultimately used
  a pretrained Hugging Face model instead, since it required no training
  time and covered more crops.

---

## 3. `frontend/`

```
frontend/
├── app.py                            # All Flask routes
├── templates/
│   ├── base.html                    # Shared layout, navbar, Bootstrap CDN
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html               # Photo upload page
│   └── diagnosis.html               # Diagnosis result + chat interface
├── static/
│   └── css/
│       └── style.css                # Chat bubble styling
├── requirements.txt
└── .env                               # FLASK_SECRET_KEY, BACKEND_URL
```

**Responsibilities:** provides the farmer-facing web interface —
register/login, photo upload, diagnosis display, and an in-page chat
panel for follow-up questions.

**Key architectural decisions:**
- Server-rendered (Jinja2 templates), no JavaScript framework — every
  action is a standard form POST + redirect.
- JWT tokens issued by the backend are stored in the Flask session
  (signed cookie), attached as an `Authorization: Bearer` header on every
  backend request.
- The farmer's request IP (`request.remote_addr`) is passed to the
  backend as `location`, which flows through to the AI service's weather
  tool for local forecast lookups.

---

## Data Flow Summary

```
Farmer (browser)
      │  1. upload leaf photo
      ▼
Frontend (Flask, :5000)
      │  2. POST /api/v1/diagnosis/predict
      ▼
Backend (FastAPI, :8000)
      │  3. runs ViT model → crop, disease, confidence
      │  4. persists Diagnosis row
      │
      │  5. farmer sends a chat message
      │  6. POST /api/v1/chat (message, diagnosis_id, location)
      ▼
Backend
      │  7. looks up diagnosis → builds context string
      │  8. forwards to AI service
      ▼
AI service (FastAPI, :8001)
      │  9. LangGraph agent reasons over the message
      │  10. calls search_knowledge_base and/or get_weather_forecast as needed
      │  11. generates grounded reply via OpenAI
      ▼
Backend
      │  12. persists ChatHistory row (message + reply)
      ▼
Frontend
      13. displays reply in the chat panel
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI, SQLAlchemy (sync), Alembic, PostgreSQL |
| Authentication | JWT (access + refresh tokens), bcrypt password hashing |
| AI service framework | FastAPI, LangChain, LangGraph |
| LLM | OpenAI (GPT-4o-mini) via `langchain-openai` |
| Image classification | `transformers` (Hugging Face), pretrained ViT model |
| RAG / vector store | ChromaDB, `sentence-transformers` embeddings |
| External APIs | WeatherAPI.com |
| Frontend framework | Flask, Jinja2, Bootstrap 5 |
| Custom ML pipeline (built, currently unused) | PyTorch, torchvision, MobileNetV2, ONNX |
