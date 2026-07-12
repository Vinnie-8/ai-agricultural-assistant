from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.diagnosis import router as diagnosis_router
from app.api.v1.chat import router as chat_router

app = FastAPI(
    title="AI Agricultural Assistant",
    version="1.0.0",
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(diagnosis_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "AI Agricultural Assistant API",
    }