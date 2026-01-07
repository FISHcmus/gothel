from pydantic import BaseModel


class FlashlightProblemDTO(BaseModel):
    problem_statement: str
    target: str
    reading_content: str

class FlashlightProblemResponseDTO(BaseModel):
    id: int
    problem_statement: str
    target: str
    reading_content: str

    class Config:
        from_attributes = True
