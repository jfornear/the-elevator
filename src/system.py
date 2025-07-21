from typing import Dict
from queue import PriorityQueue

from .elevator import Elevator, ElevatorState, ZoneType
from .floor import Floor
from .request import Direction, Request, RequestType
from .logger import ElevatorLogger


class ElevatorSystem:
    """
    Manages multiple elevators across different zones in a building.
    """
    def __init__(self, num_floors: int = 50):
        self.num_floors = num_floors
        self.logger = ElevatorLogger()
        self.logger.log_system_init(num_floors, 6)  # 6 elevators total
        
        # Create elevators for each zone
        self.elevators = [
            # Low-rise zone (2 elevators)
            Elevator(id=1, zone=ZoneType.LOW_RISE),
            Elevator(id=2, zone=ZoneType.LOW_RISE),
            
            # Mid-rise zone (2 elevators)
            Elevator(id=3, zone=ZoneType.MID_RISE),
            Elevator(id=4, zone=ZoneType.MID_RISE),
            
            # High-rise zone (2 elevators)
            Elevator(id=5, zone=ZoneType.HIGH_RISE),
            Elevator(id=6, zone=ZoneType.HIGH_RISE),
        ]
        
        # Log elevator initialization
        for elevator in self.elevators:
            self.logger.log_elevator_init(
                elevator.id,
                elevator.zone.value,
                elevator.floor_ranges[elevator.zone]
            )
        
        self.floors = [Floor(i) for i in range(1, num_floors + 1)]
        self.request_queue: PriorityQueue[Request] = PriorityQueue()
        self.step_time = 0.05  # Time between steps in seconds (20x faster)

    def add_internal_request(self, elevator_id: int, target_floor: int) -> bool:
        """Add a request from inside a specific elevator."""
        if not (1 <= elevator_id <= len(self.elevators) and 1 <= target_floor <= self.num_floors):
            return False
            
        elevator = self.elevators[elevator_id - 1]
        
        # Create request
        request = Request(
            source_floor=elevator.current_floor,
            target_floor=target_floor,
            direction=Direction.UP if target_floor > elevator.current_floor else Direction.DOWN,
            request_type=RequestType.INTERNAL
        )
        
        if elevator.add_request(request):
            self.request_queue.put(request)
            # Don't set direction until elevator starts moving
            return True
            
        return False

    def add_external_request(self, floor: int, direction: Direction) -> bool:
        """Add a request from a floor button."""
        if not 1 <= floor <= self.num_floors:
            return False
            
        # Find appropriate zone for the floor
        target_zone = None
        if floor == 1:  # Lobby can be served by any elevator
            target_zone = ZoneType.LOW_RISE  # Prefer low-rise for lobby
        elif 1 <= floor <= 20:
            target_zone = ZoneType.LOW_RISE
        elif 21 <= floor <= 35:
            target_zone = ZoneType.MID_RISE
        else:
            target_zone = ZoneType.HIGH_RISE
            
        # Find best elevator in the zone
        best_elevator = None
        min_score = float('inf')
        
        for elevator in self.elevators:
            if elevator.zone == target_zone or floor == 1:  # Allow any elevator for lobby
                score = abs(elevator.current_floor - floor) * 2  # Distance penalty
                score += len(elevator.target_floors) * 3  # Busy penalty
                
                if elevator.direction == direction:  # Bonus for same direction
                    score -= 5
                    
                if score < min_score:
                    min_score = score
                    best_elevator = elevator
                    
        if not best_elevator:
            return False
            
        # Create request
        request = Request(
            source_floor=floor,
            target_floor=floor,
            direction=direction,
            request_type=RequestType.EXTERNAL
        )
        
        if best_elevator.add_request(request):
            self.request_queue.put(request)
            return True
            
        return False

    def step(self) -> None:
        """Process one step for all elevators."""
        for elevator in self.elevators:
            if elevator.state == ElevatorState.EMERGENCY:
                continue
                
            if elevator.state == ElevatorState.IDLE:
                if elevator.target_floors:
                    # Set direction before starting to move
                    next_floor = next(iter(elevator.target_floors))
                    elevator.direction = Direction.UP if next_floor > elevator.current_floor else Direction.DOWN
                    elevator.state = ElevatorState.MOVING
                    
            elif elevator.state == ElevatorState.MOVING:
                # Move first, then check if we should stop
                elevator.move()
                # After moving, check if we've reached a target floor
                if elevator.current_floor in elevator.target_floors:
                    elevator.state = ElevatorState.DOOR_OPENING
                    
            elif elevator.state == ElevatorState.DOOR_OPENING:
                elevator.state = ElevatorState.DOOR_OPEN
                
            elif elevator.state == ElevatorState.DOOR_OPEN:
                elevator.state = ElevatorState.DOOR_CLOSING
                
            elif elevator.state == ElevatorState.DOOR_CLOSING:
                if elevator.current_floor in elevator.target_floors:
                    del elevator.target_floors[elevator.current_floor]
                elevator.state = ElevatorState.IDLE
                if not elevator.target_floors:
                    elevator.direction = Direction.IDLE

    def get_status(self) -> Dict:
        """Get current system status."""
        return {
            "elevators": [{
                "id": e.id,
                "current_floor": e.current_floor,
                "direction": e.direction.value,
                "state": e.state.value,
                "target_floors": sorted(e.target_floors.keys()),
                "zone": e.zone.value,
                "door_open": e.door_open
            } for e in self.elevators]
        }
