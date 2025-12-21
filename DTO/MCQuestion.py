from pydantic import BaseModel


class MCQuestionDTO(BaseModel):
    question: str
    options: list[str]
    correct_option: int

