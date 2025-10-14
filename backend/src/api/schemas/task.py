from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ..common import Priority


class TaskBase(BaseModel):
    summary: str = Field(max_length=200)
    description: str | None = Field(default=None)
    priority: Priority = Field(default=Priority.MEDIUM)
    due: datetime | None = Field(default=None)


class TaskCreate(TaskBase):
    ...


class TaskRead(TaskBase):
    uuid: UUID
    created: datetime
    done: bool


class TaskUpdate(BaseModel):
    summary: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None)
    done: bool | None = Field(default=None)
    priority: Priority | None = Field(default=None)
    due: datetime | None = Field(default=None)
