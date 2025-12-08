from fastapi import FastAPI
from contextlib import asynccontextmanager
from .core.database import create_db_and_tables
from .api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Question Generation Engine", version="1.0.0", lifespan=lifespan)

app.include_router(router)
