import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import Base, engine

async def init_db():
    async with engine.begin() as conn:
        # Drop all tables (use with caution!)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
