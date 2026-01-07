from typing import List

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from model.Base import Base, TimestampMixin, user_flashlight_problem_association
from model.User import UserDB

class FlashlightProblemDB(Base, TimestampMixin):
    """
    Database model for flashlight drill problems.

    In flashlight drills, users must find and highlight specific target text
    within a reading passage, typically under time pressure (15 seconds).
    This exercises rapid scanning and keyword location skills.
    """
    __tablename__ = "flashlight_problem_table"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    problem_statement: Mapped[str] = Column(String, nullable=False)
    target: Mapped[str] = Column(String, nullable=False)
    reading_content: Mapped[str] = Column(String, nullable=False)

    solved_by_users: Mapped[List["UserDB"]] = relationship(
        "UserDB",
        secondary=user_flashlight_problem_association,
        back_populates="flashlight_problems_solved",
    )
