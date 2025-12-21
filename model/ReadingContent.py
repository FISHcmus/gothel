from typing import List, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship, Mapped

from model.Base import Base, TimestampMixin
if TYPE_CHECKING:
    from model.Question import MultiChoiceQuestionDB


class ReadingContentDB(Base, TimestampMixin):
    """
    Database model for reading content, reading content can be very short paragraph to a full reading exam.
    """
    __tablename__ = "reading_content_table"
    id:Mapped[int] = Column(Integer, primary_key=True, index=True)
    content:Mapped[str] = Column(String)

    multi_choice_questions: Mapped[List["MultiChoiceQuestionDB"]] = relationship(
        "MultiChoiceQuestionDB",
        back_populates="reading_content",
        cascade="all, delete-orphan",
    )
    """
    list[MultichoiceQuestionDB]: One reading passage can have multiple questions associated with it
    """

    evidence_problems: Mapped[List["EvidenceProblemDB"]] = relationship(
        "EvidenceProblemDB",
        back_populates="reading_content",
        cascade="all, delete-orphan",
    )
    """
    One reading passage can have multiple evidence problems associated with it
    """
