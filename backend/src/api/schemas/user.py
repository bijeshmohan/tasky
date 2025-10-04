import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=20)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        if not v.replace('_', '').isalnum():
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v.lower()


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
