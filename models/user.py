from pydantic import BaseModel

class UsernameUpdate(BaseModel):
    username: str

class User(BaseModel):
    id: int
    username: str
    role: str

class CreateUser(BaseModel):
    username: str
    role: str = 'user'