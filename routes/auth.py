import os
from urllib import request

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request
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
        return {"message": "You are not logged in"}

    user = get_user_by_id(request.session["user_id"])
    if user is not None:
        log_activity(
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

    user = User(
        google_id= userinfo["sub"],
        username= userinfo["name"],
        email= userinfo["email"],
    )

    existing_user = get_user_by_google_id(user.google_id)
    if existing_user is None:
        add_user(user)
        existing_user = get_user_by_google_id(user.google_id)

    # Save user to session and log
    request.session["user_id"] = existing_user.id
    log_activity(existing_user.id, "login", f"{existing_user.username} logged in")

    return RedirectResponse(url=request.url_for("me"))


