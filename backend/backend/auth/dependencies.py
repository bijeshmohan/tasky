from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from .security import verify
from ..crud.user import get_user_by_username
from ..db import get_session
from ..models.user import User

scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    token: str = Depends(scheme),
    db: Session = Depends(get_session)
) -> User:
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username = verify(token)
    if username is None:
        raise exception

    user = get_user_by_username(db, username)
    if user is None:
        raise exception

    return user
