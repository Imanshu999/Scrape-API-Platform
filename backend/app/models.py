from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    email: Mapped[str]=mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    created_at: Mapped[datetime]=mapped_column(DateTime, default=utcnow)

class ApiKey(Base):
    __tablename__="api_keys"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    user_id: Mapped[int]=mapped_column(Integer, index=True)
    key_hash: Mapped[str]=mapped_column(String(64), unique=True, index=True)
    active: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=utcnow)

class ScrapeCache(Base):
    __tablename__="scrape_cache"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    url: Mapped[str]=mapped_column(Text, unique=True, index=True)
    title: Mapped[str|None]=mapped_column(Text, nullable=True)
    description: Mapped[str|None]=mapped_column(Text, nullable=True)
    image: Mapped[str|None]=mapped_column(Text, nullable=True)
    data_json: Mapped[str]=mapped_column(Text, default="{}")
    updated_at: Mapped[datetime]=mapped_column(DateTime, default=utcnow)

class Source(Base):
    __tablename__="sources"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    user_id: Mapped[int]=mapped_column(Integer, index=True)
    url: Mapped[str]=mapped_column(Text, unique=True, index=True)
    active: Mapped[bool]=mapped_column(Boolean, default=True)
    max_pages: Mapped[int]=mapped_column(Integer, default=25)
    max_depth: Mapped[int]=mapped_column(Integer, default=2)
    refresh_minutes: Mapped[int]=mapped_column(Integer, default=60)
    last_status: Mapped[str]=mapped_column(String(32), default="pending")
    last_error: Mapped[str|None]=mapped_column(Text, nullable=True)
    last_synced_at: Mapped[datetime|None]=mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=utcnow)
