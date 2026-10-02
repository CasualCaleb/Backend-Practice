from contextlib import asynccontextmanager
from pathlib import Path
import aiosqlite

DATABASE_PATH = Path(__file__).resolve().parent / "database.db"

@asynccontextmanager
async def get_connection():
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        await conn.execute("PRAGMA foreign_keys=ON")
        yield conn