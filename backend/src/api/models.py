from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field

from .common import Priority, Status, Type


class Item(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    summary: str = Field(max_length=200)
    type: Type = Field(default=Type.TASK, index=True)
    description: str | None = Field(default=None)
    priority: Priority = Field(default=Priority.MEDIUM, index=True)
    due: datetime | None = Field(default=None)
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: Status = Field(default=Status.TODO)
