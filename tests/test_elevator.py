import pytest
from src.elevator import Elevator, ElevatorState, ZoneType
from src.request import Direction, Request, RequestType


@pytest.fixture
def elevator():
    return Elevator(id=1, zone=ZoneType.LOW_RISE)


def test_elevator_initialization(elevator):
    assert elevator.current_floor == 1
    assert elevator.direction == Direction.IDLE
    assert elevator.state == ElevatorState.IDLE
    assert not elevator.door_open
    assert len(elevator.target_floors) == 0
    assert elevator.zone == ZoneType.LOW_RISE
    assert elevator.floor_ranges[ZoneType.LOW_RISE] == (1, 20)


def test_elevator_move_up(elevator):
    elevator.direction = Direction.UP
    elevator.state = ElevatorState.MOVING
    elevator.move()
    assert elevator.current_floor == 2


def test_elevator_move_down(elevator):
    elevator.current_floor = 2
    elevator.direction = Direction.DOWN
    elevator.state = ElevatorState.MOVING
    elevator.move()
    assert elevator.current_floor == 1


def test_elevator_add_request(elevator):
    request = Request(
        source_floor=1,
        target_floor=5,
        direction=Direction.UP,
        request_type=RequestType.INTERNAL
    )
    assert elevator.add_request(request)
    assert 5 in elevator.target_floors

    # Test zone restrictions
    out_of_zone_request = Request(
        source_floor=1,
        target_floor=30,  # Mid-rise zone
        direction=Direction.UP,
        request_type=RequestType.INTERNAL
    )
    assert not elevator.add_request(out_of_zone_request)
    assert 30 not in elevator.target_floors


def test_elevator_should_stop(elevator):
    request = Request(
        source_floor=1,
        target_floor=3,
        direction=Direction.UP,
        request_type=RequestType.INTERNAL
    )
    elevator.add_request(request)
    elevator.current_floor = 3
    assert elevator.should_stop()


def test_elevator_door_operations(elevator):
    # Door operations are now state-based
    elevator.state = ElevatorState.DOOR_OPENING
    assert elevator.door_open  # Property checks for DOOR_OPENING and DOOR_OPEN states
    
    elevator.state = ElevatorState.DOOR_OPEN
    assert elevator.door_open

    elevator.state = ElevatorState.DOOR_CLOSING
    assert not elevator.door_open

    elevator.state = ElevatorState.IDLE
    assert not elevator.door_open


def test_elevator_emergency_stop(elevator):
    elevator.direction = Direction.UP
    elevator.state = ElevatorState.MOVING
    
    elevator.emergency_stop()
    assert elevator.state == ElevatorState.EMERGENCY
    assert elevator.direction == Direction.IDLE
    assert len(elevator.target_floors) == 0

    elevator.resume_service()
    assert elevator.state == ElevatorState.IDLE


def test_elevator_weight_management(elevator):
    # Test weight limits
    assert elevator.current_weight == 0
    assert elevator.max_weight == 2200  # pounds

    # Add weight within limits
    elevator.current_weight = 500
    assert elevator.current_weight == 500

    # Add more weight
    elevator.current_weight = 900
    assert elevator.current_weight == 900

    # Set weight beyond limit (should cap at max_weight)
    elevator.current_weight = 2500
    assert elevator.current_weight == 2200


def test_elevator_zone_restrictions(elevator):
    # Test lobby access for all elevators
    assert elevator.can_serve_floor(1)  # Lobby should be accessible

    # Test in-zone floors
    assert elevator.can_serve_floor(5)  # Low-rise zone
    assert elevator.can_serve_floor(15)  # Low-rise zone

    # Test out-of-zone floors
    assert not elevator.can_serve_floor(25)  # Mid-rise zone
    assert not elevator.can_serve_floor(40)  # High-rise zone
