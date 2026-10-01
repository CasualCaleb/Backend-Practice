from models import User, OauthAccount, RegisterUser
from db import database

async def record_logout(user: User) -> bool:
    return await database.log_activity(
        user_id=user.id,
        action="logout",
        details="User logged out"
    )

async def record_login(user: User) -> bool:
    return await database.log_activity(
        user_id=user.id,
        action="login",
        details="User logged in"
    )

async def link_oauth_account(oauth_account: OauthAccount) -> OauthAccount:
    oauth_account = await database.link_oauth_account(oauth_account)

    await database.log_activity(
        user_id=oauth_account.user_id,
        action="Oauth Link",
        details=f"User linked with {oauth_account.provider} Oauth"
    )

    return oauth_account

async def get_oauth_account(provider: str, provider_id: str) -> OauthAccount | None:
    return await database.get_oauth_account(
        provider,
        provider_id
    )

async def get_oauth_accounts(user: User) -> list[OauthAccount]:
    return await database.get_oauth_accounts_by_user_id(user.id)

async def register_user(registration: RegisterUser) -> tuple[User, OauthAccount]:
    user = await database.add_user(
        User(
            username=registration.username,
            role=registration.role,
        )
    )

    await database.log_activity(
        user_id=user.id,
        action="register",
        details="User registered a new account"
    )

    oauth_account = await link_oauth_account(
        OauthAccount(
            user_id=user.id,
            provider=registration.provider,
            provider_id=registration.provider_id,
            provider_email=registration.provider_email,
        )
    )

    return user, oauth_account