from enum import Enum
import logging
from datetime import datetime
import os

class Direction(Enum):
    UP = "up"
    DOWN = "down"
    IDLE = "idle"

class ElevatorState(Enum):
    IDLE = "idle"
    MOVING = "moving"
    DOOR_OPENING = "door_opening"
    DOOR_OPEN = "door_open"
    DOOR_CLOSING = "door_closing"
    EMERGENCY = "emergency"

class Zone(Enum):
    LOW_RISE = "low_rise"
    MID_RISE = "mid_rise"
    HIGH_RISE = "high_rise"

class Elevator:
    def __init__(self, id, current_floor=1, zone=None, zone_range=None):
        self.id = id
        self.current_floor = current_floor
        self.direction = Direction.IDLE
        self.state = ElevatorState.IDLE
        self.targets = []
        self.zone = zone
        self.zone_range = zone_range
        self.door_timer = 0
        self._last_state = None  # For state change detection
        
    @property
    def door_open(self):
        """Return True if doors are open or opening."""
        return self.state in [ElevatorState.DOOR_OPEN, ElevatorState.DOOR_OPENING]

    def emergency_stop(self):
        """Trigger emergency stop."""
        self.state = ElevatorState.EMERGENCY
        self.direction = Direction.IDLE
        self.targets.clear()
        return True

    def resume_service(self):
        """Resume normal operation after emergency."""
        if self.state == ElevatorState.EMERGENCY:
            self.state = ElevatorState.IDLE
            return True
        return False

    def can_serve_floor(self, floor):
        # All elevators can serve floor 1 (lobby)
        if floor == 1:
            return True
        # Check if floor is within elevator's zone
        if self.zone_range:
            return self.zone_range[0] <= floor <= self.zone_range[1]
        return True

    def add_target(self, floor):
        """Add a target floor to the elevator's queue."""
        # Quick validation
        if not self.can_serve_floor(floor) or floor in self.targets:
            return False
            
        # Add target and sort based on direction
        self.targets.append(floor)
        if self.direction == Direction.DOWN:
            self.targets.sort(reverse=True)
        else:
            self.targets.sort()
            
        return True

    def update_direction(self):
        """Update elevator's direction based on current floor and targets."""
        if not self.targets:
            self.direction = Direction.IDLE
            return
            
        if self.direction == Direction.IDLE:
            # Starting new movement
            self.direction = Direction.UP if self.targets[0] > self.current_floor else Direction.DOWN
        elif self.direction == Direction.UP:
            # Check if we need to switch to down
            if all(t < self.current_floor for t in self.targets):
                self.direction = Direction.DOWN
                self.targets.sort(reverse=True)
        elif self.direction == Direction.DOWN:
            # Check if we need to switch to up
            if all(t > self.current_floor for t in self.targets):
                self.direction = Direction.UP
                self.targets.sort()

    def move(self):
        """Move the elevator one floor in current direction."""
        if self.state != ElevatorState.MOVING:
            return False
            
        # Move one floor
        if self.direction == Direction.UP:
            self.current_floor += 1
        elif self.direction == Direction.DOWN:
            self.current_floor -= 1
            
        return True

    def update(self):
        """Update elevator state and position."""
        # Skip update if in emergency
        if self.state == ElevatorState.EMERGENCY:
            return
            
        # Store previous state for change detection
        self._last_state = self.state
        
        if self.state == ElevatorState.IDLE:
            if self.targets:
                self.state = ElevatorState.MOVING
                self.update_direction()
                
        elif self.state == ElevatorState.MOVING:
            if self.current_floor in self.targets:
                self.state = ElevatorState.DOOR_OPENING
                self.door_timer = 2  # Reduced from 3 to 2 cycles
            else:
                self.move()
                
        elif self.state == ElevatorState.DOOR_OPENING:
            self.door_timer -= 1
            if self.door_timer <= 0:
                self.state = ElevatorState.DOOR_OPEN
                self.door_timer = 3  # Reduced from 5 to 3 cycles
                
        elif self.state == ElevatorState.DOOR_OPEN:
            self.door_timer -= 1
            if self.door_timer <= 0:
                self.state = ElevatorState.DOOR_CLOSING
                self.door_timer = 2  # Reduced from 3 to 2 cycles
                
        elif self.state == ElevatorState.DOOR_CLOSING:
            self.door_timer -= 1
            if self.door_timer <= 0:
                if self.current_floor in self.targets:
                    self.targets.remove(self.current_floor)
                self.state = ElevatorState.IDLE
                self.update_direction()
                
        # Update direction if state changed to idle
        if self._last_state != self.state and self.state == ElevatorState.IDLE:
            self.update_direction()

class ElevatorSystem:
    def __init__(self, num_floors=50, num_elevators=6):
        self.num_floors = num_floors
        self.elevators = []
        self.setup_logging()
        
        # Initialize elevators with zones
        for i in range(num_elevators):
            zone = None
            zone_range = None
            
            if i < 2:  # Elevators 1-2
                zone = Zone.LOW_RISE
                zone_range = (1, 20)
            elif i < 4:  # Elevators 3-4
                zone = Zone.MID_RISE
                zone_range = (21, 35)
            else:  # Elevators 5-6
                zone = Zone.HIGH_RISE
                zone_range = (36, 50)
            
            elevator = Elevator(i + 1, zone=zone, zone_range=zone_range)
            self.elevators.append(elevator)
            self.logger.info(f"Initialized E{elevator.id} - Zone: {zone.value}, Floors: {zone_range}")

    def setup_logging(self):
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Set up logging
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'logs/elevator_system_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file)  # Only write to file, not console
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("=== Starting New Elevator System Session ===")
        self.logger.info(f"Initializing system with {self.num_floors} floors and {len(self.elevators)} elevators")

    def find_elevator_for_floor(self, floor, direction=None):
        # Convert direction string to Direction enum if needed
        if isinstance(direction, str):
            direction = Direction(direction)

        # Quick return for invalid floors
        if floor < 1 or floor > self.num_floors:
            return None

        # Find elevators that can serve this floor
        eligible_elevators = [
            e for e in self.elevators 
            if e.can_serve_floor(floor) and e.state != ElevatorState.EMERGENCY
        ]
        
        if not eligible_elevators:
            return None
            
        # Find the best elevator based on various criteria
        best_elevator = None
        min_score = float('inf')
        
        for elevator in eligible_elevators:
            # Calculate base score (lower is better)
            score = abs(elevator.current_floor - floor) * 2  # Distance penalty
            
            # Penalize busy elevators
            score += len(elevator.targets) * 5
            
            # Special handling for floor 1 (lobby)
            if floor == 1:
                if elevator.current_floor == 1:
                    if elevator.state == ElevatorState.IDLE:
                        score = 0  # Best possible score for idle elevator at lobby
                    elif elevator.state != ElevatorState.MOVING:
                        score = 5  # Very good score for non-moving elevator at lobby
                elif 1 in elevator.targets:
                    score += 10  # Penalize if already going to lobby
            else:
                # Prefer elevators already moving in the right direction
                if direction and elevator.direction == direction:
                    if (direction == Direction.UP and elevator.current_floor < floor) or \
                       (direction == Direction.DOWN and elevator.current_floor > floor):
                        score -= 10  # Big bonus for moving in right direction
                
                # Prefer idle elevators
                if elevator.state == ElevatorState.IDLE:
                    score -= 5
                
                # Check if elevator is already serving nearby floors
                if elevator.targets:
                    nearest_target = min(elevator.targets, key=lambda t: abs(t - floor))
                    if abs(nearest_target - floor) <= 5:  # Within 5 floors
                        score -= 3  # Bonus for serving nearby floors
            
            if score < min_score:
                min_score = score
                best_elevator = elevator
        
        return best_elevator

    def add_external_request(self, floor, direction):
        """Add an external request (from floor button)."""
        # Quick validation
        if floor < 1 or floor > self.num_floors:
            return False
            
        # Convert direction string to enum if needed
        if isinstance(direction, str):
            direction = Direction(direction)
            
        # Don't allow up requests from top floor or down requests from lobby
        if (floor == self.num_floors and direction == Direction.UP) or \
           (floor == 1 and direction == Direction.DOWN):
            return False
            
        # Special handling for lobby (floor 1)
        if floor == 1:
            # Find any elevator already at lobby
            lobby_elevators = [e for e in self.elevators if e.current_floor == 1 and e.state == ElevatorState.IDLE]
            if lobby_elevators:
                return self.add_internal_request(lobby_elevators[0].id, floor)
                
            # Find any elevator already coming to lobby
            coming_to_lobby = [e for e in self.elevators if 1 in e.targets]
            if coming_to_lobby:
                return True  # Request already being served
        
        # Find best elevator for this request
        elevator = self.find_elevator_for_floor(floor, direction)
        if not elevator:
            return False
            
        # Add the floor to elevator's targets
        if elevator.add_target(floor):
            self.logger.info(f"REQUEST: External request F{floor} {direction.value} assigned to E{elevator.id}")
            self.logger.info(f"         Current floor: {elevator.current_floor}, Targets: {elevator.targets}")
            return True
            
        return False

    def add_internal_request(self, elevator_id, floor):
        """Add an internal request (from elevator button)."""
        # Quick validation
        if elevator_id < 1 or elevator_id > len(self.elevators) or \
           floor < 1 or floor > self.num_floors:
            return False
            
        elevator = self.elevators[elevator_id - 1]
        
        # Check if elevator can serve this floor
        if not elevator.can_serve_floor(floor):
            return False
            
        # Don't allow new requests in emergency mode
        if elevator.state == ElevatorState.EMERGENCY:
            return False
            
        # Add the floor to elevator's targets
        if elevator.add_target(floor):
            self.logger.info(f"REQUEST: Internal request F{floor} assigned to E{elevator_id}")
            self.logger.info(f"         Current floor: {elevator.current_floor}, Targets: {elevator.targets}")
            return True
            
        return False

    def emergency_stop(self):
        """Trigger emergency stop for all elevators."""
        for elevator in self.elevators:
            elevator.emergency_stop()
        return True

    def resume_service(self):
        """Resume normal operation after emergency."""
        success = True
        for elevator in self.elevators:
            if not elevator.resume_service():
                success = False
        return success

    def update(self):
        for elevator in self.elevators:
            old_state = elevator.state
            old_floor = elevator.current_floor
            old_direction = elevator.direction
            
            elevator.update()
            
            # Log state changes
            if elevator.state != old_state:
                if elevator.state == ElevatorState.DOOR_OPENING:
                    # Only log door opening if we're actually serving a request
                    if elevator.current_floor in elevator.targets:
                        self.logger.info(f"STATE: E{elevator.id} at F{elevator.current_floor} changed {old_state.value}→{elevator.state.value}\n       Direction: {elevator.direction.value}")
                        self.logger.info(f"STOP: E{elevator.id} at F{elevator.current_floor} ({elevator.direction.value})\n      Reason: Serving request\n      Targets: {elevator.targets}")
                elif elevator.state == ElevatorState.DOOR_OPEN:
                    # Only log door open if we're actually serving a request
                    if elevator.current_floor in elevator.targets:
                        self.logger.info(f"STATE: E{elevator.id} at F{elevator.current_floor} changed {old_state.value}→{elevator.state.value}\n       Direction: {elevator.direction.value}")
                        self.logger.info(f"DOORS: E{elevator.id} F{elevator.current_floor} - Doors fully open\n       Targets: {elevator.targets}")
                elif elevator.state == ElevatorState.DOOR_CLOSING:
                    # Only log door closing if we were serving a request
                    if elevator.current_floor in elevator.targets:
                        self.logger.info(f"STATE: E{elevator.id} at F{elevator.current_floor} changed {old_state.value}→{elevator.state.value}\n       Direction: {elevator.direction.value}")
                        self.logger.info(f"DOORS: E{elevator.id} F{elevator.current_floor} - Starting to close doors\n       Targets: {elevator.targets}")
                        self.logger.info(f"COMPLETED: E{elevator.id} F{elevator.current_floor} {elevator.direction.value} request\n          Remaining targets: {[t for t in elevator.targets if t != elevator.current_floor]}")
                else:
                    self.logger.info(f"STATE: E{elevator.id} at F{elevator.current_floor} changed {old_state.value}→{elevator.state.value}\n       Direction: {elevator.direction.value}")
            
            # Log direction changes
            if elevator.direction != old_direction:
                self.logger.info(f"DIRECTION: E{elevator.id} at F{elevator.current_floor} changed {old_direction.value}→{elevator.direction.value}\n          Targets: {elevator.targets}")
            
            # Log movements
            if elevator.current_floor != old_floor:
                self.logger.info(f"MOVE: E{elevator.id} {elevator.direction.value} F{old_floor}→F{elevator.current_floor}\n      Targets: {elevator.targets}")
            
            # Log request completions
            if old_state == ElevatorState.DOOR_CLOSING and elevator.state == ElevatorState.MOVING:
                if old_floor in elevator.targets:
                    self.logger.info(f"COMPLETED: E{elevator.id} F{old_floor} {elevator.direction.value} request\n          Remaining targets: {[t for t in elevator.targets if t != old_floor]}") 