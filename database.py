from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone

from config import DATABASE_URL

sync_url = DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
engine = create_engine(sync_url, echo=False)
SessionLocal = sessionmaker(bind=engine)
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


class VKSettings(Base):
    __tablename__ = "vk_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String(128), default="")
    client_secret = Column(String(256), default="")
    access_token = Column(String(512), default="")
    token_expires = Column(DateTime, nullable=True)


def init_db():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        settings = session.get(Settings, 1)
        if settings is None:
            session.add(Settings(id=1))
            session.commit()
    finally:
        session.close()


def get_settings(session) -> Settings:
    settings = session.get(Settings, 1)
    if settings is None:
        settings = Settings(id=1)
        session.add(settings)
        session.commit()
    return settings


def get_vk_settings(session) -> VKSettings:
    vk = session.query(VKSettings).first()
    if vk is None:
        vk = VKSettings()
        session.add(vk)
        session.commit()
    return vk
