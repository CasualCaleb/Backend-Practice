from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET
from models import User, OauthAccount, CreateUser, CreateOauthAccount
from services import user_services, auth_services

router = APIRouter(prefix="/api/auth")
oauth = OAuth()

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)
oauth.register(
    name="discord",
    client_id=DISCORD_CLIENT_ID,
    client_secret=DISCORD_CLIENT_SECRET,
    authorize_url="https://discord.com/oauth2/authorize",
    access_token_url="https://discord.com/api/oauth2/token",
    api_base_url="https://discord.com/api/",
    client_kwargs={
        "scope": "identify email"
    }
)

@router.get("/login/{provider}")
async def login(request: Request, provider: str):
    oauth_client = oauth.create_client(provider)

    if oauth_client is None:
        raise HTTPException(
            status_code=404,
            detail="Oauth provider not supported"
        )

    user_id = request.session.get("user_id")

    request.session["oauth_action"] = "register"

    if isinstance(user_id, int):
        user = await user_services.get_user(user_id)

        if isinstance(user, User):
            request.session["oauth_action"] = "link"
            request.session["oauth_link_user_id"] = user.id
        else:
            request.session.pop("user_id", None)

    redirect_uri = request.url_for(
        "auth_callback",
        provider=provider
    )

    return await oauth_client.authorize_redirect(request, redirect_uri)

@router.post("/logout")
async def logout(request: Request):
    user_id = request.session.get("user_id")

    if not isinstance(user_id, int):
        raise HTTPException(
            status_code=401,
            detail="You have not logged in"
        )

    user = await user_services.get_user(user_id)

    # Handle if existing_user is None
    if user is None:
        request.session.pop("user_id", None)
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    await auth_services.record_logout(user)

    request.session.pop("user_id", None)

    return {"message": "You have been logged out"}

async def get_oauth_user_data(request: Request, provider: str) -> dict:
    oauth_client = oauth.create_client(provider)

    if oauth_client is None:
        raise HTTPException(
            status_code=404,
            detail="OAuth provider not supported"
        )

    token = await oauth_client.authorize_access_token(request)

    if provider == 'google':
        user_data = token['userinfo']

        return {
            'provider': 'google',
            'username': user_data['name'],
            'provider_id': user_data['sub'],
            'provider_email': user_data['email'],
        }
    elif provider == 'discord':
        response = await oauth_client.get(
            "users/@me",
            token=token
        )

        user_data = response.json()

        return {
            'provider': 'discord',
            'username': user_data['username'],
            'provider_id': user_data['id'],
            'provider_email': user_data['email'],
        }

    raise HTTPException(
        status_code=404,
        detail="Oauth provider not supported"
    )

async def validate_oauth_account(request: Request, oauth_data) -> User:
    oauth_action = request.session.pop("oauth_action", None)

    if oauth_action not in ("register", "link"):
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth action"
        )

    if oauth_action == 'link':
        user_id = request.session.get('user_id')
        original_id = request.session.pop("oauth_link_user_id", None)

        if not isinstance(user_id, int) or user_id != original_id:
            raise HTTPException(
                status_code=401,
                detail="OAuth linking session changed"
            )

        user = await user_services.get_user(user_id)

        if not isinstance(user, User):
            request.session.pop("user_id", None)
            raise HTTPException(
                status_code=401,
                detail="User no longer exists"
            )

    oauth_account = await auth_services.get_oauth_account(
        oauth_data['provider'],
        oauth_data['provider_id']
    )

    # Logic for if we have DO have the oauth in the db
    if oauth_account is not None:
        if oauth_action == "link":
            if oauth_account.user_id != user.id:
                raise HTTPException(
                    status_code=409,
                    detail="OAuth account already linked to another user"
                )

            return user

        existing_user = await user_services.get_user(oauth_account.user_id)

        if not isinstance(existing_user, User):
            request.session.pop('user_id', None)
            raise HTTPException(
                status_code=401,
                detail="User no longer exists"
            )

        return existing_user

    # Logic for if we have DON'T have the oauth in the db
    if oauth_action == "link":
        await auth_services.link_oauth_account(
            user,
            CreateOauthAccount(
                provider=oauth_data['provider'],
                provider_id=oauth_data['provider_id'],
                provider_email=oauth_data['provider_email'],
            ))

        return user

    # Logic for if oauth_action == "register"
    user, _ = await auth_services.register_user(
        CreateUser(
            username=oauth_data['username']
        ),
        CreateOauthAccount(
            provider=oauth_data['provider'],
            provider_id=oauth_data['provider_id'],
            provider_email=oauth_data['provider_email']
        )
    )

    return user

@router.get("/callback/{provider}", name="auth_callback")
async def auth_callback(request: Request, provider: str):
    oauth_data = await get_oauth_user_data(request, provider)
    user = await validate_oauth_account(request, oauth_data)

    # Save user id to session
    request.session['user_id'] = user.id

    await auth_services.record_login(user)

    return RedirectResponse(url=request.url_for("me"))