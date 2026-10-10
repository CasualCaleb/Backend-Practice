from pydantic import BaseModel

class OauthAccount(BaseModel):
    id: int
    user_id: int
    provider: str
    provider_id: str
    provider_email: str

class CreateOauthAccount(BaseModel):
    provider: str
    provider_id: str
    provider_email: str