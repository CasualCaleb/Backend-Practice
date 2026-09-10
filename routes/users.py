from fastapi import APIRouter, Request, HTTPException
from db import get_user_by_id, update_username, delete_user
from models import UsernameUpdate

router = APIRouter(prefix="/api/users")

# Get current user info
@router.get("/me", name="me")
async def read_users_me(request: Request):
    if "user_id" not in request.session:
        return {"message": "You have not logged in"}

    user_id = request.session["user_id"]
    return get_user_by_id(user_id)

# Change the current user's username
@router.patch("/me/username", name="username")
async def change_username(data: UsernameUpdate, request: Request):
    if "user_id" not in request.session:
        raise HTTPException(status_code=401, detail="You have not logged in")

    return update_username(
        request.session["user_id"],
        data.username
    )

# Delete the current user
@router.delete("/me", name="delete_me")
async def delete_me(request: Request):
    if "user_id" not in request.session:
        raise HTTPException(status_code=401, detail="You have not logged in")
    user_id = request.session["user_id"]

    response = delete_user(user_id)

    if response:
        request.session.clear()

    return response