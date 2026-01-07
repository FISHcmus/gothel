# CLAUDE.md - Utility Scripts

This file provides guidance to Claude Code when working with utility scripts (`script/`).

## 📝 Maintenance Reminder

**IMPORTANT**: When you modify ANY script in this directory:
1. ✅ Update this CLAUDE.md immediately
2. ✅ Update directory structure if you add/remove files
3. ✅ Update script documentation
4. ✅ Update usage examples
5. ✅ Test the script before committing

---

## Directory Structure

```
script/
├── CLAUDE.md                    # This file - guidance for utility scripts
├── create_admin.py              # Create default admin user
├── user_gen.py                  # Generate fake users for testing
├── evidence_data_gen.py         # Generate fake evidence problems
├── gen_real_evidence_data.py    # Insert real evidence problems
├── gen_real_flashlight_data.py  # Insert real flashlight drill problems
├── reset.py                     # Reset a single database table
├── reset_all.py                 # Reset all database tables
├── db_local.db                  # Local database file (should be ignored?)
└── __init__.py                  # Package initialization
```

## Overview

The `script/` directory contains utility scripts for development, testing, and database management. These scripts are **development-only** tools and should never be run in production.

**⚠️ WARNING**: Many of these scripts delete data! Use with caution.

---

## Scripts

### 1. Database Reset Scripts

#### reset_all.py

**Purpose**: Drop and recreate ALL database tables (complete database reset)

**Usage**:
```bash
python -m script.reset_all
```

**What it does**:
- Drops all tables in the database
- Recreates all tables from model definitions
- **Deletes ALL data** (users, problems, progress, etc.)

**Use cases**:
- Development database cleanup
- After model schema changes
- Starting fresh with empty database

**⚠️ WARNING**: This deletes ALL data! Never use in production.

**Code Overview**:
```python
from model.Base import engine, Base

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
```

---

#### reset.py

**Purpose**: Reset a single database table (drop and recreate)

**Usage**:
```bash
python -m script.reset <table_name>

# Examples:
python -m script.reset user_table
python -m script.reset evidence_problem_table
python -m script.reset flashlight_problem_table
```

**What it does**:
- Drops the specified table
- Recreates the table from model definition
- **Deletes all data in that table only**
- Lists available tables if table not found

**Use cases**:
- Resetting specific table without affecting others
- Testing table-specific migrations
- Clearing test data from one table

**Arguments**:
- `table_name`: Name of the table to reset (required)

**Available Tables**:
- `user_table`
- `evidence_problem_table`
- `flashlight_problem_table`
- `reading_content_table`
- `multiple_choice_question_table`
- `user_evidence_problem_association`
- `user_flashlight_problem_association`

---

### 2. User Management Scripts

#### create_admin.py

**Purpose**: Create a default admin user if it doesn't exist

**Usage**:
```bash
python -m script.create_admin
```

**Default Credentials**:
- Username: `admin`
- Password: `password`
- Role: `admin`

**What it does**:
- Checks if admin user already exists
- If not, creates admin user with hashed password
- Safe to run multiple times (idempotent)

**Use cases**:
- Initial setup after database reset
- Creating admin account for testing
- Quick admin access for development

**⚠️ Security Note**: Change the default password in production!

**Code Overview**:
```python
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

def create_admin(session: Session) -> None:
    existing = session.query(UserDB).filter(UserDB.username == ADMIN_USERNAME).first()
    if existing:
        return
    hashed = get_password_hash(ADMIN_PASSWORD)
    admin = UserDB(username=ADMIN_USERNAME, hashed_password=hashed, role="admin")
    session.add(admin)
    session.commit()
```

---

#### user_gen.py

**Purpose**: Generate fake users for testing

**Usage**:
```bash
python -m script.user_gen
```

**What it does**:
- Resets the `user_table` (deletes all users!)
- Creates a custom user: `nhannht` / `password` (role: user)
- Generates 10 fake users using Faker library
- Each fake user gets random username and password

**Use cases**:
- Populating database with test users
- Testing user-related features
- Load testing with multiple users

**Dependencies**:
- `faker`: Python library for generating fake data

**Customization**:
Edit the script to change:
- Number of users: `create_fake_users(db, 10)` → `create_fake_users(db, 50)`
- Custom user credentials
- User roles

---

### 3. Data Generation Scripts

#### evidence_data_gen.py

**Purpose**: Generate fake evidence problems using Faker

**Usage**:
```bash
python -m script.evidence_data_gen
```

**What it does**:
- Creates 10 fake evidence problems
- Uses Faker to generate random paragraphs and sentences
- Randomly selects a word from paragraph as evidence
- **Does NOT reset table** (adds to existing data)

**Use cases**:
- Quick test data generation
- Development testing
- Prototype testing

**Note**: Generated data is random and not suitable for real testing of evidence-finding logic.

**Code Overview**:
```python
def create_fake_problems(session: Session, count: int = 10) -> None:
    for _ in range(count):
        paragraph = fake.unique.paragraph()
        evidence = random.choice(paragraph.split(' '))
        problem = EvidenceProblemDB(
            problem_statement=fake.sentence(),
            reading_content=paragraph,
            evidence=evidence
        )
        session.add(problem)
    session.commit()
```

---

#### gen_real_evidence_data.py

**Purpose**: Insert real, curated evidence problems for testing

**Usage**:
```bash
python -m script.gen_real_evidence_data
```

**What it does**:
- Resets the `evidence_problem_table` (deletes all evidence problems!)
- Inserts 5 hand-crafted evidence problems
- Problems have realistic content, questions, options, and evidence
- Skip duplicates if problem already exists

**Use cases**:
- Creating quality test data
- Demonstrating app functionality
- Testing evidence-finding logic with real scenarios

**Problems Included**:
1. Great Pyramid of Giza (blocks count)
2. Photosynthesis (light energy conversion)
3. Apollo 11 (first person on moon)
4. Honey bees (nest construction material)
5. The Internet (TCP/IP protocol)

**Customization**:
Edit the `problems_data` list in the script to add more problems.

**Example Problem Structure**:
```python
{
    "reading_content": "Full passage text...",
    "problem_statement": "Question?",
    "options": ["A", "B", "C", "D"],
    "correct_option": 1,  # 0-indexed
    "evidence": "exact text to find"
}
```

---

#### gen_real_flashlight_data.py

**Purpose**: Insert real, curated flashlight drill problems for testing

**Usage**:
```bash
python -m script.gen_real_flashlight_data
```

**What it does**:
- Resets the `flashlight_problem_table` (deletes all flashlight problems!)
- Inserts 10 hand-crafted flashlight drill problems
- Problems have realistic content with specific target words/phrases to find
- Covers different difficulty levels (single words, phrases, numbers, names)
- Skip duplicates if problem already exists

**Use cases**:
- Creating quality test data for flashlight drills
- Demonstrating flashlight drill functionality
- Testing rapid scanning and keyword location features

**Problems Included**:
1. Climate change (phrase)
2. Apollo 11 - 1969 (number)
3. Photosynthesis (single word)
4. Artificial intelligence (phrase)
5. Marie Curie (name)
6. Renaissance period (historical term)
7. Biodiversity (single word)
8. Human skeleton - 206 bones (number)
9. Great Wall of China (landmark name)
10. Democracy (concept word)

**Customization**:
Edit the `problems_data` list in the script to add more problems.

**Example Problem Structure**:
```python
{
    "problem_statement": "Find the phrase 'climate change' in the passage",
    "target": "climate change",
    "reading_content": "Scientists have studied climate change for decades..."
}
```

---

## Common Workflows

### Starting Fresh (New Development Environment)

```bash
# 1. Reset all tables
python -m script.reset_all

# 2. Create admin user
python -m script.create_admin

# 3. Generate test users
python -m script.user_gen

# 4. Add real evidence problems
python -m script.gen_real_evidence_data

# 5. Add real flashlight drill problems
python -m script.gen_real_flashlight_data
```

### After Model Schema Changes

```bash
# Option 1: Reset all tables
python -m script.reset_all

# Option 2: Reset only affected tables
python -m script.reset evidence_problem_table
python -m script.reset user_table
```

### Quick Test Data Setup

```bash
# Reset and populate with all test data
python -m script.reset_all
python -m script.create_admin
python -m script.gen_real_evidence_data
python -m script.gen_real_flashlight_data
```

---

## Best Practices

### 1. Creating New Data Generation Scripts

When creating new data generation scripts:

```python
# script/new_data_gen.py
from sqlalchemy.orm import Session
from model.Base import get_db
from model.NewModel import NewModelDB
from script.reset import reset_single_table

def create_new_data(session: Session, count: int = 10) -> None:
    """Generate sample data for NewModel."""
    for _ in range(count):
        item = NewModelDB(
            field1="value1",
            field2="value2"
        )
        session.add(item)
    session.commit()

if __name__ == "__main__":
    db_gen = get_db()
    db = next(db_gen)
    try:
        # Optionally reset table first
        # reset_single_table("new_model_table")
        create_new_data(db, 10)
        print("Data generation completed!")
    finally:
        db_gen.close()
```

### 2. Database Session Management

Always use this pattern:

```python
if __name__ == "__main__":
    db_gen = get_db()
    db = next(db_gen)
    try:
        # Your operations here
        pass
    finally:
        db_gen.close()
```

This ensures:
- Database session is properly opened
- Session is closed even if errors occur
- No connection leaks

### 3. Idempotent Scripts

Make scripts safe to run multiple times:

```python
# Check if item exists before creating
existing = session.query(Model).filter(Model.field == value).first()
if existing:
    print(f"Already exists, skipping...")
    return

# Create new item
item = Model(field=value)
session.add(item)
session.commit()
```

### 4. User Feedback

Provide clear output:

```python
print(f"Creating {count} items...")
# ... creation logic ...
print(f"Successfully created {count} items!")
```

---

## Adding New Scripts

### Example: Flashlight Problem Data Generation (Implemented)

The `script/gen_real_flashlight_data.py` is a good example of how to create new data generation scripts:

**Key Features**:
- Resets the table first using `reset_single_table()`
- Defines problems_data as a list of dictionaries
- Checks for duplicates before inserting
- Uses proper session management with try/finally
- Provides clear console output
- Follows the established pattern from `gen_real_evidence_data.py`

**When creating new data generation scripts**:
1. Follow this pattern (see `gen_real_flashlight_data.py` for reference)
2. Use `reset_single_table()` if you want to clear existing data
3. Implement duplicate checking with `.filter().first()`
4. Add console output for user feedback
5. Update this CLAUDE.md with documentation

### For Future Features (GapFill, etc.)

Create `script/gen_real_gapfill_data.py` following the same pattern:

```python
from sqlalchemy.orm import Session
from model.Base import get_db
from model.GapFill import GapFillDB
from script.reset import reset_single_table

def create_real_gapfill_problems(session: Session) -> None:
    """Generate sample gap-fill problems."""
    problems_data = [
        {
            "reading_content": "Passage with [GAP] to fill...",
            "correct_answer": "answer",
            "options": ["answer", "wrong1", "wrong2"]
        },
        # Add more problems...
    ]

    for p_data in problems_data:
        exists = session.query(GapFillDB).filter(
            GapFillDB.reading_content == p_data["reading_content"]
        ).first()

        if not exists:
            problem = GapFillDB(**p_data)
            session.add(problem)
            print(f"Added: Gap-fill problem")
        else:
            print(f"Skipped duplicate")

    session.commit()
    print("Done!")

if __name__ == "__main__":
    db_gen = get_db()
    db = next(db_gen)
    try:
        reset_single_table("gapfill_table")
        create_real_gapfill_problems(db)
    finally:
        db_gen.close()
```

Then update this CLAUDE.md with the new script documentation.

---

## Dependencies

Scripts use these Python libraries:

- **faker**: Generate fake data (usernames, paragraphs, etc.)
  - Install: `uv add --group dev faker` or `pip install faker`
- **sqlalchemy**: Database ORM (already in project)
- **argparse**: Command-line argument parsing (built-in)

---

## Troubleshooting

### Common Issues

**1. "Table not found" error**
```bash
# List available tables
python -m script.reset invalid_name
# Output: Available tables: user_table, evidence_problem_table, ...
```

**2. "Unique constraint violation"**
- Script trying to create duplicate data
- Reset the table first: `python -m script.reset <table_name>`

**3. "Session is closed" error**
- Database session management issue
- Ensure you're using the try/finally pattern

**4. Import errors**
- Make sure you're running from project root
- Use `python -m script.scriptname` not `python script/scriptname.py`

**5. Faker generates duplicate data**
- Use `fake.unique.method()` instead of `fake.method()`
- Or handle duplicates with existence checks

**6. "Foreign key... could not find table" error**
- Error: `NoReferencedTableError: Foreign key associated with column '...' could not find table '...'`
- **Root cause**: New model not imported in `model/__init__.py` or `script/reset.py`
- **Fix**:
  1. Add import to `model/__init__.py`: `from model.NewModel import NewModelDB`
  2. Add import to `script/reset.py` (if using reset functions)
  3. Clear Python cache: `find . -type d -name __pycache__ -exec rm -rf {} +`
  4. Run script again

**7. "no such table" error when running data generation**
- Table doesn't exist in database yet
- **Fix**: The script should call `reset_single_table()` which creates the table
- Make sure the model is imported in `script/reset.py`
- The script gets a fresh DB session AFTER resetting the table

---

## Security Warnings

### ⚠️ Production Safety

**NEVER** run these scripts in production:
- They delete data
- They use default passwords
- They are for development only

### Default Credentials

Scripts use insecure default credentials:
- Admin: `admin` / `password`
- Custom user: `nhannht` / `password`

**Always change these in production!**

---

## File: db_local.db

**Status**: This file should probably be in `.gitignore`

The `db_local.db` file in the script directory appears to be a leftover or test database file.

**Recommendation**:
- The main database should be at project root: `/db_local.db`
- Script directory should not contain database files
- Add `script/db_local.db` to `.gitignore` if not already

---

## Quick Reference

| Task | Command |
|------|---------|
| Reset all tables | `python -m script.reset_all` |
| Reset one table | `python -m script.reset <table_name>` |
| Create admin | `python -m script.create_admin` |
| Generate users | `python -m script.user_gen` |
| Generate fake evidence problems | `python -m script.evidence_data_gen` |
| Generate real evidence problems | `python -m script.gen_real_evidence_data` |
| Generate real flashlight problems | `python -m script.gen_real_flashlight_data` |
| Fresh setup | Reset all → Create admin → Gen users → Gen all data |
