import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from rag_pipeline import RAGPipeline

app = FastAPI(title="Dadrah Sarbazi RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = RAGPipeline()


class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    answer_text, sources = pipeline.answer(session_id, req.query)
    return ChatResponse(session_id=session_id, answer=answer_text, sources=sources)


@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    pipeline.memory.sessions.pop(session_id, None)
    return {"status": "cleared"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
