from fastapi import APIRouter, Request, HTTPException, Depends
from db import get_user_by_id, update_username, delete_user, log_activity
from models import UsernameUpdate, User

async def require_user(request: Request) -> User:
    if "user_id" not in request.session:
        raise HTTPException(
            status_code=401,
            detail="You have not logged in"
        )
    user = await get_user_by_id(request.session["user_id"])

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

router = APIRouter(
    prefix="/api/users",
    dependencies=[Depends(require_user)]
)

# Get current user info
@router.get("/me", name="me")
async def read_users_me(user: User = Depends(require_user)):
    return user

# Change the current user's username
@router.patch("/me/username", name="username")
async def change_username(data: UsernameUpdate, user: User = Depends(require_user)):
    is_updated = await update_username(
        user.id,
        data.username
    )
    if is_updated:
        await log_activity(
            user.id,
            "username",
            f"Changed username to {data.username}"
        )

    return is_updated

# Delete the current user
@router.delete("/me", name="delete_me")
async def delete_me(request: Request, user: User = Depends(require_user)):
    is_deleted  = await delete_user(user.id)

    if is_deleted :
        request.session.clear()

    return is_deleted