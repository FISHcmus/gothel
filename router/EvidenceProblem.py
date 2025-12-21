from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from DTO.EvidenceProblem import EvidenceProblemDTO
from auth.auth import require_admin
from model.Base import get_db
from model.Question import EvidenceProblemDB
from model.User import UserDB

router = APIRouter()
@router.post("/evidence_problem/create", response_model=EvidenceProblemDB)
async def create_reading_content(input_data: EvidenceProblemDTO,
                                 admin: UserDB = Depends(require_admin),
                                 db: Session = Depends(get_db)):
    new_problem = EvidenceProblemDB()
    new_problem.reading_content = input_data.reading_content
    new_problem.evidence = input_data.evidence
    db.add(new_problem)
    db.commit()
    db.refresh(new_problem)
    return new_problem
