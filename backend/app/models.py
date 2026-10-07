from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    email: Mapped[str]=mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    created_at: Mapped[datetime]=mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class ApiKey(Base):
    __tablename__="api_keys"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    user_id: Mapped[int]=mapped_column(Integer, index=True)
    key_hash: Mapped[str]=mapped_column(String(64), unique=True, index=True)
    active: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class ScrapeCache(Base):
    __tablename__="scrape_cache"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    url: Mapped[str]=mapped_column(Text, unique=True, index=True)
    title: Mapped[str|None]=mapped_column(Text, nullable=True)
    description: Mapped[str|None]=mapped_column(Text, nullable=True)
    image: Mapped[str|None]=mapped_column(Text, nullable=True)
    data_json: Mapped[str]=mapped_column(Text, default="{}")
    updated_at: Mapped[datetime]=mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
