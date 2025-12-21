from typing import Literal

from pydantic import BaseModel


class UserCreateDTO(BaseModel):
    username: str
    password: str
    role: Literal["user", "admin"] = "user"


class UserResponseDTO(BaseModel):
    username: str
    role: Literal["user", "admin"]

    class Config:
        from_attributes = True  # Renamed from 'orm_mode' in Pydantic v2
