from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..auth.dependencies import get_current_user
from ..crud.task import (create_task, read_task, read_tasks, update_task,
                         delete_task)
from ..db import get_session
from ..schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=TaskRead, status_code=201)
async def create(
    task: TaskCreate,
    session: Session = Depends(get_session),
    user: Session = Depends(get_current_user)
):
    task = create_task(session, user, task)
    return task


@router.get("/", response_model=list[TaskRead], status_code=200)
async def read(
    session: Session = Depends(get_session),
    user: Session = Depends(get_current_user)
):
    tasks = read_tasks(session, user)
    if not tasks:
        raise HTTPException(status_code=404, detail=f"Tasks NOT FOUND!")
    return tasks


@router.get("/{uuid}", response_model=TaskRead, status_code=200)
async def read(
    uuid: UUID,
    session: Session = Depends(get_session),
    user: Session = Depends(get_current_user)
):
    task = read_task(session, user, uuid)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {uuid} NOT FOUND!")
    return task


@router.patch("/{uuid}", response_model=TaskRead, status_code=200)
async def update(
    uuid: UUID,
    update: TaskUpdate,
    session: Session = Depends(get_session),
    user: Session = Depends(get_current_user)
):
    task = update_task(session, user, uuid, update)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {uuid} NOT FOUND!")

    return task


@router.delete("/{uuid}", status_code=204)
async def delete(
    uuid: UUID,
    session: Session = Depends(get_session),
    user: Session = Depends(get_current_user)
):
    success = delete_task(session, user, uuid)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task {uuid} NOT FOUND!")
