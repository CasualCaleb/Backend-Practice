import os
from dotenv import load_dotenv

load_dotenv()

SESSION_SECRET=os.getenv("SESSION_SECRET")

GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")

DISCORD_CLIENT_ID=os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET=os.getenv("DISCORD_CLIENT_SECRET")

if SESSION_SECRET is None:
    raise RuntimeError("SESSION_SECRET not set")

if GOOGLE_CLIENT_ID is None:
    raise RuntimeError("GOOGLE_CLIENT_ID not set")

if GOOGLE_CLIENT_SECRET is None:
    raise RuntimeError("GOOGLE_CLIENT_SECRET not set")

if DISCORD_CLIENT_ID is None:
    raise RuntimeError("DISCORD_CLIENT_ID not set")

if DISCORD_CLIENT_SECRET is None:
    raise RuntimeError("DISCORD_CLIENT_SECRET not set")