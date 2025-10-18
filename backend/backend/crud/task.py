from uuid import UUID

from sqlmodel import Session, select

from ..models import Task, User
from ..schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, user: User, data: TaskCreate) -> Task:
    task = Task(
        summary=data.summary,
        description=data.description,
        priority=data.priority,
        due=data.due,
        uid=user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def read_task(db: Session, user: User, uuid: UUID) -> Task | None:
    statement = select(Task).join(User).where(Task.uid == user.id).where(Task.uuid == uuid)
    task = db.exec(statement).first()
    return task


def read_tasks(db: Session, user: User) -> list[Task] | None:
    statement = select(Task).join(User).where(Task.uid == user.id)
    tasks = db.exec(statement).all()
    return tasks


def update_task(db: Session, user: User, uuid: UUID, update: TaskUpdate) -> Task | None:
    task = read_task(db, user, uuid)
    if not task:
        return

    data = update.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(task, key, value)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, user: User, uuid: UUID) -> bool:
    task = read_task(db, user, uuid)
    if not task:
        return False

    db.delete(task)
    db.commit()
    return True
