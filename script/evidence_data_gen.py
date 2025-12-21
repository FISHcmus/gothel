import random
from typing import cast

from faker import Faker
from sqlalchemy.orm import Session

from model.Base import get_db
from model.User import UserDB # noqa

from model.EvidenceProblem import EvidenceProblemDB
fake = Faker()


def create_fake_problems(session: Session, count: int = 10) -> None:
    unique_fake = cast(Faker, fake.unique)
    for _ in range(count):
        paragraph = unique_fake.paragraph()
        evidence = random.choice(paragraph.split(' '))


        problem = EvidenceProblemDB(
            problem_statement=unique_fake.sentence(),
            reading_content=paragraph,
            evidence=evidence
        )
        session.add(problem)
    session.commit()


if __name__ == "__main__":
    db_gen = get_db()
    db = next(db_gen)
    try:
        create_fake_problems(db, 10)
    finally:
        db_gen.close()
