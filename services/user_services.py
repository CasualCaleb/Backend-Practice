from db import database
from models import User

async def get_user(user_id: int) -> User | None:
    return await database.get_user_by_id(user_id)

async def change_username(user_id: int, username: str) -> bool:
    is_updated = await database.update_username(
        user_id=user_id,
        username=username
    )

    if is_updated:
        await database.log_activity(
            user_id=user_id,
            action="Username",
            details=f"Changed username to {username}"
        )

    return is_updated

async def delete_user(user_id: int) -> bool:
    is_deleted = await database.delete_user(user_id)

    if is_deleted:
        await database.log_activity(
            user_id=user_id,
            action="Termination",
            details=f"User terminated account"
        )

    return is_deleted