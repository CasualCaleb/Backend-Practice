from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET
from models import User, OauthAccount, RegisterUser
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

    # Validate existing session user
    if user_id is not None:
        user = await user_services.get_user(user_id)
        if user is None:
            request.session.clear()
            user_id = None

    # Determine OAuth action based on authentication state
    if user_id is None:
        request.session['oauth_action'] = 'register'
    else:
        request.session['oauth_action'] = 'link'

    redirect_uri = request.url_for(
        "auth_callback",
        provider=provider
    )

    return await oauth_client.authorize_redirect(request, redirect_uri)

@router.post("/logout")
async def logout(request: Request):
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="You have not logged in"
        )

    user = await user_services.get_user(user_id)

    # Handle if existing_user is None
    if user is None:
        request.session.clear()
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    await auth_services.record_logout(user)

    request.session.clear()

    return {"message": "You have been logged out"}

async def get_oauth_user_data(request: Request, provider: str) -> dict:
    oauth_client = oauth.create_client(provider)
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

@router.get("/callback/{provider}", name="auth_callback")
async def auth_callback(request: Request, provider: str):
    oauth_action = request.session.pop('oauth_action', None)

    if oauth_action not in ('link', 'register'):
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth action"
        )

    oauth_data = await get_oauth_user_data(
        request,
        provider
    )

    oauth_account = await auth_services.get_oauth_account(
        oauth_data['provider'],
        oauth_data['provider_id']
    )

    # When linking an oauth account checks if the account already has a link
    if oauth_action == 'link' and oauth_account is not None:
        if oauth_account.user_id != request.session.get('user_id'):
            raise HTTPException(
                status_code=409,
                detail='OAuth account already linked to another user'
            )

    if oauth_account is None:
        if oauth_action == 'link':
            user_id = request.session.get('user_id')
            if user_id is None:
                raise HTTPException(
                    status_code=401,
                    detail='Login session expired'
                )

            user = await user_services.get_user(user_id)

            if user is None:
                request.session.clear()
                raise HTTPException(
                    status_code=401,
                    detail="User no longer exists"
                )

            oauth_account = await auth_services.link_oauth_account(OauthAccount(
                user_id=user.id,
                provider=oauth_data['provider'],
                provider_id=oauth_data['provider_id'],
                provider_email=oauth_data['provider_email'],
            ))

        elif oauth_action == 'register':
            await auth_services.register_user(
                RegisterUser(
                    username=oauth_data['username'],
                    provider=oauth_data['provider'],
                    provider_id=oauth_data['provider_id'],
                    provider_email=oauth_data['provider_email'],
                )
            )

    user = await user_services.get_user(oauth_account.user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Save user id to session
    request.session['user_id'] = user.id

    await auth_services.record_login(user)

    return RedirectResponse(url=request.url_for("me"))