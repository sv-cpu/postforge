from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key = Column(String(512), default="")
    model = Column(String(128), default="openai/gpt-4o-mini")


class SavedPost(Base):
    __tablename__ = "saved_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_url = Column(String(2048), default="")
    tone = Column(String(32), default="friendly")
    model = Column(String(128), default="")
    content = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        result = await session.get(Settings, 1)
        if result is None:
            session.add(Settings(id=1))
            await session.commit()


async def get_settings(session: AsyncSession) -> Settings:
    settings = await session.get(Settings, 1)
    if settings is None:
        settings = Settings(id=1)
        session.add(settings)
        await session.commit()
    return settings
