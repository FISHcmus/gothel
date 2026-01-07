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
    new_problem.correct_answer = input_data.correct_answer
    new_problem.options = input_data.options
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
    problem.options = input_data.options
    problem.correct_answer = input_data.correct_answer
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
async def solved_by_user(question_id: int,
                         user: UserDB = Depends(get_current_user),
                         db: Session = Depends(get_db),
                         ):
    """
    Mark a question as solved by the user
    :param question_id:
    :param user:
    :param db:
    :return:
    """
    print(f"User {user.username} is solving question {question_id}")
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


@router.post("/reset_by_user")
async def reset_by_user(question_id: int,
                        user: UserDB = Depends(get_current_user),
                        db: Session = Depends(get_db),
                        ):
    """
    Reset a question as to be unsolved by the user
    :param question_id:
    :param user:
    :param db:
    :return:
    """
    print(f"User {user.username} is solving question {question_id}")
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

        # Remove the relationship if it exists
    if problem in user.evidence_problems_solved:
        user.evidence_problems_solved.remove(problem)

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
        .order_by(EvidenceProblemDB.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/get/{problem_id}", response_model=EvidenceProblemResponseDTO)
async def get_problem_by_id(problem_id: int,
                            db: Session = Depends(get_db)):
    problem: EvidenceProblemDB | None = db.query(EvidenceProblemDB).filter(
        EvidenceProblemDB.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return problem


@router.get("/is_solved_by_user")
async def get_my_solved_problems(problem_id: int,
                                 user: UserDB = Depends(get_current_user),
                                 db: Session = Depends(get_db)
                                 ):
    for problem in user.evidence_problems_solved:
        if problem.id == problem_id:
            return {"solved": True}
    return {"solved": False}


@router.get("/get_all_problems_solved_by_user", response_model=List[EvidenceProblemResponseDTO])
async def get_all_solved_problems_by_user(
        user: UserDB = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return user.evidence_problems_solved


@router.get("/get_user_track_status")
async def get_user_evidence_track_status(
        user: UserDB = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    total_problems = db.query(EvidenceProblemDB).count()
    solved_problems = len(user.evidence_problems_solved)
    return {
        "total_problems": total_problems,
        "solved_problems": solved_problems,
        "unsolved_problems": total_problems - solved_problems
    }
