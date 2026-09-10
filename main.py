import os
from fastapi import FastAPI
from dotenv import load_dotenv
from routes import users, auth, admin
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET"),
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(admin.router)