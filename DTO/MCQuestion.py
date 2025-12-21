from pydantic import BaseModel


class MCQuestionDTO(BaseModel):
    question: str
    options: list[str]
    correct_option: int

class MCQuestionResponseDTO(BaseModel):
    id: int
    question: str
    options: list[str]
    correct_option: int

    class Config:
        from_attributes = True