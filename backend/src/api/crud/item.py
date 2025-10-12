from uuid import UUID

from sqlmodel import Session, select

from ..models import Item, User
from ..schemas.item import ItemCreate, ItemUpdate


def create_user_item(db: Session, user: User, data: ItemCreate) -> Item:
    item = Item(
        summary=data.summary,
        description=data.description,
        priority=data.priority,
        due=data.due,
        uid=user.id
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_user_item(db: Session, user: User, uuid: UUID) -> Item | None:
    statement = select(Item).join(User).where(Item.uid == user.id).where(Item.uuid == uuid)
    item = db.exec(statement).first()
    return item


def get_user_items(db: Session, user: User) -> list[Item] | None:
    statement = select(Item).join(User).where(Item.uid == user.id)
    items = db.exec(statement).all()
    return items


def update_user_item(db: Session, user: User, uuid: UUID, update: ItemUpdate) -> Item | None:
    item = get_user_item(db, user, uuid)
    if not item:
        return

    data = update.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(item, key, value)

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_user_item(db: Session, user: User, uuid: UUID) -> bool:
    item = get_user_item(db, user, uuid)
    if not item:
        return False

    db.delete(item)
    db.commit()
    return True
