from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Literal


class UsernameUpdate(BaseModel):
    username: str = Field(min_length=5, max_length=50)

class User(BaseModel):
    id: int | None = None
    google_id: str
    username: str
    email: EmailStr
    role: str = Literal['user', 'admin']

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr