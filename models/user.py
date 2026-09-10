from pydantic import BaseModel

class User(BaseModel):
    id: int | None = None
    google_id: str
    username: str
    email: str
    role: str = 'user'