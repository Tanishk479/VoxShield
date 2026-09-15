import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import async_sessionmaker, engine
from db.models import User
from passlib.context import CryptContext
from sqlalchemy import select

# Standard FastAPI Bcrypt context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def fix_password():
    print("[*] Connecting to database...")
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as db:
        stmt = select(User).where(User.email == "demo@voxshield.in")
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if user:
            # Hash the password correctly using bcrypt
            user.hashed_password = pwd_context.hash("VoxShieldDemo2026!")
            await db.commit()
            print("[✓] Success! Password hash updated to Bcrypt format.")
        else:
            print("[!] User demo@voxshield.in not found.")

if __name__ == "__main__":
    asyncio.run(fix_password())