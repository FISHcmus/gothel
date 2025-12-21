from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from model.Base import Base, TimestampMixin
if TYPE_CHECKING:
    from model.User import UserDB
class MultiChoiceQuestionDB(Base,TimestampMixin):
    __tablename__ = "multiple_choice_question_table"
    id:Mapped[int] = Column(Integer, primary_key=True, index=True)
    question:Mapped[str] = Column(String)
    choices:Mapped[str] = Column(String)
    correct_answer:Mapped[str] = Column(String)

    user_id: Mapped[int] = Column(Integer, ForeignKey("user_table.id"), nullable=False, index=True)
    user: Mapped["UserDB"] = relationship(
        "UserDB",
        back_populates="multichoice_problems_solved",
    )
    reading_content_id: Mapped[int] = Column(Integer, ForeignKey("reading_content_table.id"), nullable=False, index=True)
    reading_content: Mapped["ReadingContentDB"] = relationship(
        "ReadingContentDB",
        back_populates="multi_choice_questions",
    )




class EvidenceProblemDB(Base,TimestampMixin):
    __tablename__ = "evidence_problem_table"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    problem_statement: Mapped[str] = Column(String)
    evidence: Mapped[str] = Column(String)

    user_id: Mapped[int] = Column(Integer, ForeignKey("user_table.id"), nullable=False, index=True)
    user: Mapped["UserDB"] = relationship(
        "UserDB",
        back_populates="evidence_problems_solved",
    )
    reading_content_id: Mapped[int] = Column(Integer, ForeignKey("reading_content_table.id"), nullable=False, index=True)
    reading_content: Mapped["ReadingContentDB"] = relationship(
        "ReadingContentDB",
        back_populates="evidence_problems",
    )
