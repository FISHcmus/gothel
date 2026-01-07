# CLAUDE.md - Data Transfer Objects (DTOs)

This file provides guidance to Claude Code when working with DTOs (`DTO/`).

## 📝 Maintenance Reminder

**IMPORTANT**: When you modify ANY DTO file in this directory:
1. ✅ Update this CLAUDE.md immediately
2. ✅ Update directory structure if you add/remove files
3. ✅ Update DTO documentation sections
4. ✅ Update conversion examples
5. ✅ Update validation patterns
6. ✅ Check if corresponding `model/CLAUDE.md` needs updates

---

## Directory Structure

```
DTO/
├── CLAUDE.md               # This file - guidance for DTOs
├── EvidenceProblem.py      # Evidence problem DTOs
├── FlashlightProblem.py    # Flashlight problem DTOs
├── User.py                 # User DTOs
├── MCQuestion.py           # Multiple choice question DTOs
├── ReadingContent.py       # Reading content DTOs
└── __init__.py             # Package initialization
```

## What are DTOs?

**Data Transfer Objects (DTOs)** are Pydantic models that define the shape of data moving in and out of the API.

**Purpose**:
- **Validation**: Ensure incoming data meets requirements
- **Serialization**: Convert Python objects to JSON responses
- **Documentation**: Auto-generate OpenAPI/Swagger docs
- **Type Safety**: Provide IDE autocomplete and type checking
- **Security**: Control which fields are exposed to clients

**Framework**: Pydantic BaseModel

---

## DTO Patterns

### Two-DTO Pattern

Each resource typically has **two DTOs**:

1. **Input DTO** (e.g., `EvidenceProblemDTO`)
   - Used for **creating** or **updating** resources
   - Contains only fields the client can set
   - No `id` field (server generates it)
   - No computed fields

2. **Response DTO** (e.g., `EvidenceProblemResponseDTO`)
   - Used for **returning** data to the client
   - Includes `id` and all resource fields
   - May include computed/derived fields
   - Uses `Config.from_attributes = True` to convert from SQLAlchemy models

### Example Pattern

```python
# Input DTO - for POST/PUT requests
class ResourceDTO(BaseModel):
    field1: str
    field2: int

# Response DTO - for GET responses
class ResourceResponseDTO(BaseModel):
    id: int              # Server-generated
    field1: str
    field2: int

    class Config:
        from_attributes = True  # Allow SQLAlchemy model conversion
```

---

## DTOs

### 1. Evidence Problem (`EvidenceProblem.py`)

#### EvidenceProblemDTO (Input)

**Purpose**: Create or update evidence problems

**Fields**:
- `problem_statement`: str - The question asked
- `reading_content`: str - The full reading passage
- `evidence`: str - The correct evidence text to find
- `options`: list[str] - Answer choices
- `correct_option`: int - Index of correct answer (0-based)

**Usage**:
```python
# POST /evidence_problem/create
{
    "problem_statement": "Which statement is supported?",
    "reading_content": "The full passage...",
    "evidence": "key phrase in text",
    "options": ["A", "B", "C", "D"],
    "correct_option": 1
}
```

#### EvidenceProblemResponseDTO (Output)

**Purpose**: Return evidence problem data to client

**Fields**: All fields from input DTO plus:
- `id`: int - Database primary key

**Configuration**:
- `from_attributes = True` - Allows conversion from `EvidenceProblemDB` model

**Usage**:
```python
from model.EvidenceProblem import EvidenceProblemDB
from DTO.EvidenceProblem import EvidenceProblemResponseDTO

# In route
problem_db = db.query(EvidenceProblemDB).first()
return EvidenceProblemResponseDTO.from_orm(problem_db)
```

---

### 2. User (`User.py`)

#### UserCreateDTO (Input)

**Purpose**: Register new users

**Fields**:
- `username`: str - Unique username
- `password`: str - Plain text password (will be hashed server-side)

**Security Note**:
- Password is **never** stored in plain text
- Server hashes password before saving to database
- Never include password in response DTOs

**Usage**:
```python
# POST /register
{
    "username": "john_doe",
    "password": "secret123"
}
```

#### UserResponseDTO (Output)

**Purpose**: Return user data to client

**Fields**:
- `username`: str - The user's username
- `role`: Literal["user", "admin"] - User's role
- `avatar_id`: str | None - Avatar identifier (optional)
- `email`: str | None - User email (optional)

**Security Notes**:
- **No password fields** - Never expose passwords or hashes
- **No id** - User ID not exposed to prevent enumeration attacks
- Role is exposed for UI permission logic

**Configuration**:
- `from_attributes = True` - Convert from `UserDB` model

**Usage**:
```python
# GET /users/me response
{
    "username": "john_doe",
    "role": "user",
    "avatar_id": null,
    "email": "john@example.com"
}
```

---

### 3. Multiple Choice Question (`MCQuestion.py`)

#### MCQuestionDTO (Input)

**Purpose**: Create multiple choice questions

**Fields**:
- `question`: str - The question text
- `options`: list[str] - Answer options
- `correct_option`: int - Index of correct answer (0-based)

**Status**: Currently not actively used (placeholder for future features)

**Usage**:
```python
# Future POST endpoint
{
    "question": "What is the capital of France?",
    "options": ["London", "Paris", "Berlin", "Madrid"],
    "correct_option": 1
}
```

#### MCQuestionResponseDTO (Output)

**Purpose**: Return MC question data

**Fields**: All input fields plus:
- `id`: int - Database ID

**Configuration**:
- `from_attributes = True`

---

### 4. Reading Content (`ReadingContent.py`)

#### ReadingContentDTO (Input)

**Purpose**: Create or update reading passages

**Fields**:
- `content`: str - The reading passage text

**Status**: Currently not actively used (evidence problems embed content directly)

**Usage**:
```python
# Future POST endpoint
{
    "content": "The full reading passage goes here..."
}
```

#### ReadingContentResponseDTO (Output)

**Purpose**: Return reading content data

**Fields**: Input fields plus:
- `id`: int - Database ID

**Configuration**:
- `from_attributes = True`

---

### 5. Flashlight Problem (`FlashlightProblem.py`)

#### FlashlightProblemDTO (Input)

**Purpose**: Create flashlight drill problems

**Fields**:
- `problem_statement`: str - The instruction/question (e.g., "Find the phrase 'climate change'")
- `target`: str - The exact text users must find and highlight
- `reading_content`: str - The full reading passage

**Usage**:
```python
# POST /flashlight_problem/create
{
    "problem_statement": "Find the phrase 'climate change' in the passage",
    "target": "climate change",
    "reading_content": "The full passage text here..."
}
```

**Key Differences from EvidenceProblem**:
- No `evidence` field (uses `target` instead)
- No `options` field (no multiple choice)
- No `correct_option` field
- Simpler structure focused on text-finding drill

#### FlashlightProblemResponseDTO (Output)

**Purpose**: Return flashlight problem data to client

**Fields**: All fields from input DTO plus:
- `id`: int - Database primary key

**Configuration**:
- `from_attributes = True` - Allows conversion from `FlashlightProblemDB` model

**Usage**:
```python
from model.FlashlightProblem import FlashlightProblemDB
from DTO.FlashlightProblem import FlashlightProblemResponseDTO

# In route
problem_db = db.query(FlashlightProblemDB).first()
return FlashlightProblemResponseDTO.model_validate(problem_db)
```

**Example Response**:
```json
{
    "id": 1,
    "problem_statement": "Find the phrase 'climate change' in the passage",
    "target": "climate change",
    "reading_content": "Scientists have studied climate change for decades..."
}
```

---

## Converting Between Models and DTOs

### Database Model → Response DTO

**Using Pydantic v2**:
```python
from model.EvidenceProblem import EvidenceProblemDB
from DTO.EvidenceProblem import EvidenceProblemResponseDTO

# Query database
problem_db = db.query(EvidenceProblemDB).first()

# Convert to DTO
problem_dto = EvidenceProblemResponseDTO.model_validate(problem_db)

# Or in FastAPI route (automatic)
@router.get("/problem/{id}", response_model=EvidenceProblemResponseDTO)
def get_problem(id: int, db: Session = Depends(get_db)):
    return db.query(EvidenceProblemDB).filter_by(id=id).first()
    # FastAPI automatically converts to DTO
```

### Input DTO → Database Model

```python
from DTO.EvidenceProblem import EvidenceProblemDTO
from model.EvidenceProblem import EvidenceProblemDB

# Receive input
input_dto = EvidenceProblemDTO(
    problem_statement="Question here",
    reading_content="Passage here",
    evidence="Evidence text",
    options=["A", "B", "C"],
    correct_option=0
)

# Create database model
problem_db = EvidenceProblemDB(
    problem_statement=input_dto.problem_statement,
    reading_content=input_dto.reading_content,
    evidence=input_dto.evidence,
    options=input_dto.options,
    correct_option=input_dto.correct_option
)

# Or use .model_dump()
problem_db = EvidenceProblemDB(**input_dto.model_dump())

# Save to database
db.add(problem_db)
db.commit()
db.refresh(problem_db)
```

---

## Best Practices

### Creating New DTOs

1. **Follow the two-DTO pattern**:
   ```python
   class NewResourceDTO(BaseModel):
       # Input fields only
       field1: str

   class NewResourceResponseDTO(BaseModel):
       id: int
       field1: str

       class Config:
           from_attributes = True
   ```

2. **Use type hints**:
   - `str`, `int`, `bool` for required fields
   - `str | None` or `Optional[str]` for optional fields
   - `list[str]`, `dict[str, int]` for collections
   - `Literal["option1", "option2"]` for enums

3. **Validate data**:
   ```python
   from pydantic import Field, validator

   class UserDTO(BaseModel):
       username: str = Field(min_length=3, max_length=50)
       age: int = Field(ge=0, le=120)

       @validator('username')
       def username_alphanumeric(cls, v):
           assert v.isalnum(), 'must be alphanumeric'
           return v
   ```

4. **Document fields**:
   ```python
   class UserDTO(BaseModel):
       username: str = Field(description="Unique username, 3-50 chars")
       email: str = Field(description="Valid email address")
   ```

### Security Considerations

1. **Never expose sensitive data**:
   - ❌ Password fields in response DTOs
   - ❌ Password hashes
   - ❌ Internal IDs that could enable attacks
   - ❌ System configuration

2. **Validate all inputs**:
   - Use Pydantic validators
   - Set min/max lengths
   - Use regex patterns for formats
   - Sanitize user input

3. **Use Literal types for enums**:
   ```python
   role: Literal["user", "admin"]  # Only these values allowed
   ```

### Response Model Usage

**In FastAPI routes**:
```python
@router.post("/create", response_model=EvidenceProblemResponseDTO)
async def create_problem(
    data: EvidenceProblemDTO,
    db: Session = Depends(get_db)
):
    # Create and save
    problem = EvidenceProblemDB(**data.model_dump())
    db.add(problem)
    db.commit()
    db.refresh(problem)

    # Return is automatically converted to response DTO
    return problem
```

**FastAPI automatically**:
- Validates input against `EvidenceProblemDTO`
- Converts output to `EvidenceProblemResponseDTO`
- Generates OpenAPI documentation
- Returns JSON response

---

## Common Patterns

### Nested DTOs

```python
from DTO.User import UserResponseDTO
from DTO.EvidenceProblem import EvidenceProblemResponseDTO

class DetailedProblemDTO(BaseModel):
    """Problem with solver information"""
    id: int
    problem_statement: str
    solved_by: list[UserResponseDTO]  # Nested DTOs

    class Config:
        from_attributes = True
```

### Partial Updates

```python
from pydantic import BaseModel

class ProblemUpdateDTO(BaseModel):
    """All fields optional for PATCH requests"""
    problem_statement: str | None = None
    options: list[str] | None = None

    class Config:
        # Only include fields that were actually set
        exclude_unset = True
```

### List Responses

```python
# Return list of DTOs
@router.get("/all", response_model=list[EvidenceProblemResponseDTO])
def get_all_problems(db: Session = Depends(get_db)):
    return db.query(EvidenceProblemDB).all()
```

---

## Pydantic Configuration

### Config Options

Common `Config` class settings:

```python
class MyDTO(BaseModel):
    field: str

    class Config:
        # Convert from SQLAlchemy models
        from_attributes = True

        # Only include set fields in .model_dump()
        exclude_unset = True

        # Exclude None values
        exclude_none = True

        # Use enum values instead of names
        use_enum_values = True

        # Allow population by field name or alias
        populate_by_name = True
```

---

## Future DTOs

Future models that may need DTOs:

### GapFill Problem (Planned)

When the Gap-Fill drill feature is implemented, create:
- `GapFillProblemDTO` (input)
- `GapFillProblemResponseDTO` (output)

Follow the two-DTO pattern and document in this CLAUDE.md.

---

## Troubleshooting

### Common Issues

1. **"from_attributes not found"**:
   - Using Pydantic v1? Use `orm_mode = True` instead
   - Update to Pydantic v2 for `from_attributes`

2. **"field required"**:
   - Make field optional: `field: str | None = None`
   - Or provide default: `field: str = "default"`

3. **Circular import errors**:
   - Use `from __future__ import annotations`
   - Use string type hints: `"UserResponseDTO"`
   - Move imports inside functions if needed

4. **Validation errors**:
   - Check field types match data
   - Use `.model_dump()` not `.dict()` in Pydantic v2
   - Enable debug mode for detailed errors

---

## Testing DTOs

```python
from DTO.EvidenceProblem import EvidenceProblemDTO

# Valid data
valid_data = {
    "problem_statement": "Question",
    "reading_content": "Passage",
    "evidence": "Evidence",
    "options": ["A", "B"],
    "correct_option": 0
}

# Create DTO - will validate
dto = EvidenceProblemDTO(**valid_data)

# Access fields
assert dto.problem_statement == "Question"

# Convert to dict
data_dict = dto.model_dump()

# Convert to JSON
json_str = dto.model_dump_json()
```
