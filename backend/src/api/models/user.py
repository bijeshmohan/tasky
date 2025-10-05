import re
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
        v = v.lower()

        if not re.match(r'^[a-z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')

        if not re.search(r'[a-z]', v):
            raise ValueError('Username must contain at least one letter')

        if not v[0].isalpha():
            raise ValueError('Username must start with a letter')

        return v
