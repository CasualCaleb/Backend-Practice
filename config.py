import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
SESSION_SECRET=os.getenv("SESSION_SECRET")

if GOOGLE_CLIENT_ID is None:
    raise RuntimeError("GOOGLE_CLIENT_ID not set")

if GOOGLE_CLIENT_SECRET is None:
    raise RuntimeError("GOOGLE_CLIENT_SECRET not set")

if SESSION_SECRET is None:
    raise RuntimeError("SESSION_SECRET not set")