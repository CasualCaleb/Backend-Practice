from pydantic import BaseModel, Field

class UsernameUpdate(BaseModel):
    username: str = Field(min_length=5, max_length=50)

class User(BaseModel):
    id: int | None = None
    username: str
    role: str = 'user'

class OauthAccount(BaseModel):
    id: int | None = None
    user_id: int
    provider: str
    provider_id: str
    provider_email: str