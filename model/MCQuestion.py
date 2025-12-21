from typing import TYPE_CHECKING, List

from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped

from model.Base import Base, TimestampMixin
if TYPE_CHECKING:
    from model.User import UserDB
class MultiChoiceQuestionDB(Base,TimestampMixin):
    __tablename__ = "multiple_choice_question_table"
    id:Mapped[int] = Column(Integer, primary_key=True, index=True)
    question:Mapped[str] = Column(String, nullable=False)
    choices:Mapped[List[str]] = Column(JSON, nullable=False)
    correct_answer:Mapped[str] = Column(String,nullable=False)

    # user_id: Mapped[int] = Column(Integer, ForeignKey("user_table.id"), nullable=False, index=True)
    # user: Mapped["UserDB"] = relationship(
    #     "UserDB",
    #     back_populates="multichoice_problems_solved",
    # )





