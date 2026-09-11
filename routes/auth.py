import os
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from models.user import User
from db import get_user_by_google_id, get_user_by_id, add_user, log_activity


router = APIRouter(prefix="/api/auth")

load_dotenv()
oauth = OAuth()

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.post("/logout")
async def logout(request: Request):
    if request.session.get("user_id") is None:
        raise HTTPException(
            status_code=401,
            detail="You have not logged in"
        )

    user = await get_user_by_id(request.session["user_id"])

    # Handle if existing_user is None or if id is None
    if user is None or user.id is None:
        request.session.clear()
        raise HTTPException(
            status_code=500,
            detail="Invalid session"
        )

    await log_activity(
        user.id,
        "logout",
        f"{user.username} logged out"
    )

    request.session.clear()
    return {"message": "You have been logged out"}

@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token['userinfo']

    user_data = User(
        google_id= userinfo["sub"],
        username= userinfo["name"],
        email= userinfo["email"],
    )

    user = await get_user_by_google_id(user_data.google_id)
    if user is None:
        await add_user(user_data)
        user = await get_user_by_google_id(user_data.google_id)

    # Handle if existing_user is None or if id is None
    if user is None or user.id is None:
        raise HTTPException(
            status_code=401,
            detail="User record is invalid"
        )

    # Save user to session and log
    request.session["user_id"] = user.id
    await log_activity(
        user.id,
        "login",
        f"{user.username} logged in"
    )

    return RedirectResponse(url=request.url_for("me"))


