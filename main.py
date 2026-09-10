import os
from fastapi import FastAPI
from dotenv import load_dotenv
from routes import users, auth, admin
from starlette.middleware.sessions import SessionMiddleware
from db import init_db

# Load .env
load_dotenv()

# Initiate FastAPI and SQLite database
app = FastAPI()
init_db()

# Add middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET"),
)

# Setup routes
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(admin.router)