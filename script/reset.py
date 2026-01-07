import sys
import argparse
from sqlalchemy import text
from model.Base import engine, Base

# Import all models so they are registered with Base.metadata
# (Add any other models you have in your project here)
from model.MCQuestion import MultiChoiceQuestionDB
from model.EvidenceProblem import EvidenceProblemDB
from model.FlashlightProblem import FlashlightProblemDB
from model.User import UserDB
from model.ReadingContent import ReadingContentDB


def reset_single_table(table_name: str) -> None:
    """
    Resets a single table by dropping and recreating it.
    """
    # Base.metadata.tables is a dictionary of 'tablename' -> Table object
    # Note: SQLAlchemy usually stores table names in the case defined in __tablename__
    table = Base.metadata.tables.get(table_name)

    if table is None:
        print(f"Error: Table '{table_name}' not found in metadata.")
        print("Available tables:", ", ".join(Base.metadata.tables.keys()))
        return

    print(f"Resetting table: {table_name}...")

    try:
        # Drop the specific table (ignore if it doesn't exist)
        table.drop(bind=engine, checkfirst=True)
    except Exception as e:
        print(f"Warning dropping table '{table_name}': {e}")

    try:
        # Create the specific table
        table.create(bind=engine, checkfirst=True)
        print(f"Successfully reset table '{table_name}'.")
    except Exception as e:
        print(f"Error creating table '{table_name}': {e}")


def main():
    parser = argparse.ArgumentParser(description="Reset a single database table.")
    parser.add_argument("table_name", help="The name of the table to reset (e.g., user_table)")

    args = parser.parse_args()

    reset_single_table(args.table_name)


if __name__ == "__main__":
    main()
