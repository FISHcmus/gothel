# Import all models so they're registered with Base.metadata
# This is required for SQLAlchemy to create all tables correctly
from model.Base import Base, engine, SessionLocal, get_db, reset_db, TimestampMixin
from model.User import UserDB
from model.EvidenceProblem import EvidenceProblemDB
from model.FlashlightProblem import FlashlightProblemDB
from model.ReadingContent import ReadingContentDB
from model.MCQuestion import MultiChoiceQuestionDB

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "reset_db",
    "TimestampMixin",
    "UserDB",
    "EvidenceProblemDB",
    "FlashlightProblemDB",
    "ReadingContentDB",
    "MultiChoiceQuestionDB",
]
