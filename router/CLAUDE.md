# CLAUDE.md - API Routers

This file provides guidance to Claude Code when working with API routers (`router/`).

## 📝 Maintenance Reminder

**IMPORTANT**: When you modify ANY router file in this directory:
1. ✅ Update this CLAUDE.md immediately
2. ✅ Update directory structure if you add/remove files
3. ✅ Update endpoint documentation
4. ✅ Update route patterns and examples
5. ✅ Update `main.py` if adding new routers
6. ✅ Check if corresponding `model/CLAUDE.md` or `DTO/CLAUDE.md` needs updates

---

## Directory Structure

```
router/
├── CLAUDE.md               # This file - guidance for routers
├── EvidenceProblem.py      # Evidence problem endpoints
├── FlashlightProblem.py    # Flashlight problem endpoints
├── User.py                 # Authentication & user endpoints
├── ReadingContent.py       # Reading content endpoints
├── MCQuestion.py           # Multiple choice question endpoints (placeholder)
└── __init__.py             # Package initialization
```

## Overview

Routers define FastAPI endpoint groups. Each router handles a specific resource type and is registered in `main.py` using `app.include_router()`.

## Architecture

### Router Pattern

Each router file follows this structure:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from DTO.Resource import ResourceDTO, ResourceResponseDTO
from model.Resource import ResourceDB
from model.Base import get_db
from auth.auth import get_current_user, require_admin

# Create router with optional prefix
router = APIRouter(prefix="/resource")

# Define endpoints
@router.get("/endpoint", response_model=ResourceResponseDTO)
async def endpoint_name(db: Session = Depends(get_db)):
    # Implementation
    pass
```

### Key Components

- **APIRouter**: Creates a router instance with optional prefix
- **Depends(get_db)**: Dependency injection for database sessions
- **Depends(get_current_user)**: Requires authenticated user
- **Depends(require_admin)**: Requires admin role
- **response_model**: Pydantic DTO for response validation

---

## Routers

### 1. Evidence Problem (`EvidenceProblem.py`)

**Prefix**: `/evidence_problem`

**Purpose**: CRUD operations and user tracking for evidence problems

#### Admin Endpoints (require authentication + admin role)

**POST /create**
- **Auth**: Admin required
- **Input**: `EvidenceProblemDTO`
- **Output**: `EvidenceProblemResponseDTO`
- **Purpose**: Create new evidence problem
- **Example**:
```python
@router.post("/create", response_model=EvidenceProblemResponseDTO)
async def create_reading_content(
    input_data: EvidenceProblemDTO,
    admin: UserDB = Depends(require_admin),
    db: Session = Depends(get_db)
)
```

**POST /delete**
- **Auth**: Admin required
- **Input**: `problem_id` (query param)
- **Output**: `{"ok": bool, "id": int}`
- **Purpose**: Delete evidence problem

**POST /update**
- **Auth**: Admin required
- **Input**: `EvidenceProblemDTO` + `problem_id`
- **Output**: `EvidenceProblemResponseDTO`
- **Purpose**: Update existing problem

#### Public Endpoints

**GET /all**
- **Auth**: None
- **Query Params**: `page` (int), `page_size` (int, max 200)
- **Output**: `List[EvidenceProblemResponseDTO]`
- **Purpose**: Get paginated list of all problems
- **Default**: page=0, page_size=50

**GET /get/{problem_id}**
- **Auth**: None
- **Path Param**: `problem_id` (int)
- **Output**: `EvidenceProblemResponseDTO`
- **Purpose**: Get single problem by ID
- **Error**: 404 if not found

**GET /search**
- **Auth**: None
- **Query Params**:
  - `q` (str, optional): Search query
  - `problem_id` (int, optional): Filter by ID
  - `limit` (int, max 200): Results limit
  - `offset` (int): Pagination offset
- **Output**: `List[EvidenceProblemResponseDTO]`
- **Purpose**: Search problems by content/statement/evidence

#### User Progress Endpoints (require authentication)

**POST /solved_by_user**
- **Auth**: User required
- **Input**: `question_id` (query param)
- **Output**: `{"solved": bool, "user_id": int, "problem_id": int}`
- **Purpose**: Mark problem as solved by current user
- **Note**: Updates both sides of many-to-many relationship

**POST /reset_by_user**
- **Auth**: User required
- **Input**: `question_id` (query param)
- **Output**: `{"solved": bool, "user_id": int, "problem_id": int}`
- **Purpose**: Mark problem as unsolved (reset progress)

**GET /is_solved_by_user**
- **Auth**: User required
- **Input**: `problem_id` (query param)
- **Output**: `{"solved": bool}`
- **Purpose**: Check if user solved specific problem

**GET /get_all_problems_solved_by_user**
- **Auth**: User required
- **Output**: `List[EvidenceProblemResponseDTO]`
- **Purpose**: Get all problems solved by current user

**GET /get_user_track_status**
- **Auth**: User required
- **Output**: `{"total_problems": int, "solved_problems": int, "unsolved_problems": int}`
- **Purpose**: Get user's progress summary

---

### 2. User (`User.py`)

**Prefix**: None (uses default)

**Purpose**: Authentication and user management

#### Authentication Endpoints

**POST /token**
- **Auth**: None (OAuth2 form)
- **Input**: `OAuth2PasswordRequestForm` (username, password)
- **Output**: `Token` (access_token, token_type)
- **Purpose**: Login and get JWT token
- **Error**: 401 if credentials incorrect
- **Token Expiry**: Configured via `ACCESS_TOKEN_EXPIRE_MINUTES`

**POST /register**
- **Auth**: None
- **Input**: `UserCreateDTO` (username, password)
- **Output**: `UserResponseDTO`
- **Purpose**: Register new user
- **Error**: 400 if username exists
- **Security**: Password is hashed before storage

**GET /users/me**
- **Auth**: User required
- **Output**: `UserResponseDTO`
- **Purpose**: Get current authenticated user's info

---

### 3. Reading Content (`ReadingContent.py`)

**Prefix**: None (uses `/reading_content` in endpoint path)

**Purpose**: Manage reading passages (currently minimal implementation)

**Status**: Partially implemented, not actively used

#### Admin Endpoints

**POST /reading_content/create**
- **Auth**: Admin required
- **Input**: `ReadingContentDTO`
- **Output**: `ReadingContentResponseDTO`
- **Purpose**: Create new reading passage
- **Note**: Not currently used since problems embed content directly

---

### 4. Flashlight Problem (`FlashlightProblem.py`)

**Prefix**: `/flashlight_problem`

**Purpose**: CRUD operations and user tracking for flashlight drill problems

Flashlight drills require users to find and highlight specific target text within a reading passage, typically under time pressure (15 seconds). This exercises rapid scanning and keyword location skills.

#### Admin Endpoints (require authentication + admin role)

**POST /create**
- **Auth**: Admin required
- **Input**: `FlashlightProblemDTO`
- **Output**: `FlashlightProblemResponseDTO`
- **Purpose**: Create new flashlight problem

**POST /delete**
- **Auth**: Admin required
- **Input**: `problem_id` (query param)
- **Output**: `{"ok": bool, "id": int}`
- **Purpose**: Delete flashlight problem

**POST /update**
- **Auth**: Admin required
- **Input**: `FlashlightProblemDTO` + `problem_id`
- **Output**: `FlashlightProblemResponseDTO`
- **Purpose**: Update existing flashlight problem

#### Public Endpoints

**GET /all**
- **Auth**: None
- **Query Params**: `page` (int), `page_size` (int, max 200)
- **Output**: `List[FlashlightProblemResponseDTO]`
- **Purpose**: Get paginated list of all flashlight problems

**GET /get/{problem_id}**
- **Auth**: None
- **Path Param**: `problem_id` (int)
- **Output**: `FlashlightProblemResponseDTO`
- **Purpose**: Get single flashlight problem by ID

**GET /search**
- **Auth**: None
- **Query Params**:
  - `q` (str, optional): Search in problem_statement, target, or reading_content
  - `problem_id` (int, optional): Filter by ID
  - `limit` (int, max 200): Results limit
  - `offset` (int): Pagination offset
- **Output**: `List[FlashlightProblemResponseDTO]`
- **Purpose**: Search flashlight problems

#### User Progress Endpoints (require authentication)

**POST /solved_by_user**
- **Auth**: User required
- **Input**: `question_id` (query param)
- **Output**: `{"solved": bool, "user_id": int, "problem_id": int}`
- **Purpose**: Mark flashlight problem as solved by current user

**POST /reset_by_user**
- **Auth**: User required
- **Input**: `question_id` (query param)
- **Output**: `{"solved": bool, "user_id": int, "problem_id": int}`
- **Purpose**: Reset flashlight problem progress

**GET /is_solved_by_user**
- **Auth**: User required
- **Input**: `problem_id` (query param)
- **Output**: `{"solved": bool}`
- **Purpose**: Check if user solved specific flashlight problem

**GET /get_all_problems_solved_by_user**
- **Auth**: User required
- **Output**: `List[FlashlightProblemResponseDTO]`
- **Purpose**: Get all flashlight problems solved by current user

**GET /get_user_track_status**
- **Auth**: User required
- **Output**: `{"total_problems": int, "solved_problems": int, "unsolved_problems": int}`
- **Purpose**: Get user's flashlight drill progress summary

---

### 5. Multiple Choice Question (`MCQuestion.py`)

**Status**: Placeholder file (empty or minimal implementation)

**Purpose**: Future endpoint for MC question drill features

---

## Common Patterns

### 1. Database Session Management

All endpoints use dependency injection for database sessions:

```python
from model.Base import get_db

@router.get("/endpoint")
async def my_endpoint(db: Session = Depends(get_db)):
    # db is automatically opened and closed
    results = db.query(Model).all()
    return results
```

### 2. Authentication

**User Authentication**:
```python
from auth.auth import get_current_user
from model.User import UserDB

@router.get("/protected")
async def protected_endpoint(user: UserDB = Depends(get_current_user)):
    # user is the authenticated UserDB instance
    return {"username": user.username}
```

**Admin Authentication**:
```python
from auth.auth import require_admin

@router.post("/admin-only")
async def admin_endpoint(admin: UserDB = Depends(require_admin)):
    # admin is a UserDB instance with role="admin"
    return {"message": "Admin access granted"}
```

### 3. Response Models

Always specify `response_model` for automatic validation and documentation:

```python
@router.get("/all", response_model=List[ResourceResponseDTO])
async def get_all(db: Session = Depends(get_db)):
    return db.query(ResourceDB).all()
    # FastAPI automatically converts to DTO
```

### 4. Error Handling

Use HTTPException for errors:

```python
from fastapi import HTTPException
from starlette import status

@router.get("/get/{id}")
async def get_by_id(id: int, db: Session = Depends(get_db)):
    item = db.query(Model).filter(Model.id == id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item
```

### 5. Many-to-Many Relationship Updates

When updating many-to-many relationships, update both sides:

```python
# Correct pattern (from EvidenceProblem.py)
if problem not in user.evidence_problems_solved:
    user.evidence_problems_solved.append(problem)
if user not in problem.solved_by_users:
    problem.solved_by_users.append(user)

db.add(user)
db.add(problem)
db.commit()
```

### 6. Pagination

Standard pagination pattern:

```python
@router.get("/all")
async def get_all(
    page: int = 0,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    if page < 0:
        raise HTTPException(status_code=400, detail="Invalid page")

    limit = min(page_size, 200)  # Cap at 200
    offset = page * limit

    return (
        db.query(Model)
        .order_by(Model.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
```

### 7. Search/Filter Pattern

Use SQLAlchemy `or_` and `ilike` for flexible searching:

```python
from sqlalchemy import or_

@router.get("/search")
async def search(q: str, db: Session = Depends(get_db)):
    pattern = f"%{q}%"
    return (
        db.query(Model)
        .filter(
            or_(
                Model.field1.ilike(pattern),
                Model.field2.ilike(pattern),
            )
        )
        .all()
    )
```

---

## Best Practices

### Creating New Routers

1. **Create router file**:
```python
# router/NewResource.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from DTO.NewResource import NewResourceDTO, NewResourceResponseDTO
from model.NewResource import NewResourceDB
from model.Base import get_db

router = APIRouter(prefix="/new_resource")

@router.post("/create", response_model=NewResourceResponseDTO)
async def create(data: NewResourceDTO, db: Session = Depends(get_db)):
    new_item = NewResourceDB(**data.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item
```

2. **Register in main.py**:
```python
from router import NewResource

app.include_router(NewResource.router)
```

3. **Update this CLAUDE.md**:
- Add to directory structure
- Document all endpoints
- Add examples

### Endpoint Naming Conventions

- **CRUD Operations**: `/create`, `/update`, `/delete`
- **Retrieval**: `/get/{id}`, `/all`, `/search`
- **User Actions**: `/solved_by_user`, `/reset_by_user`
- **Status Checks**: `/is_solved_by_user`, `/get_user_track_status`

### Security Guidelines

1. **Never expose sensitive data**:
   - Don't return passwords or hashes
   - Use DTOs to control exposed fields

2. **Require authentication when needed**:
   - User data: `Depends(get_current_user)`
   - Admin operations: `Depends(require_admin)`
   - Public data: No auth dependency

3. **Validate input**:
   - Use Pydantic DTOs for input validation
   - Check constraints (page >= 0, limit <= 200)
   - Validate IDs exist before operations

4. **Return appropriate status codes**:
   - 200 OK: Success
   - 201 Created: Resource created
   - 400 Bad Request: Invalid input
   - 401 Unauthorized: Not authenticated
   - 403 Forbidden: Not authorized (wrong role)
   - 404 Not Found: Resource doesn't exist

### Database Best Practices

1. **Always use dependency injection**:
```python
db: Session = Depends(get_db)
```

2. **Commit after changes**:
```python
db.add(item)
db.commit()
db.refresh(item)  # Get updated values
```

3. **Use `.first()` for single results**:
```python
item = db.query(Model).filter(Model.id == id).first()
if not item:
    raise HTTPException(404, "Not found")
```

4. **Use `.all()` for multiple results**:
```python
items = db.query(Model).all()
```

---

## Registration in main.py

Routers are registered in `main.py`:

```python
from router import EvidenceProblem, FlashlightProblem, ReadingContent, User

app.include_router(EvidenceProblem.router)
app.include_router(FlashlightProblem.router)
app.include_router(ReadingContent.router)
app.include_router(User.router)
```

**Order matters**: Register routers with more specific prefixes first.

---

## Testing Endpoints

### Using FastAPI Docs

Access interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Authentication in Docs

1. Create user via `/register`
2. Login via `/token` to get access_token
3. Click "Authorize" button in Swagger UI
4. Enter: `Bearer <your-access-token>`

### Example: Testing with curl

```bash
# Register
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"pass123"}'

# Login
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=pass123"

# Use token
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer <token>"
```

---

## Common Queries

### Get All Resources with Pagination
```python
# GET /resource/all?page=0&page_size=20
```

### Create Resource (Admin)
```python
# POST /resource/create
# Body: ResourceDTO JSON
# Header: Authorization: Bearer <admin-token>
```

### Search Resources
```python
# GET /resource/search?q=keyword&limit=10
```

### Track User Progress
```python
# POST /evidence_problem/solved_by_user?question_id=5
# Header: Authorization: Bearer <user-token>
```

---

## Troubleshooting

### Common Issues

**1. "Could not validate credentials"**
- Token expired or invalid
- Re-login to get new token
- Check `ACCESS_TOKEN_EXPIRE_MINUTES` setting

**2. "Not enough permissions"**
- Using user token for admin endpoint
- Check if user has `role="admin"`

**3. "Detail: Item not found"**
- Resource ID doesn't exist
- Check database for valid IDs

**4. "Username already registered"**
- User exists in database
- Choose different username

**5. Relationship not updating**
- Update both sides of many-to-many
- Call `db.add()` for both objects
- Don't forget `db.commit()`

---

## Future Routers

When creating new feature routers (e.g., GapFill):

1. Create `router/NewRouter.py`
2. Follow the Evidence Problem or Flashlight Problem pattern
3. Include:
   - CRUD endpoints (admin)
   - Public list/get endpoints
   - User progress tracking endpoints
4. Register in `main.py` via `app.include_router(NewRouter.router)`
5. Update this CLAUDE.md

**Template**:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from DTO.NewResource import NewResourceDTO, NewResourceResponseDTO
from auth.auth import require_admin, get_current_user
from model.Base import get_db
from model.NewResource import NewResourceDB
from model.User import UserDB

router = APIRouter(prefix="/new_resource")

@router.post("/create", response_model=NewResourceResponseDTO)
async def create(
    input_data: NewResourceDTO,
    admin: UserDB = Depends(require_admin),
    db: Session = Depends(get_db)
):
    new_item = NewResourceDB(**input_data.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/all", response_model=List[NewResourceResponseDTO])
async def get_all(
    page: int = 0,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    limit = min(page_size, 200)
    offset = page * limit
    return db.query(NewResourceDB).offset(offset).limit(limit).all()

@router.post("/solved_by_user")
async def mark_solved(
    question_id: int,
    user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update relationship logic
    pass

@router.get("/get_user_track_status")
async def get_status(
    user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total = db.query(NewResourceDB).count()
    solved = len(user.new_resources_solved)
    return {
        "total_problems": total,
        "solved_problems": solved,
        "unsolved_problems": total - solved
    }
```
