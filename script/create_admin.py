# python

from sqlalchemy.orm import Session

from auth.auth import get_password_hash
from model.Base import get_db
from model.User import UserDB
from model.EvidenceProblem import EvidenceProblemDB # noqa
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"


def create_admin(session: Session) -> None:
    existing = session.query(UserDB).filter(UserDB.username == ADMIN_USERNAME).first()
    if existing:
        return
    hashed = get_password_hash(ADMIN_PASSWORD)
    admin = UserDB(username=ADMIN_USERNAME, hashed_password=hashed, role="admin")
    session.add(admin)
    session.commit()



if __name__ == "__main__":
    db_gen = get_db()
    db = next(db_gen)
    try:
        create_admin(db)
    finally:
        db_gen.close()
