from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator, Any
from app.core.config import settings

engine_options: dict[str, Any] = {
    "echo": settings.DEBUG,
    "future": True,
}

# Force UTC at the DB session level for asyncpg/PostgreSQL connections.
if settings.DATABASE_URL.startswith("postgresql+asyncpg"):
    engine_options["connect_args"] = {"server_settings": {"timezone": "UTC"}}

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, **engine_options)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
