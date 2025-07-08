from enum import Enum
from typing import Set, Dict, Optional, List
from .request import Direction, Request, RequestType


class ZoneType(Enum):
    """Elevator zone types."""
    LOW_RISE = "low_rise"     # Floors 1-20
    MID_RISE = "mid_rise"     # Floors 21-35
    HIGH_RISE = "high_rise"   # Floors 36-50


class ElevatorState(Enum):
    """Elevator operational states."""
    IDLE = "idle"
    MOVING = "moving"
    DOOR_OPEN = "door_open"
    DOOR_OPENING = "door_opening"
    DOOR_CLOSING = "door_closing"
    EMERGENCY = "emergency"


class Elevator:
    """
    Represents a single elevator car.
    """
    def __init__(self, id: int, zone: ZoneType):
        self.id = id
        self.zone = zone
        self.current_floor = 1
        self.target_floors: Dict[int, Direction] = {}  # floor -> direction
        self.direction = Direction.IDLE
        self.state = ElevatorState.IDLE
        self._current_weight = 0  # in pounds
        self.max_weight = 2200   # maximum 2200 pounds

        # Zone floor ranges
        self.floor_ranges = {
            ZoneType.LOW_RISE: (1, 20),
            ZoneType.MID_RISE: (21, 35),
            ZoneType.HIGH_RISE: (36, 50)
        }

    @property
    def door_open(self) -> bool:
        """Return True if doors are open or opening."""
        return self.state in [ElevatorState.DOOR_OPEN, ElevatorState.DOOR_OPENING]

    @property
    def current_weight(self) -> int:
        """Get current weight with safety limit."""
        return self._current_weight

    @current_weight.setter
    def current_weight(self, value: int) -> None:
        """Set current weight with safety limit."""
        self._current_weight = min(value, self.max_weight)

    def can_serve_floor(self, floor: int) -> bool:
        """Check if this elevator can serve the given floor based on its zone."""
        min_floor, max_floor = self.floor_ranges[self.zone]
        
        # Strict zone enforcement - only serve floors within zone
        # Exception: All elevators can serve floor 1 (lobby)
        if floor == 1:
            return True
            
        return min_floor <= floor <= max_floor

    def add_request(self, request: Request) -> bool:
        """Add a request. Returns False if floor is out of zone."""
        if not self.can_serve_floor(request.target_floor):
            return False
            
        # For internal requests, also check if current floor is in zone
        if request.request_type == RequestType.INTERNAL and not self.can_serve_floor(self.current_floor):
            return False
            
        self.target_floors[request.target_floor] = request.direction
        return True

    def move(self) -> None:
        """Move the elevator one floor in current direction."""
        if self.state != ElevatorState.MOVING:
            return
            
        if self.direction == Direction.UP:
            self.current_floor += 1
        elif self.direction == Direction.DOWN:
            self.current_floor -= 1

    def should_stop(self) -> bool:
        """Check if elevator should stop at current floor."""
        return self.current_floor in self.target_floors

    def emergency_stop(self) -> bool:
        """Trigger emergency stop."""
        self.state = ElevatorState.EMERGENCY
        self.direction = Direction.IDLE
        self.target_floors.clear()
        return True

    def resume_service(self) -> bool:
        """Resume normal operation after emergency."""
        if self.state == ElevatorState.EMERGENCY:
            self.state = ElevatorState.IDLE
            return True
        return False
