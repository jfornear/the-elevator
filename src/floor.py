from typing import Optional, Dict
from .request import Direction, Request, RequestType


class Floor:
    """
    Represents a floor in the building.
    """
    def __init__(self, floor_number: int):
        self.floor_number = floor_number
        self.up_button_pressed = False
        self.down_button_pressed = False
        self.weight_sensors: Dict[int, float] = {}  # elevator_id -> weight

    def request_elevator(self, direction: Direction) -> Optional[Request]:
        """
        Create a request from this floor.
        Returns None if a request in that direction already exists.
        """
        if direction == Direction.UP and not self.up_button_pressed:
            self.up_button_pressed = True
            return Request(self.floor_number, self.floor_number, direction, RequestType.EXTERNAL)
        elif direction == Direction.DOWN and not self.down_button_pressed:
            self.down_button_pressed = True
            return Request(self.floor_number, self.floor_number, direction, RequestType.EXTERNAL)
        return None

    def clear_button(self, direction: Direction) -> None:
        """Clear the button press for the given direction."""
        if direction == Direction.UP:
            self.up_button_pressed = False
        elif direction == Direction.DOWN:
            self.down_button_pressed = False
