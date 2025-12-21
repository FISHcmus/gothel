from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from DTO.ReadingContent import ReadingContentDTO, ReadingContentResponseDTO
from auth.auth import  require_admin
from model.Base import get_db
from model.ReadingContent import ReadingContentDB
from model.User import UserDB

router = APIRouter()
@router.post("/reading_content/create", response_model=ReadingContentResponseDTO)
async def create_reading_content(input_data: ReadingContentDTO,
                                 admin: UserDB = Depends(require_admin),
                                 db: Session = Depends(get_db)):
    new_content = ReadingContentDB()
    new_content.content = input_data.content
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content

# delete reading content