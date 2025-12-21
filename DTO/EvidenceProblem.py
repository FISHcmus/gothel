from pydantic import BaseModel


class EvidenceProblemDTO(BaseModel):
    reading_content: str
    evidence: str

