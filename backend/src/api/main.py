from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from .db import engine
from .routers import items, users, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    ...


app = FastAPI(title="Task Master", lifespan=lifespan)
app.include_router(items.router)
app.include_router(users.router)
app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Tasky API!"}
