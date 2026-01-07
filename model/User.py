# --- DATABASE SETUP (SQLAlchemy) ---
from typing import List, TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped

from model.Base import Base, TimestampMixin, user_evidence_problem_association, user_flashlight_problem_association

if TYPE_CHECKING:
    from model.MCQuestion import MultiChoiceQuestionDB
    from model.EvidenceProblem import EvidenceProblemDB
    from model.FlashlightProblem import FlashlightProblemDB


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
        secondary=user_evidence_problem_association,
        back_populates="solved_by_users",
    )

    # one-to-many: a user can solve many flashlight problems
    flashlight_problems_solved:Mapped[List["FlashlightProblemDB"]] = relationship(
        "FlashlightProblemDB",
        secondary=user_flashlight_problem_association,
        back_populates="solved_by_users",
    )

    email: Mapped[str | None] = Column(String, unique=True, index=True, nullable=True)
    avatar_id: Mapped[str | None] = Column(String, nullable=True)


    # multichoice_problems_solved:Mapped[List["MultiChoiceQuestionDB"]] = relationship(
    #     "MultiChoiceQuestionDB",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    # )

    @property
    def solved_evidence_count(self) -> int:
        return len(self.evidence_problems_solved)

    @property
    def solved_flashlight_count(self) -> int:
        return len(self.flashlight_problems_solved)




