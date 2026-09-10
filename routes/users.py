from fastapi import APIRouter, Request
from db.database import get_user_by_id

router = APIRouter(prefix="/api/users")

# Get current user info
@router.get("/me", name="me")
async def read_users_me(request: Request):
    if "user_id" not in request.session:
        return {"message": "You have not logged in"}

    user_id = request.session["user_id"]
    return get_user_by_id(user_id)