from sqlalchemy import create_engine, Column, func, DateTime, Table, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, declared_attr

SQLALCHEMY_DATABASE_URL = "sqlite:///./db_local.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TimestampMixin:
    """Mixin that adds timestamp columns to models."""

    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


def reset_db():
    Base.metadata.drop_all(bind=engine)   # deletes tables (and all data)
    Base.metadata.create_all(bind=engine) # recreates tables from current models


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

user_evidence_problem_association = Table(
    'user_evidence_problem_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user_table.id')),
    Column('evidence_problem_id', Integer, ForeignKey('evidence_problem_table.id'))
)

user_flashlight_problem_association = Table(
    'user_flashlight_problem_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user_table.id')),
    Column('flashlight_problem_id', Integer, ForeignKey('flashlight_problem_table.id'))
)