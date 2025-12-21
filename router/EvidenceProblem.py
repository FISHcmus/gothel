from typing import List, Optional

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from starlette import status

from DTO.EvidenceProblem import EvidenceProblemDTO, EvidenceProblemResponseDTO
from auth.auth import require_admin, get_current_user
from model.Base import get_db
from model.EvidenceProblem import EvidenceProblemDB
from model.User import UserDB

router = APIRouter(prefix="/evidence_problem")


@router.post("/create", response_model=EvidenceProblemResponseDTO)
async def create_reading_content(input_data: EvidenceProblemDTO,
                                 admin: UserDB = Depends(require_admin),
                                 db: Session = Depends(get_db)):
    new_problem = EvidenceProblemDB()
    new_problem.reading_content = input_data.reading_content
    new_problem.evidence = input_data.evidence
    new_problem.problem_statement = input_data.problem_statement
    db.add(new_problem)
    db.commit()
    db.refresh(new_problem)
    return new_problem


@router.post("/delete")
async def delete_evidence_problem(problem_id: int,
                                  admin: UserDB = Depends(require_admin),
                                  db: Session = Depends(get_db)):
    problem: EvidenceProblemDB | None = db.query(EvidenceProblemDB).filter(EvidenceProblemDB.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=400, detail="Problem already deleted")
    db.delete(problem)
    db.commit()
    return {"ok": True, "id": problem.id}


@router.post("/update", response_model=EvidenceProblemResponseDTO)
async def update_evidence_problem(input_data: EvidenceProblemDTO,
                                  problem_id: int,
                                  admin: UserDB = Depends(require_admin),
                                  db: Session = Depends(get_db)):
    problem: EvidenceProblemDB | None = db.query(EvidenceProblemDB).filter(
        EvidenceProblemDB.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problems not found")
    problem.reading_content = input_data.reading_content
    problem.evidence = input_data.evidence
    problem.problem_statement = input_data.problem_statement
    db.commit()
    db.refresh(problem)
    return problem


@router.get("/search",
            response_model=List[EvidenceProblemResponseDTO],
            status_code=status.HTTP_200_OK)
async def search_evidence_problems(
        q: Optional[str] = None,
        problem_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
        db: Session = Depends(get_db),
):
    query = db.query(EvidenceProblemDB)

    if problem_id is not None:
        query = query.filter(EvidenceProblemDB.id == problem_id)

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                EvidenceProblemDB.reading_content.ilike(pattern),
                EvidenceProblemDB.evidence.ilike(pattern),
                EvidenceProblemDB.problem_statement.ilike(pattern),
            )
        )

    return (
        query.order_by(EvidenceProblemDB.id.desc())
        .offset(offset)
        .limit(min(limit, 200))
        .all()
    )


@router.post("/solved_by_user")
async def solve_by_user(question_id: int,
                        user: UserDB = Depends(get_current_user),
                        db: Session = Depends(get_db),
                        ):
    problem: EvidenceProblemDB | None = (
        db.query(EvidenceProblemDB)
        .filter(EvidenceProblemDB.id == question_id)
        .first()
    )
    if problem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )

    # Update both sides of the relationship
    if problem not in user.evidence_problems_solved:
        user.evidence_problems_solved.append(problem)
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



@router.get(
    "/all",
    response_model=List[EvidenceProblemResponseDTO],
    status_code=status.HTTP_200_OK,
)
async def get_all_problem_with_pagination(
        page: int = 0,
        page_size: int = 50,
        db: Session = Depends(get_db),
):
    if page < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid page")
    limit = min(page_size, 200)
    offset = page * limit
    return (
        db.query(EvidenceProblemDB)
        .order_by(EvidenceProblemDB.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
