# --- DATABASE SETUP (SQLAlchemy) ---
from typing import List, TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped

from model.Base import Base, TimestampMixin
if TYPE_CHECKING:
    from model.Question import EvidenceProblemDB, MultiChoiceQuestionDB

# --- DATABASE MODELS ---
class UserDB(Base,TimestampMixin):
    __tablename__ = "user_table"
    id:Mapped[int] = Column(Integer, primary_key=True, index=True)
    username:Mapped[str] = Column(String, unique=True, index=True)
    hashed_password:Mapped[str] = Column(String)
    role:Mapped[str] = Column(String, default="user")  # e.g., 'user', 'admin'
    # one-to-many: a user can solve many evidence problems
    evidence_problems_solved:Mapped[List["EvidenceProblemDB"]] = relationship(
        "EvidenceProblemDB",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    multichoice_problems_solved:Mapped[List["MultiChoiceQuestionDB"]] = relationship(
        "MultiChoiceQuestionDB",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def solved_evidence_count(self) -> int:
        return len(self.evidence_problems_solved)




