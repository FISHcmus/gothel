from pydantic import BaseModel


class EvidenceProblemDTO(BaseModel):
    problem_statement: str
    reading_content: str
    evidence: str

class EvidenceProblemResponseDTO(BaseModel):
    id: int
    problem_statement: str
    reading_content: str
    evidence: str

    class Config:
        from_attributes = True
