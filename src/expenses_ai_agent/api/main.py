from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine

engine = create_engine("sqlite:///expenses.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle handler."""
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Expense API", version="1.0.0", lifespan=lifespan)


@app.get("/api/v1/health")
async def status_check():
    return {"status": "ok"}
