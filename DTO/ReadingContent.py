from pydantic import BaseModel


class ReadingContentDTO(BaseModel):
    content: str