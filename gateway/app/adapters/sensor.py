from typing import Protocol, List
from ..models.events import Point
import uuid
from datetime import datetime, timezone

class SensorAdapter(Protocol):
    """
    Base protocol for any sensor providing board data.
    """
    def get_latest_points(self) -> List[Point]:
        ...

class SimulatedSensorAdapter:
    """
    Fully functional software-only simulator for local testing.
    Generates random smooth curves.
    """
    def __init__(self):
        self.points = []

    def get_latest_points(self) -> List[Point]:
        # return dummy points
        return self.points

class BleHolderAdapter:
    """
    Placeholder for future Bluetooth hardware holder.
    Do not implement fake BLE stacks.
    """
    def get_latest_points(self) -> List[Point]:
        raise NotImplementedError("Deferred to Phase 4")

class CornerClipUdpAdapter:
    """
    Placeholder for UDP TDOA corner clips.
    """
    def get_latest_points(self) -> List[Point]:
        raise NotImplementedError("Deferred to Phase 4")
