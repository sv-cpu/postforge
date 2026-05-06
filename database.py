from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
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
    api_key = Column(String(512), default="")
    selected_group_id = Column(String(128), default="")


def init_db():
    Base.metadata.create_all(engine)
    # Migration: add selected_group_id column if not exists
    _migrate_db()
    session = SessionLocal()
    try:
        settings = session.get(Settings, 1)
        if settings is None:
            session.add(Settings(id=1))
            session.commit()
    finally:
        session.close()


def _migrate_db():
    """Add missing columns to existing tables"""
    with engine.connect() as conn:
        # Check if vk_settings.selected_group_id exists
        try:
            conn.execute(text("ALTER TABLE vk_settings ADD COLUMN selected_group_id VARCHAR(128) DEFAULT ''"))
            conn.commit()
            print("Migration: added selected_group_id to vk_settings")
        except Exception:
            pass  # Column already exists


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
