from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from .db import engine
from .routers import tasks, users, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    ...


app = FastAPI(title="Tasky", lifespan=lifespan)
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Tasky API!"}
