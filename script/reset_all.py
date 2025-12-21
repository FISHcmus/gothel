"""Dev-only reset: drop and recreate ALL tables (users + reading).

WARNING: This deletes all data.
"""

from model.Base import engine, Base
from model.Question import MultiChoiceQuestionDB, EvidenceProblemDB
from model.User import UserDB
# Import to register tables
from model.ReadingContent import ReadingContentDB

def main() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    main()

