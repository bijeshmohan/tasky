import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=20)

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


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=64)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')

        return v


class UserRead(UserBase):
    id: UUID
    created: datetime


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
