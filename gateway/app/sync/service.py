import asyncio
import httpx
from sqlalchemy import select
from ..storage.database import AsyncSessionLocal
from ..storage.models import NormalizedEvent
from ..config import settings
import logging

logger = logging.getLogger(__name__)

async def sync_events_task():
    async with AsyncSessionLocal() as db:
        # Find unsynced events
        result = await db.execute(
            select(NormalizedEvent).where(NormalizedEvent.synced == False).limit(100)
        )
        events = result.scalars().all()

        if not events:
            return

        # Group by session
        sessions_to_sync = {}
        for event in events:
            if event.session_id not in sessions_to_sync:
                sessions_to_sync[event.session_id] = []
            sessions_to_sync[event.session_id].append(event)

        async with httpx.AsyncClient() as client:
            headers = {"X-Gateway-Auth": settings.GATEWAY_API_KEY}
            
            for session_id, session_events in sessions_to_sync.items():
                payload = {
                    "events": [
                        {**e.payload, "event_id": e.event_id, "type": e.event_type}
                        for e in session_events
                    ]
                }
                
                url = f"{settings.BACKEND_URL}/api/v1/sessions/{session_id}/sync/"
                try:
                    response = await client.post(url, json=payload, headers=headers)
                    if response.status_code == 200:
                        # Mark as synced
                        for e in session_events:
                            e.synced = True
                        logger.info(f"Successfully synced {len(session_events)} events for session {session_id}")
                    else:
                        logger.error(f"Failed to sync for session {session_id}. Status: {response.status_code}")
                        for e in session_events:
                            e.sync_attempts += 1
                            e.last_sync_error = response.text
                except Exception as ex:
                    logger.error(f"Network error syncing session {session_id}: {ex}")
                    for e in session_events:
                        e.sync_attempts += 1
                        e.last_sync_error = str(ex)
        
        await db.commit()
