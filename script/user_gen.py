import random
from faker import Faker
from sqlalchemy.orm import Session
from auth.auth import get_password_hash
from model.Base import get_db
from model.User import UserDB

from model.EvidenceProblem import EvidenceProblemDB # noqa
from script.reset import reset_single_table

fake = Faker()

def create_custom_user(session: Session, username: str, password: str, role: str = "user") -> None:
    exists = session.query(UserDB).filter(UserDB.username == username).first()
    if exists:
        return

    hashed_password = get_password_hash(password)

    user = UserDB(
        username=username,
        hashed_password=hashed_password,
        role=role,
    )
    session.add(user)
    session.commit()

def create_fake_users(session: Session, count: int = 10) -> None:
    for _ in range(count):
        username = fake.unique.user_name()
        password = get_password_hash(fake.password(length=12))

        exists = session.query(UserDB).filter(UserDB.username == username).first()
        if exists:
            continue

        user = UserDB(
            username=username,
            hashed_password=password,
            role="user",
        )
        session.add(user)
    session.commit()


if __name__ == "__main__":
    db_gen = get_db()
    db = next(db_gen)
    try:
        reset_single_table("user_table")
        create_custom_user(db,"nhannht","password","user")
        create_fake_users(db, 10)
    finally:
        db_gen.close()
