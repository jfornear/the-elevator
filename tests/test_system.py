import pytest
from src.system import ElevatorSystem
from src.elevator import ElevatorState, ZoneType
from src.request import Direction


@pytest.fixture
def system():
    return ElevatorSystem(num_floors=50)  # Default 50 floors, 6 elevators


def test_system_initialization(system):
    assert system.num_floors == 50
    assert len(system.floors) == 50
    assert len(system.elevators) == 6
    
    # Check zone distribution
    low_rise = [e for e in system.elevators if e.zone == ZoneType.LOW_RISE]
    mid_rise = [e for e in system.elevators if e.zone == ZoneType.MID_RISE]
    high_rise = [e for e in system.elevators if e.zone == ZoneType.HIGH_RISE]
    
    assert len(low_rise) == 2  # Elevators 1-2
    assert len(mid_rise) == 2  # Elevators 3-4
    assert len(high_rise) == 2  # Elevators 5-6


def test_add_internal_request(system):
    # Add valid request to low-rise elevator
    assert system.add_internal_request(1, 5)  # Elevator 1, floor 5
    assert 5 in system.elevators[0].target_floors

    # Add invalid request (floor out of range)
    assert not system.add_internal_request(1, 51)
    
    # Add request to wrong zone
    assert not system.add_internal_request(1, 40)  # Low-rise elevator can't serve high-rise floor


def test_add_external_request(system):
    # Add valid request for low-rise zone
    assert system.add_external_request(5, Direction.UP)
    # Should be assigned to one of the low-rise elevators
    assert any(5 in e.target_floors for e in system.elevators[:2])

    # Add valid request for mid-rise zone
    assert system.add_external_request(25, Direction.UP)
    # Should be assigned to one of the mid-rise elevators
    assert any(25 in e.target_floors for e in system.elevators[2:4])

    # Add invalid request (floor out of range)
    assert not system.add_external_request(51, Direction.UP)


def test_elevator_movement(system):
    # Request floor 5 from elevator 1
    system.add_internal_request(1, 5)
    elevator = system.elevators[0]

    # First step - transition to moving state
    system.step()
    assert elevator.state == ElevatorState.MOVING
    assert elevator.direction == Direction.UP
    assert elevator.current_floor == 1  # Still at starting floor

    # Second step - actual movement
    system.step()
    assert elevator.current_floor == 2

    # Run until reaching target
    while elevator.current_floor < 5:
        system.step()

    assert elevator.current_floor == 5
    assert elevator.state == ElevatorState.DOOR_OPENING


def test_system_status(system):
    system.add_internal_request(1, 5)  # Request for first elevator
    
    status = {
        "elevators": [{
            "id": e.id,
            "current_floor": e.current_floor,
            "direction": e.direction.value,
            "state": e.state.value,
            "target_floors": sorted(e.target_floors.keys()) if hasattr(e, 'target_floors') else [],
            "zone": e.zone.value
        } for e in system.elevators]
    }
    
    # Check first elevator's status
    elevator_status = status["elevators"][0]
    assert elevator_status["current_floor"] == 1
    assert elevator_status["direction"] == "idle"
    assert elevator_status["state"] == "idle"
    assert 5 in elevator_status["target_floors"]
    assert elevator_status["zone"] == "low_rise"


def test_multiple_requests(system):
    # Add multiple requests to different zones
    system.add_internal_request(1, 5)   # Low-rise
    system.add_external_request(25, Direction.UP)  # Mid-rise
    system.add_external_request(40, Direction.UP)  # High-rise

    # Check if requests are assigned to correct zones
    assert any(5 in e.target_floors for e in system.elevators[:2])  # Low-rise
    assert any(25 in e.target_floors for e in system.elevators[2:4])  # Mid-rise
    assert any(40 in e.target_floors for e in system.elevators[4:])  # High-rise


def test_lobby_access(system):
    # All elevators should be able to serve lobby (floor 1)
    for elevator in system.elevators:
        assert elevator.can_serve_floor(1)

    # Test lobby request assignment
    assert system.add_external_request(1, Direction.UP)
    # Should prefer idle elevator at lobby if available
    idle_at_lobby = [e for e in system.elevators if e.current_floor == 1 and e.state == ElevatorState.IDLE]
    if idle_at_lobby:
        assert 1 in idle_at_lobby[0].target_floors
