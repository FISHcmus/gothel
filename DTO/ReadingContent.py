from pydantic import BaseModel


class ReadingContentDTO(BaseModel):
    content: str

class ReadingContentResponseDTO(BaseModel):
    id: int
    content: str

    class Config:
        from_attributes = True