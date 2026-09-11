from fastapi import APIRouter, HTTPException, Depends, Request
from models.user import User
from db import get_user_by_id, get_users, delete_user

# CHECK IF USER IS ADMIN
async def require_admin(request: Request):
    if 'user_id' not in request.session:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in"
        )
    user = await get_user_by_id(request.session["user_id"])

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return user

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)]
)

# Get all users
@router.get("/users", response_model=list[User])
async def list_users() -> list[User]:
    return await get_users()

# Get user by id
@router.get("/users/{user_id}", response_model=User)
async def admin_get_user_by_id(user_id: int):
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

# Remove user by id
@router.delete("/users/{user_id}")
async def admin_remove_user(user_id: int, request: Request):
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    await delete_user(user_id)

    # Handle if user deletes themselves
    if request.session["user_id"] == user_id:
        request.session.clear()

    return {"message": "User removed"}