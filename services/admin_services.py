from models import User
from db import database

async def get_users() -> list[User]:
    return await database.get_users()

async def delete_user(admin_id: int, user_id: int) -> bool:
    is_deleted = await database.delete_user(user_id)

    if is_deleted:
        await database.log_activity(
            user_id=admin_id,
            action="Termination",
            details=f"Admin {admin_id} terminated account for user {user_id}"
        )

    return is_deleted