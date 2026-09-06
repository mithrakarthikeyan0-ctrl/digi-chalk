from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..storage.database import get_db
from ..storage.models import GatewaySession, NormalizedEvent
from ..models.events import StrokeEvent, BookmarkEvent
from datetime import datetime, timezone
import uuid

from ..sync.service import sync_events_task
from sqlalchemy import select

router = APIRouter()

@router.get("/health/")
async def health_check():
    return {"status": "ok"}

@router.get("/status/")
async def gateway_status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NormalizedEvent).where(NormalizedEvent.synced == False))
    pending_events = len(result.scalars().all())
    return {"status": "online", "syncing": False, "pending_events": pending_events}

@router.post("/sync/now/")
async def sync_now():
    # In a real app this would be a background task, but for MVP we await it
    await sync_events_task()
    return {"status": "synced"}

@router.post("/sessions/")
async def start_session(classroom: str, status: str = "recording", db: AsyncSession = Depends(get_db)):
    session_id = str(uuid.uuid4())
    new_session = GatewaySession(id=session_id, status=status)
    db.add(new_session)
    await db.commit()
    return {"id": session_id, "status": status}

@router.post("/sessions/{session_id}/end/")
async def end_session(session_id: str, db: AsyncSession = Depends(get_db)):
    session = await db.get(GatewaySession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.status = "ended"
    session.ended_at = datetime.now(timezone.utc)
    session.synced = False
    await db.commit()
    return {"id": session_id, "status": "ended"}

@router.post("/simulate/stroke/")
async def simulate_stroke(event: StrokeEvent, db: AsyncSession = Depends(get_db)):
    new_event = NormalizedEvent(
        session_id=event.sessionId,
        event_id=event.strokeId,
        event_type="stroke",
        payload=event.model_dump()
    )
    db.add(new_event)
    await db.commit()
    return {"status": "ok", "event_id": event.strokeId}

@router.post("/sessions/{session_id}/bookmarks/")
async def add_bookmark(session_id: str, event: BookmarkEvent, db: AsyncSession = Depends(get_db)):
    # This matches Django's bookmark endpoint but also serves as the simulate_bookmark
    new_event = NormalizedEvent(
        session_id=session_id,
        event_id=str(uuid.uuid4()),
        event_type="bookmark",
        payload=event.model_dump()
    )
    db.add(new_event)
    await db.commit()
    return {"status": "ok", "event_id": new_event.event_id}

@router.get("/sessions/{session_id}/events/")
async def get_events(session_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(NormalizedEvent).where(NormalizedEvent.session_id == session_id).order_by(NormalizedEvent.created_at))
    events = result.scalars().all()
    return {"events": [e.payload for e in events]}
