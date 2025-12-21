from typing import Literal

from pydantic import BaseModel


class UserCreateDTO(BaseModel):
    username: str
    password: str


class UserResponseDTO(BaseModel):
    username: str
    role: Literal["user", "admin"]

    class Config:
        from_attributes = True
