from enum import Enum
from dataclasses import dataclass


class Direction(Enum):
    """Elevator direction enum."""
    UP = "up"
    DOWN = "down"
    IDLE = "idle"


class RequestType(Enum):
    """Type of elevator request."""
    INTERNAL = "internal"  # From inside the elevator
    EXTERNAL = "external"  # From a floor button


@dataclass
class Request:
    """
    Represents an elevator request.
    """
    source_floor: int
    target_floor: int
    direction: Direction
    request_type: RequestType

    def __lt__(self, other):
        """For priority queue ordering."""
        # Prioritize internal requests
        if self.request_type != other.request_type:
            return self.request_type == RequestType.INTERNAL
        return self.source_floor < other.source_floor
