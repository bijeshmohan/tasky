import os
from datetime import datetime, timedelta, timezone
from typing import overload

from jose import JWTError, jwt
from passlib.context import CryptContext


SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@overload
def verify(password: str, hashword: str) -> bool: ...


@overload
def verify(token: str) -> str | None: ...


def verify(arg1: str, arg2: str | None = None) -> bool | str | None:
    if arg2:
        password = arg1
        hashword = arg2
        return context.verify(password, hashword)
    else:
        token = arg1
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None


def hashword(password: str) -> str:
    return context.hash(password)


def tokenize(data: dict, delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if delta:
        expire = datetime.now(timezone.utc) + delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
