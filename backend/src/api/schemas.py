from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .common import Priority, Status


class ItemBase(BaseModel):
    summary: str = Field(max_length=200)
    description: str | None = Field(default=None)
    priority: Priority = Field(default=Priority.MEDIUM)
    due: datetime | None = Field(default=None)


class ItemCreate(ItemBase):
    ...


class ItemRead(ItemBase):
    id: UUID
    created: datetime
    status: Status


class ItemUpdate(BaseModel):
    summary: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None)
    status: Status | None = Field(default=None)
    priority: Priority | None = Field(default=None)
    due: datetime | None = Field(default=None)
