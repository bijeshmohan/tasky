from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Session, create_engine, select

from .common import Priority, Status
from .models import Item
from .schemas import ItemCreate, ItemRead, ItemUpdate


DATABASE = "sqlite:///./items.db"
engine = create_engine(DATABASE, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    ...

app = FastAPI(title="Task Master", lifespan=lifespan)

@app.post("/items", response_model=ItemRead, status_code=201)
def create(item: ItemCreate, session: Session = Depends(get_session)):
    item = Item.model_validate(item)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@app.get("/items", response_model=list[ItemRead], status_code=200)
def read(
    skip: int = 0,
    limit: int = 100,
    status: Status | None = None,
    priority: Priority | None = None,
    session: Session = Depends(get_session)
):
    query = select(Item)

    if status:
        query = query.where(Item.status == status)
    
    if priority:
        query = query.where(Item.priority == priority)

    items = session.exec(query.offset(skip).limit(limit)).all()
    return items


@app.get("/items/{id}", response_model=ItemRead, status_code=200)
def read(id: UUID, session: Session = Depends(get_session)):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Work Item {id} NOT FOUND!")
    return item


@app.patch("/items/{id}", response_model=ItemRead, status_code=200)
def update(id: UUID, update: ItemUpdate, session: Session = Depends(get_session)):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Work Item {id} NOT FOUND!")

    data = update.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(item, key, value)
    
    session.add(item)
    session.commit()
    session.refresh(item)

    return item


@app.delete("/items/{id}", status_code=204)
def delete(id: UUID, session: Session = Depends(get_session)):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Work Item {id} NOT FOUND!")
    
    session.delete(item)
    session.commit()
