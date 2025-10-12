from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..auth.dependencies import get_current_user
from ..common import Priority, Status
from ..db import get_session
from ..models import Item
from ..schemas.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=ItemRead, status_code=201)
async def create(
    item: ItemCreate,
    session: Session = Depends(get_session),
    user: Session = Depends(get_current_user)
):
    item = Item(
        summary=item.summary,
        description=item.description,
        priority=item.priority,
        due=item.due,
        uid=user.id
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("/", response_model=list[ItemRead], status_code=200)
async def read(
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


@router.get("/{uuid}", response_model=ItemRead, status_code=200)
async def read(uuid: UUID, session: Session = Depends(get_session)):
    statement = select(Item).where(Item.uuid == uuid)
    item = session.exec(statement).first()
    # FIXME: check if the user has access to this item
    if not item:
        raise HTTPException(status_code=404, detail=f"Work Item {uuid} NOT FOUND!")
    return item


@router.patch("/{uuid}", response_model=ItemRead, status_code=200)
async def update(uuid: UUID, update: ItemUpdate, session: Session = Depends(get_session)):
    statement = select(Item).where(Item.uuid == uuid)
    item = session.exec(statement).first()
    # FIXME: check if the user has access to this item
    if not item:
        raise HTTPException(status_code=404, detail=f"Work Item {uuid} NOT FOUND!")

    data = update.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(item, key, value)
    
    session.add(item)
    session.commit()
    session.refresh(item)

    return item


@router.delete("/{uuid}", status_code=204)
async def delete(uuid: UUID, session: Session = Depends(get_session)):
    statement = select(Item).where(Item.uuid == uuid)
    item = session.exec(statement).first()
    # FIXME: check if the user has access to this item
    if not item:
        raise HTTPException(status_code=404, detail=f"Work Item {uuid} NOT FOUND!")
    
    session.delete(item)
    session.commit()
