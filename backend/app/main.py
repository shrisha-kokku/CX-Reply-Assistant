from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.routes import conversations, kb, replies

app = FastAPI(title="CX Reply Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversations.router)
app.include_router(kb.router)
app.include_router(replies.router)


@app.get("/health")
def health():
    return {"status": "ok"}
