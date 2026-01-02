from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

import settings

BaseModel = declarative_base()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

print("=== RUNTIME DATABASE_URL ===", settings.DATABASE_URL, flush=True)
import os
print("=== ENV DATABASE_URL ===", os.getenv("DATABASE_URL"), flush=True)
print("=== ENV POSTGRES_PASSWORD ===", repr(os.getenv("POSTGRES_PASSWORD")), flush=True)

Session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

