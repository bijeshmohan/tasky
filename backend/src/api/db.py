from sqlmodel import Session, create_engine

DATABASE = "sqlite:///./tasky.db"
engine = create_engine(DATABASE, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
