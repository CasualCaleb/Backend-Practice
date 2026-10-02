from fastapi import APIRouter, HTTPException, Depends, Request
from services import user_services, admin_services
from models.user import User

# CHECK IF USER IS ADMIN
async def require_admin(request: Request):
    user_id = request.session.get('user_id')

    if not isinstance(user_id, int):
        raise HTTPException(
            status_code=401,
            detail="You must be logged in"
        )

    admin_user = await user_services.get_user(user_id)

    if admin_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if admin_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return admin_user

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)]
)

# Get all users
@router.get("/users", response_model=list[User])
async def list_users() -> list[User]:
    return await admin_services.get_users()

# Get user by id
@router.get("/users/{user_id}", response_model=User)
async def admin_get_user_by_id(user_id: int):
    user = await user_services.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

# Remove user by id
@router.delete("/users/{user_id}")
async def admin_remove_user(
        request: Request,
        user_id: int,
        admin_user: User = Depends(require_admin)
):
    user = await user_services.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    await admin_services.delete_user(admin_user.id, user_id)

    # Handle if admin deleted themselves
    if request.session["user_id"] == user_id:
        request.session.clear()

    return {"message": "User removed"}