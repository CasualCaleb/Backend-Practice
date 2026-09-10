from fastapi import APIRouter, Request, HTTPException
from db import get_user_by_id,update_username
from models import UsernameUpdate

router = APIRouter(prefix="/api/users")

# Get current user info
@router.get("/me", name="me")
async def read_users_me(request: Request):
    if "user_id" not in request.session:
        return {"message": "You have not logged in"}

    user_id = request.session["user_id"]
    return get_user_by_id(user_id)

@router.patch("/me/username", name="username")
async def read_users_username(data: UsernameUpdate, request: Request):
    if "user_id" not in request.session:
        raise HTTPException(status_code=401, detail="You have not logged in")

    return update_username(
        request.session["user_id"],
        data.username
    )