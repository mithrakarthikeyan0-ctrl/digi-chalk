from pydantic import BaseModel, Field
from typing import List

class Point(BaseModel):
    x: float
    y: float
    dt: int
    color: str

class StrokeEvent(BaseModel):
    type: str = "stroke"
    sessionId: str
    strokeId: str
    points: List[Point] = Field(..., max_items=500)

class BookmarkEvent(BaseModel):
    type: str = "bookmark"
    sessionId: str
    bookmarkId: str
    timestamp_seconds: float
    label: str
