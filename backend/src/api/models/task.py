from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field

from ..common import Priority, Status


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID = Field(default_factory=uuid4, index=True)
    summary: str = Field(max_length=200)
    description: str | None = Field(default=None)
    priority: Priority = Field(default=Priority.MEDIUM, index=True)
    due: datetime | None = Field(default=None)
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: Status = Field(default=Status.TODO)

    uid: UUID = Field(foreign_key="user.id")
