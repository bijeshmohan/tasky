from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import field_validator
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(index=True, unique=True, min_length=3, max_length=20)
    hashword: str
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        if not v.replace('_', '').isalnum():
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v.lower()
