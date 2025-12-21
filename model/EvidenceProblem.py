from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, relationship

from model.Base import Base, TimestampMixin, user_evidence_problem_association
from model.User import UserDB


class EvidenceProblemDB(Base,TimestampMixin):
    __tablename__ = "evidence_problem_table"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    problem_statement: Mapped[str] = Column(String,nullable=False)
    evidence: Mapped[str] = Column(String,nullable=False)
    options: Mapped[List[str]] = Column(JSON, nullable=False)
    correct_option: Mapped[int] = Column(Integer,nullable=False)

    solved_by_users: Mapped[List["UserDB"]] = relationship(
        "UserDB",
        secondary=user_evidence_problem_association,
        back_populates="evidence_problems_solved",
    )
    reading_content:Mapped[str] = Column(String,nullable=False)
