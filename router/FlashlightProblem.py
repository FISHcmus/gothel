from typing import List, Optional

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from starlette import status

from DTO.FlashlightProblem import FlashlightProblemDTO, FlashlightProblemResponseDTO
from auth.auth import require_admin, get_current_user
from model.Base import get_db
from model.FlashlightProblem import FlashlightProblemDB
from model.User import UserDB

router = APIRouter(prefix="/flashlight_problem")


@router.post("/create", response_model=FlashlightProblemResponseDTO)
async def create_flashlight_problem(
    input_data: FlashlightProblemDTO,
    admin: UserDB = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new flashlight drill problem (admin only).

    Flashlight drills require users to find and highlight specific target text
    within a reading passage, typically under time pressure (15 seconds).
    """
    new_problem = FlashlightProblemDB(
        problem_statement=input_data.problem_statement,
        target=input_data.target,
        reading_content=input_data.reading_content
    )
    db.add(new_problem)
    db.commit()
    db.refresh(new_problem)
    return new_problem


@router.post("/delete")
async def delete_flashlight_problem(
    problem_id: int,
    admin: UserDB = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a flashlight problem (admin only)."""
    problem: FlashlightProblemDB | None = db.query(FlashlightProblemDB).filter(
        FlashlightProblemDB.id == problem_id
    ).first()

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found or already deleted"
        )

    db.delete(problem)
    db.commit()
    return {"ok": True, "id": problem.id}


@router.post("/update", response_model=FlashlightProblemResponseDTO)
async def update_flashlight_problem(
    input_data: FlashlightProblemDTO,
    problem_id: int,
    admin: UserDB = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update an existing flashlight problem (admin only)."""
    problem: FlashlightProblemDB | None = db.query(FlashlightProblemDB).filter(
        FlashlightProblemDB.id == problem_id
    ).first()

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )

    problem.problem_statement = input_data.problem_statement
    problem.target = input_data.target
    problem.reading_content = input_data.reading_content

    db.commit()
    db.refresh(problem)
    return problem


@router.get("/search", response_model=List[FlashlightProblemResponseDTO], status_code=status.HTTP_200_OK)
async def search_flashlight_problems(
    q: Optional[str] = None,
    problem_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Search flashlight problems by query string.

    - **q**: Search in problem_statement, target, or reading_content
    - **problem_id**: Filter by specific problem ID
    - **limit**: Max results (capped at 200)
    - **offset**: Pagination offset
    """
    query = db.query(FlashlightProblemDB)

    if problem_id is not None:
        query = query.filter(FlashlightProblemDB.id == problem_id)

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                FlashlightProblemDB.reading_content.ilike(pattern),
                FlashlightProblemDB.target.ilike(pattern),
                FlashlightProblemDB.problem_statement.ilike(pattern),
            )
        )

    return (
        query.order_by(FlashlightProblemDB.id.desc())
        .offset(offset)
        .limit(min(limit, 200))
        .all()
    )


@router.post("/solved_by_user")
async def solved_by_user(
    question_id: int,
    user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark a flashlight problem as solved by the current user.

    Updates the many-to-many relationship between users and flashlight problems.
    """
    problem: FlashlightProblemDB | None = (
        db.query(FlashlightProblemDB)
        .filter(FlashlightProblemDB.id == question_id)
        .first()
    )

    if problem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )

    # Update both sides of the relationship
    if problem not in user.flashlight_problems_solved:
        user.flashlight_problems_solved.append(problem)
    if user not in problem.solved_by_users:
        problem.solved_by_users.append(user)

    db.add(user)
    db.add(problem)
    db.commit()

    return {
        "solved": True,
        "user_id": user.id,
        "problem_id": problem.id,
    }


@router.post("/reset_by_user")
async def reset_by_user(
    question_id: int,
    user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark a flashlight problem as unsolved (reset user progress).

    Removes the relationship between user and problem.
    """
    problem: FlashlightProblemDB | None = (
        db.query(FlashlightProblemDB)
        .filter(FlashlightProblemDB.id == question_id)
        .first()
    )

    if problem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )

    # Remove the relationship if it exists
    if problem in user.flashlight_problems_solved:
        user.flashlight_problems_solved.remove(problem)

    if user in problem.solved_by_users:
        problem.solved_by_users.remove(user)

    db.add(user)
    db.add(problem)
    db.commit()

    return {
        "solved": False,
        "user_id": user.id,
        "problem_id": problem.id,
    }


@router.get("/all", response_model=List[FlashlightProblemResponseDTO], status_code=status.HTTP_200_OK)
async def get_all_problems_with_pagination(
    page: int = 0,
    page_size: int = 50,
    db: Session = Depends(get_db),
):
    """
    Get all flashlight problems with pagination.

    - **page**: Page number (0-indexed)
    - **page_size**: Items per page (max 200)
    """
    if page < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid page number"
        )

    limit = min(page_size, 200)
    offset = page * limit

    return (
        db.query(FlashlightProblemDB)
        .order_by(FlashlightProblemDB.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/get/{problem_id}", response_model=FlashlightProblemResponseDTO)
async def get_problem_by_id(
    problem_id: int,
    db: Session = Depends(get_db)
):
    """Get a single flashlight problem by ID."""
    problem: FlashlightProblemDB | None = db.query(FlashlightProblemDB).filter(
        FlashlightProblemDB.id == problem_id
    ).first()

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )

    return problem


@router.get("/is_solved_by_user")
async def is_solved_by_user(
    problem_id: int,
    user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if the current user has solved a specific flashlight problem."""
    for problem in user.flashlight_problems_solved:
        if problem.id == problem_id:
            return {"solved": True}
    return {"solved": False}


@router.get("/get_all_problems_solved_by_user", response_model=List[FlashlightProblemResponseDTO])
async def get_all_solved_problems_by_user(
    user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all flashlight problems solved by the current user."""
    return user.flashlight_problems_solved


@router.get("/get_user_track_status")
async def get_user_flashlight_track_status(
    user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's flashlight drill progress summary.

    Returns total problems, solved count, and unsolved count.
    """
    total_problems = db.query(FlashlightProblemDB).count()
    solved_problems = len(user.flashlight_problems_solved)

    return {
        "total_problems": total_problems,
        "solved_problems": solved_problems,
        "unsolved_problems": total_problems - solved_problems
    }
