from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import uvicorn
import threading
import time
import logging

from .elevator_system import ElevatorSystem
from .elevator_system import ElevatorState

app = FastAPI(
    title="Elevator System API",
    description="API for controlling and monitoring a multi-elevator system",
    version="1.0.0"
)

# Initialize the elevator system
system = ElevatorSystem(num_floors=50, num_elevators=6)

# Cache for system status
_status_cache = None
_last_update_time = 0
_cache_ttl = 0.1  # 100ms TTL

# Set up console logging
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger = logging.getLogger("elevator_api")
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log API requests to console."""
    if not request.url.path.endswith("/system/status"):  # Skip logging status requests
        logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response

# Background update task
def update_system():
    global _status_cache, _last_update_time
    while True:
        current_time = time.time()
        
        # Update system
        system.update()
        
        # Update cache if TTL expired
        if current_time - _last_update_time >= _cache_ttl:
            _status_cache = {
                "elevators": [{
                    "id": e.id,
                    "current_floor": e.current_floor,
                    "direction": e.direction.value,
                    "state": e.state.value,
                    "target_floors": e.targets,
                    "door_open": e.door_open,
                    "zone": e.zone.value if e.zone else None,
                    "zone_range": e.zone_range
                } for e in system.elevators]
            }
            _last_update_time = current_time
            
        time.sleep(0.05)  # Update every 50ms

# Start background update thread
update_thread = threading.Thread(target=update_system, daemon=True)
update_thread.start()

@app.get("/")
async def root():
    """Root endpoint showing API information."""
    return {
        "name": "Elevator System API",
        "version": "1.0.0",
        "description": "API for controlling and monitoring a multi-elevator system",
        "documentation": "/docs",
        "endpoints": {
            "GET /": "This information",
            "GET /system/status": "Get status of all elevators",
            "GET /elevator/{id}/status": "Get status of specific elevator",
            "POST /elevator/{id}/request": "Add internal request for specific elevator",
            "POST /floor/{number}/request": "Add external request from a floor",
            "GET /system/statistics": "Get system statistics",
            "POST /system/emergency": "Trigger emergency mode"
        }
    }

class DirectionEnum(str, Enum):
    UP = "up"
    DOWN = "down"
    IDLE = "idle"

class ElevatorRequest(BaseModel):
    target_floor: int
    direction: Optional[DirectionEnum] = None  # Make direction optional

class ElevatorStatus(BaseModel):
    id: int
    current_floor: int
    direction: str
    state: str
    target_floors: List[int]
    door_open: bool
    zone: Optional[str] = None
    zone_range: Optional[tuple] = None

class SystemStatus(BaseModel):
    elevators: List[ElevatorStatus]

@app.get("/system/status", response_model=SystemStatus)
async def get_system_status():
    """Get the current status of all elevators in the system."""
    global _status_cache
    return _status_cache or {
        "elevators": [{
            "id": e.id,
            "current_floor": e.current_floor,
            "direction": e.direction.value,
            "state": e.state.value,
            "target_floors": e.targets,
            "door_open": e.door_open,
            "zone": e.zone.value if e.zone else None,
            "zone_range": e.zone_range
        } for e in system.elevators]
    }

@app.get("/elevator/{elevator_id}/status", response_model=ElevatorStatus)
async def get_elevator_status(elevator_id: int):
    """Get the status of a specific elevator."""
    if elevator_id < 1 or elevator_id > len(system.elevators):
        raise HTTPException(status_code=404, detail="Elevator not found")
    
    elevator = system.elevators[elevator_id - 1]
    return {
        "id": elevator.id,
        "current_floor": elevator.current_floor,
        "direction": elevator.direction.value,
        "state": elevator.state.value,
        "target_floors": elevator.targets,
        "door_open": elevator.door_open,
        "zone": elevator.zone.value if elevator.zone else None,
        "zone_range": elevator.zone_range
    }

@app.post("/elevator/{elevator_id}/request")
async def add_elevator_request(elevator_id: int, request: ElevatorRequest):
    """Add a request for a specific elevator (internal request)."""
    if elevator_id < 1 or elevator_id > len(system.elevators):
        raise HTTPException(status_code=404, detail="Elevator not found")
    
    if request.target_floor < 1 or request.target_floor > system.num_floors:
        raise HTTPException(status_code=400, detail="Invalid floor number")
    
    elevator = system.elevators[elevator_id - 1]
    if not elevator.can_serve_floor(request.target_floor):
        raise HTTPException(
            status_code=400, 
            detail=f"Elevator {elevator_id} cannot serve floor {request.target_floor} (zone: {elevator.zone.value}, range: {elevator.zone_range})"
        )
    
    if elevator.state == ElevatorState.EMERGENCY:
        raise HTTPException(
            status_code=400,
            detail=f"Elevator {elevator_id} is in emergency mode"
        )
    
    success = system.add_internal_request(elevator_id, request.target_floor)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail=f"Could not add request - Elevator {elevator_id} is busy or request conflicts with current direction"
        )
    
    return {"message": "Request added successfully"}

@app.post("/floor/{floor_number}/request")
async def add_floor_request(floor_number: int, direction: DirectionEnum):
    """Add a request from a floor (external request)."""
    if floor_number < 1 or floor_number > system.num_floors:
        raise HTTPException(status_code=400, detail="Invalid floor number")
    
    # Don't allow up requests from top floor or down requests from lobby
    if (floor_number == system.num_floors and direction == DirectionEnum.UP) or \
       (floor_number == 1 and direction == DirectionEnum.DOWN):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid direction {direction} for floor {floor_number}"
        )
    
    # For floor 1 (lobby), we'll let the elevator system handle the special cases
    if floor_number == 1:
        success = system.add_external_request(floor_number, direction.value)
        if success:
            return {"message": "Lobby request added successfully"}
        else:
            # Check elevator states to provide better error messages
            coming_to_lobby = [e for e in system.elevators if 1 in e.targets]
            
            if coming_to_lobby:
                return {"message": f"Floor 1 is already being served by elevator {coming_to_lobby[0].id}"}
            elif all(e.state == ElevatorState.EMERGENCY for e in system.elevators):
                raise HTTPException(status_code=400, detail="All elevators are in emergency mode")
            else:
                # Check if any low-rise elevators are available
                low_rise_available = any(e.state != ElevatorState.EMERGENCY and e.zone == "low_rise" 
                                      for e in system.elevators)
                if not low_rise_available:
                    raise HTTPException(
                        status_code=400, 
                        detail="No low-rise elevators available to serve lobby at this time"
                    )
                else:
                    raise HTTPException(
                        status_code=400, 
                        detail="No elevators available to serve lobby at this time - all elevators are busy"
                    )
    
    # Check if there's already an elevator serving this floor in the same direction
    serving_elevator = None
    for elevator in system.elevators:
        if floor_number in elevator.targets:
            serving_elevator = elevator
            # If elevator is already serving this floor in the same direction, that's fine
            if elevator.direction.value == direction.value:
                return {"message": f"Floor {floor_number} is already being served by elevator {elevator.id} in direction {direction}"}
            break
    
    if serving_elevator:
        raise HTTPException(
            status_code=400,
            detail=f"Floor {floor_number} is already being served by elevator {serving_elevator.id} in direction {serving_elevator.direction.value}"
        )
    
    success = system.add_external_request(floor_number, direction.value)
    if not success:
        # Find elevators that could potentially serve this floor
        potential_elevators = [e for e in system.elevators if e.can_serve_floor(floor_number)]
        if not potential_elevators:
            detail = f"No elevators are configured to serve floor {floor_number}"
        else:
            busy_elevators = [e.id for e in potential_elevators if e.state != ElevatorState.IDLE]
            if busy_elevators:
                detail = f"All eligible elevators are busy: {busy_elevators}"
            else:
                detail = f"Could not add request - No available elevators can serve floor {floor_number} at this time"
        raise HTTPException(status_code=400, detail=detail)
    
    return {"message": "Request added successfully"}

@app.get("/system/statistics")
async def get_system_statistics():
    """Get system statistics like total requests handled, average wait time, etc."""
    return {
        "total_floors": system.num_floors,
        "total_elevators": len(system.elevators),
        "active_requests": sum(len(e.targets) for e in system.elevators)
    }

@app.post("/system/emergency")
async def trigger_emergency():
    """Trigger emergency mode for all elevators."""
    try:
        success = system.emergency_stop()
        if not success:
            raise HTTPException(status_code=500, detail="Failed to activate emergency mode")
        return {"message": "Emergency mode activated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/system/resume")
async def resume_service():
    """Resume normal operation after emergency."""
    try:
        success = system.resume_service()
        if not success:
            raise HTTPException(status_code=500, detail="Failed to resume service")
        return {"message": "Service resumed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_api(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server."""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_api() 