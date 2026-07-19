from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine

from expenses_ai_agent.api.routes import analytics, categories, expenses

engine = create_engine("sqlite:///expenses.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle handler."""
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Expense API", version="1.0.0", lifespan=lifespan)

app.include_router(analytics.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(expenses.router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def status_check():
    return {"status": "ok"}
