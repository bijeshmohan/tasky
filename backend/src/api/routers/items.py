from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..auth.dependencies import get_current_user
from ..crud.item import (create_user_item, get_user_item, get_user_items,
                         update_user_item, delete_user_item)
from ..db import get_session
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
    item = create_user_item(session, user, item)
    return item


@router.get("/", response_model=list[ItemRead], status_code=200)
async def read(
    session: Session = Depends(get_session),
    user: Session = Depends(get_current_user)
):
    items = get_user_items(session, user)
    if not items:
        raise HTTPException(status_code=404, detail=f"Work Items NOT FOUND!")
    return items


@router.get("/{uuid}", response_model=ItemRead, status_code=200)
async def read(
    uuid: UUID,
    session: Session = Depends(get_session),
    user: Session = Depends(get_current_user)
):
    item = get_user_item(session, user, uuid)
    if not item:
        raise HTTPException(status_code=404, detail=f"Work Item {uuid} NOT FOUND!")
    return item


@router.patch("/{uuid}", response_model=ItemRead, status_code=200)
async def update(
    uuid: UUID,
    update: ItemUpdate,
    session: Session = Depends(get_session),
    user: Session = Depends(get_current_user)
):
    item = update_user_item(session, user, uuid, update)
    if not item:
        raise HTTPException(status_code=404, detail=f"Work Item {uuid} NOT FOUND!")

    return item


@router.delete("/{uuid}", status_code=204)
async def delete(
    uuid: UUID,
    session: Session = Depends(get_session),
    user: Session = Depends(get_current_user)
):
    item = delete_user_item(session, user, uuid)
    if not item:
        raise HTTPException(status_code=404, detail=f"Work Item {uuid} NOT FOUND!")
