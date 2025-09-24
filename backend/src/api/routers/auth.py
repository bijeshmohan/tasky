from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from ..auth.security import tokenize, verify
from ..crud.user import get_user_by_username
from ..db import get_session
from ..schemas.token import Token

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/token", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = get_user_by_username(session, form.username)
    if not user or not verify(form.password, user.hashword):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    access_token = tokenize({"sub": user.username})
    return Token(token=access_token, type="bearer")
