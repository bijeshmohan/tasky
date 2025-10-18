from uuid import UUID

from sqlmodel import Session, select
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..auth.security import hashword


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        username = data.username,
        hashword = hashword(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return db.exec(statement).first()


def get_user_by_id(db: Session, uid: UUID) -> User | None:
    return db.get(User, uid)


def update_user(
    db: Session,
    username: str,
    data: UserUpdate
) -> User | None:
    user = get_user_by_username(db, username)
    if not user:
        return None

    update = data.model_dump(exclude_unset=True)
    if "password" in update:
        update["hashword"] = hashword(update.pop("password"))

    for field, value in update.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
