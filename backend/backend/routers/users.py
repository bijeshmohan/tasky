from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import get_session
from ..auth.dependencies import get_current_user
from ..crud.user import create_user, get_user_by_username, update_user
from ..models.user import User
from ..schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=201)
async def signup(data: UserCreate, session: Session = Depends(get_session)):
    if get_user_by_username(session, data.username):
        raise HTTPException(status_code=400, detail="User already exists!")

    user = create_user(session, data)
    return user


@router.get("/", response_model=list[UserRead], status_code=200)
async def users(session: Session = Depends(get_session)):
    query = select(User)
    items = session.exec(query).all()
    return items


@router.get("/me", response_model=UserRead, status_code=200)
async def profile(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    return get_user_by_username(session, user.username)


@router.patch("/me", response_model=UserRead, status_code=200)
async def update(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    user = update_user(session, user.username, data)
    return UserRead(
        id=user.id,
        username=user.username,
        created=user.created
    )


@router.delete("/{id}", status_code=204)
async def delete(id: UUID, session: Session = Depends(get_session)):
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {id} NOT FOUND!")

    session.delete(user)
    session.commit()
