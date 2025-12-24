from typing import Literal, List

from pydantic import BaseModel

from DTO.EvidenceProblem import EvidenceProblemResponseDTO


class UserCreateDTO(BaseModel):
    username: str
    password: str


class UserResponseDTO(BaseModel):
    username: str
    role: Literal["user", "admin"]
    avatar_id: str | None
    email: str | None

    class Config:
        from_attributes = True
