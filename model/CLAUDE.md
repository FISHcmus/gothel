# CLAUDE.md - Database Models

This file provides guidance to Claude Code when working with the database models (`model/`).

## 📝 Maintenance Reminder

**IMPORTANT**: When you modify ANY model file in this directory:
1. ✅ Update this CLAUDE.md immediately
2. ✅ Update directory structure if you add/remove files
3. ✅ Update model documentation sections
4. ✅ Update relationship patterns
5. ✅ Update code examples
6. ✅ Update `DTO/CLAUDE.md` if DTOs need changes
7. ✅ Update `Base.py` association tables if adding relationships

---

## Directory Structure

```
model/
├── CLAUDE.md               # This file - guidance for database models
├── Base.py                 # SQLAlchemy configuration and base classes
├── User.py                 # User model
├── EvidenceProblem.py      # Evidence problem model
├── FlashlightProblem.py    # Flashlight problem model
├── ReadingContent.py       # Reading content model
├── MCQuestion.py           # Multiple choice question model
├── __init__.py             # Package initialization
└── model-design-guild.md   # Original design notes
```

## Database Architecture

**Database**: SQLite (`db_local.db`)
**ORM**: SQLAlchemy
**Session Management**: Dependency injection via `get_db()`

### Base Configuration (`Base.py`)

**Key Components**:
- `engine`: SQLAlchemy engine for SQLite
- `SessionLocal`: Session factory
- `Base`: Declarative base for all models
- `TimestampMixin`: Mixin class providing automatic timestamps
- Association tables for many-to-many relationships

**Important Functions**:
```python
def get_db():
    # Dependency injection for database sessions
    # Use in FastAPI routes with Depends(get_db)

def reset_db():
    # Drops and recreates all tables
    # WARNING: Deletes all data!
    # Use for development/testing only
```

**Association Tables**:
- `user_evidence_problem_association`: Links users with solved evidence problems
- `user_flashlight_problem_association`: Links users with solved flashlight problems

### TimestampMixin

All models that inherit from `TimestampMixin` automatically get:
- `created_at`: DateTime, set on creation
- `updated_at`: DateTime, updated on modification

## Models

### 1. User (`User.py`)

**Table**: `user_table`

**Fields**:
- `id`: Integer, primary key
- `username`: String, unique, indexed
- `hashed_password`: String (never store plain passwords!)
- `role`: String, default "user" (values: "user", "admin")
- `email`: String, unique, indexed, nullable
- `avatar_id`: String, nullable
- `created_at`: DateTime (from TimestampMixin)
- `updated_at`: DateTime (from TimestampMixin)

**Relationships**:
- `evidence_problems_solved`: Many-to-many with `EvidenceProblemDB`
  - Via `user_evidence_problem_association` table
  - Tracks which evidence problems the user has solved
- `flashlight_problems_solved`: Many-to-many with `FlashlightProblemDB`
  - Via `user_flashlight_problem_association` table
  - Tracks which flashlight problems the user has solved

**Properties**:
- `solved_evidence_count`: Returns count of solved evidence problems
- `solved_flashlight_count`: Returns count of solved flashlight problems

**Usage Example**:
```python
from model.User import UserDB
from model.Base import get_db

# Create user
user = UserDB(
    username="john_doe",
    hashed_password=hash_password("secret"),
    role="user"
)
db.add(user)
db.commit()

# Check solved count
print(user.solved_evidence_count)
```

---

### 2. Evidence Problem (`EvidenceProblem.py`)

**Table**: `evidence_problem_table`

**Fields**:
- `id`: Integer, primary key
- `problem_statement`: String, the question asked
- `evidence`: String, the correct evidence text to find
- `options`: JSON (List[str]), answer choices
- `correct_option`: Integer, index of correct answer
- `reading_content`: String, the full reading passage
- `created_at`: DateTime (from TimestampMixin)
- `updated_at`: DateTime (from TimestampMixin)

**Relationships**:
- `solved_by_users`: Many-to-many with `UserDB`
  - Via `user_evidence_problem_association` table
  - Tracks which users have solved this problem

**Usage Example**:
```python
from model.EvidenceProblem import EvidenceProblemDB

problem = EvidenceProblemDB(
    problem_statement="Which statement is supported by the passage?",
    evidence="the key phrase in the text",
    options=["Option A", "Option B", "Option C", "Option D"],
    correct_option=1,  # Index 1 = "Option B"
    reading_content="The full passage text here..."
)
db.add(problem)
db.commit()
```

**Important Notes**:
- `correct_option` is zero-indexed (0 = first option)
- `evidence` contains the exact text users must highlight
- `reading_content` is embedded in the problem (denormalized for simplicity)

---

### 3. Reading Content (`ReadingContent.py`)

**Table**: `reading_content_table`

**Fields**:
- `id`: Integer, primary key
- `content`: String, the reading passage text
- `created_at`: DateTime (from TimestampMixin)
- `updated_at`: DateTime (from TimestampMixin)

**Relationships**:
- Currently none (commented out relationships to MCQuestion and EvidenceProblem)

**Status**:
- This model is currently **not actively used**
- Evidence problems embed reading content directly
- May be refactored in the future to normalize reading content

**Design Note**:
The commented-out relationships suggest a planned architecture where:
- One reading passage can have multiple questions
- One reading passage can have multiple evidence problems
- This would allow reusing reading content across different problems

---

### 4. Multiple Choice Question (`MCQuestion.py`)

**Table**: `multiple_choice_question_table`

**Fields**:
- `id`: Integer, primary key
- `question`: String, the question text
- `choices`: JSON (List[str]), answer options
- `correct_answer`: String, the correct answer text
- `created_at`: DateTime (from TimestampMixin)
- `updated_at`: DateTime (from TimestampMixin)

**Relationships**:
- Currently none (user relationship commented out)

**Status**:
- Model exists but is **not actively used** in current implementation
- Evidence problems are the primary focus
- May be used for future features (Flashlight, Gap-Fill drills)

---

### 5. FlashlightProblem.py (`FlashlightProblem.py`)
**Table**: `flashlight_problem_table`

**Fields**:
- `id`: Integer, primary key
- `problem_statement`: String, the question asked
- `target`: String, the correct target text that user need to find and highlight
- `reading_content`: String, the full reading passage
- `created_at`: DateTime (from TimestampMixin)
- `updated_at`: DateTime (from TimestampMixin)

**Relationships**:
- `solved_by_users`: Many-to-many with `UserDB`
  - Via `user_flashlight_problem_association` table
  - Tracks which users have solved this problem

**Usage Example**:
```python
from model.FlashlightProblem import FlashlightProblemDB

problem = FlashlightProblemDB(
    problem_statement="Find the phrase 'climate change' in the passage",
    target="climate change",
    reading_content="The full passage text here..."
)
db.add(problem)
db.commit()
```

**Important Notes**:
- `target` contains the exact text users must find and highlight
- Unlike EvidenceProblem, there are no multiple choice options
- Typically used with time constraints (15 seconds)
- Reading content is embedded directly (denormalized)



## Relationship Patterns

### Many-to-Many: User ↔ Evidence Problems

**Purpose**: Track which problems each user has solved

**Implementation**:
```python
# In Base.py
user_evidence_problem_association = Table(
    'user_evidence_problem_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user_table.id')),
    Column('evidence_problem_id', Integer, ForeignKey('evidence_problem_table.id'))
)

# In User.py
evidence_problems_solved = relationship(
    "EvidenceProblemDB",
    secondary=user_evidence_problem_association,
    back_populates="solved_by_users",
)

# In EvidenceProblem.py
solved_by_users = relationship(
    "UserDB",
    secondary=user_evidence_problem_association,
    back_populates="evidence_problems_solved",
)
```

**Usage**:
```python
# Mark problem as solved by user
user.evidence_problems_solved.append(problem)
db.commit()

# Get all users who solved a problem
solvers = problem.solved_by_users

# Get all problems solved by user
solved = user.evidence_problems_solved
```

---

### Many-to-Many: User ↔ Flashlight Problems

**Purpose**: Track which flashlight problems each user has solved

**Implementation**:
```python
# In Base.py
user_flashlight_problem_association = Table(
    'user_flashlight_problem_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user_table.id')),
    Column('flashlight_problem_id', Integer, ForeignKey('flashlight_problem_table.id'))
)

# In User.py
flashlight_problems_solved = relationship(
    "FlashlightProblemDB",
    secondary=user_flashlight_problem_association,
    back_populates="solved_by_users",
)

# In FlashlightProblem.py
solved_by_users = relationship(
    "UserDB",
    secondary=user_flashlight_problem_association,
    back_populates="flashlight_problems_solved",
)
```

**Usage**:
```python
# Mark flashlight problem as solved by user
user.flashlight_problems_solved.append(flashlight_problem)
db.commit()

# Get all users who solved a flashlight problem
solvers = flashlight_problem.solved_by_users

# Get all flashlight problems solved by user
solved = user.flashlight_problems_solved

# Get count of solved flashlight problems
count = user.solved_flashlight_count
```

---

## Best Practices

### Creating New Models

1. **Inherit from Base and TimestampMixin**:
   ```python
   class NewModel(Base, TimestampMixin):
       __tablename__ = "new_model_table"
   ```

2. **Use Mapped type hints**:
   ```python
   id: Mapped[int] = Column(Integer, primary_key=True)
   name: Mapped[str] = Column(String, nullable=False)
   ```

3. **Define relationships carefully**:
   - Use `back_populates` for bidirectional relationships
   - Consider cascade behavior for dependent data
   - Use association tables for many-to-many in `Base.py`

4. **Add to Base.py if needed**:
   - Association tables go in `Base.py`
   - Keep foreign key relationships in the model files

### Modifying Models

1. **After changing models, reset the database**:
   ```python
   from model.Base import reset_db
   reset_db()  # WARNING: Deletes all data!
   ```

2. **For production, use migrations** (not currently implemented):
   - Consider using Alembic for database migrations
   - Never use `reset_db()` in production

### Type Checking

Models use `TYPE_CHECKING` to avoid circular imports:
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.User import UserDB
```

This allows type hints without runtime import issues.

---

## Common Queries

### Get Database Session
```python
from model.Base import get_db

# In FastAPI route
@router.get("/endpoint")
def my_route(db: Session = Depends(get_db)):
    # db is automatically managed (opened and closed)
    users = db.query(UserDB).all()
```

### Query Examples
```python
# Get all evidence problems
problems = db.query(EvidenceProblemDB).all()

# Get all flashlight problems
flashlight_problems = db.query(FlashlightProblemDB).all()

# Get user by username
user = db.query(UserDB).filter(UserDB.username == "john").first()

# Get unsolved evidence problems for a user
all_problems = db.query(EvidenceProblemDB).all()
solved_ids = [p.id for p in user.evidence_problems_solved]
unsolved = [p for p in all_problems if p.id not in solved_ids]

# Get unsolved flashlight problems for a user
all_flashlight = db.query(FlashlightProblemDB).all()
solved_flashlight_ids = [p.id for p in user.flashlight_problems_solved]
unsolved_flashlight = [p for p in all_flashlight if p.id not in solved_flashlight_ids]

# Count solved problems
evidence_count = user.solved_evidence_count
flashlight_count = user.solved_flashlight_count
total_count = evidence_count + flashlight_count
```

---

## Database Reset

**Development Only**:
```python
from model.Base import reset_db

# This will DELETE ALL DATA and recreate tables
reset_db()
```

**Warning**: Never use `reset_db()` in production! It drops all tables and data.

For production, implement proper database migrations using Alembic.

---

## Future Considerations

### Normalization Opportunities

Currently, both `EvidenceProblemDB` and `FlashlightProblemDB` embed `reading_content` directly. Future refactoring could:

1. **Extract reading content to separate table**:
   - Reduce duplication if multiple problems share the same passage
   - Easier to manage and update reading materials
   - Both evidence and flashlight problems could reference the same reading passage

2. **Link problems to reading content**:
   ```python
   # In EvidenceProblem.py and FlashlightProblem.py (future)
   reading_content_id = Column(Integer, ForeignKey('reading_content_table.id'))
   reading_content = relationship("ReadingContentDB", back_populates="problems")
   ```

3. **Activate MCQuestion model**:
   - Use for Gap-Fill drill features
   - Link to reading content for consistency

### Track Answer Attempts

Currently, we only track if a problem is solved (for both evidence and flashlight problems). Future enhancement:
- Track incorrect attempts
- Store timestamps of attempts
- For evidence problems: record which incorrect options were selected
- For flashlight problems: record time taken to find the target
- Track number of attempts before success

This would require enhanced association tables with additional fields:
```python
# Future: user_problem_attempt table
class UserProblemAttempt(Base):
    user_id: int
    problem_id: int
    problem_type: str  # 'evidence' or 'flashlight'
    attempt_number: int
    success: bool
    time_taken: float
    selected_option: int | None  # For evidence problems
    timestamp: DateTime
```
