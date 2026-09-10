from pydantic import BaseModel

class UsernameUpdate(BaseModel):
    username: str

class User(BaseModel):
    id: int | None = None
    google_id: str
    username: str
    email: str
    role: str = 'user'