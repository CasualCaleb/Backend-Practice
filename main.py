from fastapi import FastAPI
from routes import users, auth, admin
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from db import init_db
from config import SESSION_SECRET

# Initialize the database
@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Add middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
)

# Setup routes
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(admin.router)