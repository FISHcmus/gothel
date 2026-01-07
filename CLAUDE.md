# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL: Documentation Maintenance Protocol

**IMPORTANT**: Whenever you make changes to the codebase, you **MUST** follow this checklist:

### Before Making Changes
1. **Check for CLAUDE.md files** in the directory you're working in
2. **Read the relevant CLAUDE.md** to understand current architecture and patterns
3. **Follow established patterns** documented in CLAUDE.md files

### After Making Changes
1. **Update affected CLAUDE.md files immediately**:
   - If you modify models → update `model/CLAUDE.md`
   - If you modify DTOs → update `DTO/CLAUDE.md`
   - If you modify routers → update `router/CLAUDE.md` (if it exists)
   - If you modify frontend routes → update relevant `storefront/app/*/CLAUDE.md`
   - If you add new features → update root `CLAUDE.md`

2. **What to update**:
   - Directory structure listings
   - File descriptions
   - Code examples
   - Relationship documentation
   - Best practices
   - Usage examples

3. **Verification**:
   - Ensure all new files are listed in directory structures
   - Ensure all new relationships are documented
   - Ensure code examples are accurate and tested

### CLAUDE.md Files in This Project

```
Gothel/
├── CLAUDE.md                              # This file - project overview
├── model/CLAUDE.md                        # Database models documentation
├── DTO/CLAUDE.md                          # DTOs documentation
├── router/CLAUDE.md                       # API routers documentation
├── script/CLAUDE.md                       # Utility scripts documentation
├── storefront/CLAUDE.md                   # Frontend overview
└── storefront/app/evidence/CLAUDE.md      # Evidence route documentation
    └── blueprint/                         # Design references
        ├── blueprint-1.png
        ├── evidence-list-redesign.png
        └── evidence-problem-redesign.png
```

**Rule**: If you create a new major component/module/route, create a CLAUDE.md for it.

---

## Project Overview

Gothel is an IELTS reading practice application with a FastAPI backend and Next.js frontend. The application focuses on evidence-based reading comprehension problems where users identify evidence in reading passages that support specific statements.

## Architecture

### Backend (FastAPI + SQLAlchemy)

**Entry Point**: `main.py` - FastAPI application with CORS middleware configured for localhost:3000 and production deployment.

**Router Pattern**: The application uses FastAPI's router system to organize endpoints:
- Routes are defined in `router/` directory modules
- Each router is included in `main.py` via `app.include_router()`
- Main routers: `EvidenceProblem`, `FlashlightProblem`, `ReadingContent`, `User`

**Data Layer**:
- **Models** (`model/`): SQLAlchemy ORM models define database schema
  - `Base.py`: Database engine configuration, session management, and `TimestampMixin` for automatic `created_at`/`updated_at` columns
  - Database: SQLite (`db_local.db`)
  - Association tables defined in `Base.py` (e.g., `user_evidence_problem_association` for many-to-many relationships)
- **DTOs** (`DTO/`): Pydantic models for request/response validation
  - Separate DTOs for input (e.g., `EvidenceProblemDTO`) and responses (e.g., `EvidenceProblemResponseDTO`)

**Authentication** (`auth/auth.py`):
- JWT-based authentication using PyJWT
- Password hashing with Argon2 (via passlib)
- OAuth2 password bearer flow
- Two dependency injection functions:
  - `get_current_user`: Validates JWT and returns authenticated user
  - `require_admin`: Extends `get_current_user` to require admin role
- Configuration via environment variables:
  - `AUTH_SECRET`: JWT signing key
  - `AUTH_ALGORITHM`: Default HS256
  - `ACCESS_TOKEN_EXPIRE_MINUTES`: Default 30 minutes

**Key Relationship Pattern**:
The application uses many-to-many relationships between users and problems to track which problems users have solved. The `user_evidence_problem_association` table links `UserDB.evidence_problems_solved` with `EvidenceProblemDB.solved_by_users`.

### Frontend (Next.js + TypeScript)

**Location**: `storefront/` directory
- Next.js 16 with App Router
- TypeScript with React 19
- Styling: Tailwind CSS v4 + Radix UI components
- Theme support via `next-themes`

**Structure**:
- `app/`: Next.js app directory with route-based organization
  - `evidence/`: Evidence problem practice pages
  - `flashlight/`, `gapfill/`: Other practice modes
  - `components/`: Shared UI components
  - `lib/`: Utility functions

**API Integration**:
- Backend URL configured per environment (`.env.development`, `.env.production`)
- JWT token stored in localStorage
- CORS configured in backend for localhost:3000 and production domain

## Development Commands

### Backend

Python dependencies are managed with `uv` (uses `pyproject.toml`):
```bash
uv sync              # Install dependencies
uv sync --group dev  # Include dev dependencies (factory-boy, faker for test data)
```

Start the FastAPI development server:
```bash
uvicorn main:app --reload
```

The server runs on `http://localhost:8000`. Interactive API docs available at `/docs`.

**Utility Scripts** (`script/` directory):
```bash
# Reset all database tables (deletes all data!)
python -m script.reset_all

# Reset a specific table
python -m script.reset user_table

# Create default admin user
python -m script.create_admin

# Generate test users
python -m script.user_gen

# Generate real evidence problems
python -m script.gen_real_evidence_data
```

See `script/CLAUDE.md` for complete documentation of all utility scripts.

### Frontend

```bash
cd storefront
npm install        # Install dependencies
npm run dev        # Start development server (localhost:3000)
npm run build      # Build for production
npm run start      # Start production server
npm run lint       # Run ESLint
npm run lint:fix   # Fix ESLint issues
```

## Environment Configuration

### Backend (.env)
Required environment variables:
- `AUTH_SECRET`: Secret key for JWT signing
- `AUTH_ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

### Frontend
- `.env.development`: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- `.env.production`: `NEXT_PUBLIC_API_URL=https://gothel.fishcmus.io.vn`

## Database Schema Notes

**TimestampMixin**: All models that inherit from `TimestampMixin` automatically get `created_at` and `updated_at` timestamp columns with automatic management.

**Many-to-Many Pattern**: User-problem relationships use association tables defined in `model/Base.py`. When creating new many-to-many relationships, define the association table in `Base.py` and reference it in both model classes using SQLAlchemy's `relationship()` with the `secondary` parameter.

## API Endpoint Patterns

**Authentication Required**: Use `Depends(get_current_user)` to require authentication
**Admin Required**: Use `Depends(require_admin)` to require admin role
**Database Session**: Use `Depends(get_db)` to inject database session

Example from `router/EvidenceProblem.py`:
```python
@router.post("/create", response_model=EvidenceProblemResponseDTO)
async def create_reading_content(
    input_data: EvidenceProblemDTO,
    admin: UserDB = Depends(require_admin),
    db: Session = Depends(get_db)
):
```

## Testing User Tracking

The evidence problem router includes endpoints for tracking user progress:
- `/solved_by_user`: Mark a problem as solved
- `/reset_by_user`: Mark a problem as unsolved
- `/is_solved_by_user`: Check if user solved a specific problem
- `/get_all_problems_solved_by_user`: Get all problems solved by user
- `/get_user_track_status`: Get summary of user's progress (total/solved/unsolved)

These endpoints manage the bidirectional relationship between users and problems.
