from sqlalchemy import Column, String, Integer, Float, JSON, Boolean, DateTime
from datetime import datetime, timezone
from .database import Base

class GatewaySession(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, default="recording")
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)
    synced = Column(Boolean, default=False)

class NormalizedEvent(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True)
    event_id = Column(String, unique=True, index=True)
    event_type = Column(String) # 'stroke', 'bookmark'
    payload = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    synced = Column(Boolean, default=False)
    sync_attempts = Column(Integer, default=0)
    last_sync_error = Column(String, nullable=True)
