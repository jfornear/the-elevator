# Elevator System Architecture

This document outlines the architecture of the elevator system, including component relationships, data flow, and state management.

## System Components

```mermaid
classDiagram
    class ElevatorSystem {
        +List~Elevator~ elevators
        +List~Floor~ floors
        +PriorityQueue~Request~ request_queue
        +ElevatorLogger logger
        +step()
        +add_external_request()
        +add_internal_request()
        +emergency_stop()
        +resume_service()
        +find_elevator_for_floor()
    }
    
    class Elevator {
        +int id
        +ZoneType zone
        +int current_floor
        +Dict~int,Direction~ target_floors
        +Direction direction
        +ElevatorState state
        +int _current_weight
        +int max_weight
        +move()
        +add_request()
        +can_serve_floor()
        +emergency_stop()
        +resume_service()
    }
    
    class Floor {
        +int floor_number
        +bool up_button_pressed
        +bool down_button_pressed
        +Dict~int,float~ weight_sensors
        +request_elevator()
        +clear_button()
    }
    
    class Request {
        +int source_floor
        +int target_floor
        +Direction direction
        +RequestType request_type
    }

    class ElevatorLogger {
        +Logger logger
        +log_system_init()
        +log_elevator_init()
        +log_request_assignment()
        +log_request_rejected()
    }

    class FastAPI_App {
        +ElevatorSystem system
        +get_status()
        +get_elevator_status()
        +add_elevator_request()
        +add_floor_request()
        +emergency_stop()
    }
    
    ElevatorSystem "1" *-- "many" Elevator : manages
    ElevatorSystem "1" *-- "many" Floor : contains
    ElevatorSystem "1" *-- "many" Request : processes
    ElevatorSystem "1" *-- "1" ElevatorLogger : uses
    Elevator "1" -- "many" Request : handles
    Floor "1" -- "many" Request : creates
    FastAPI_App "1" -- "1" ElevatorSystem : controls
```

## Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant System
    participant Logger
    participant Elevator
    participant Floor
    
    Client->>API: POST /floor/{number}/request
    API->>System: add_external_request(floor, direction)
    System->>Floor: Create request
    Floor-->>System: Return request
    System->>System: find_elevator_for_floor()
    System->>Logger: Log request assignment
    System->>Elevator: add_request()
    Elevator-->>System: Confirm request
    System-->>API: Request status
    API-->>Client: Response
    
    loop Every system step
        System->>Elevator: Update state
        Elevator->>Elevator: Move/change state
        alt State changed
            Elevator-->>Logger: Log state change
        end
        Elevator-->>System: Report status
    end
```

## State Management

```mermaid
stateDiagram-v2
    [*] --> IDLE
    
    IDLE --> MOVING: Has targets
    MOVING --> DOOR_OPENING: At target floor
    DOOR_OPENING --> DOOR_OPEN: Timer complete (2 cycles)
    DOOR_OPEN --> DOOR_CLOSING: Timer complete (3 cycles)
    DOOR_CLOSING --> IDLE: Timer complete (2 cycles)
    
    state EMERGENCY {
        [*] --> Stopped
        Stopped --> [*]: Resume service
    }
    
    IDLE --> EMERGENCY: Emergency stop
    MOVING --> EMERGENCY: Emergency stop
    DOOR_OPENING --> EMERGENCY: Emergency stop
    DOOR_OPEN --> EMERGENCY: Emergency stop
    DOOR_CLOSING --> EMERGENCY: Emergency stop
    EMERGENCY --> IDLE: Resume service
```

## Zone Configuration

```mermaid
graph TD
    subgraph High-Rise[High-Rise Zone: E5, E6]
        F50[Floor 50] --> F36[Floor 36]
        style F50 fill:#f9f,stroke:#333
        style F36 fill:#f9f,stroke:#333
    end
    
    subgraph Mid-Rise[Mid-Rise Zone: E3, E4]
        F35[Floor 35] --> F21[Floor 21]
        style F35 fill:#bbf,stroke:#333
        style F21 fill:#bbf,stroke:#333
    end
    
    subgraph Low-Rise[Low-Rise Zone: E1, E2]
        F20[Floor 20] --> F1[Floor 1]
        style F20 fill:#bfb,stroke:#333
        style F1 fill:#bfb,stroke:#333
    end

    F1 --> Common[Floor 1 - Common to All Zones]
    style Common fill:#fff,stroke:#333,stroke-width:2px
```

## API Structure

```mermaid
graph LR
    subgraph API Endpoints
        GET_STATUS[/system/status]
        GET_ELEVATOR[/elevator/{id}/status]
        POST_ELEVATOR[/elevator/{id}/request]
        POST_FLOOR[/floor/{number}/request]
        POST_EMERGENCY[/system/emergency]
        RESUME[/system/resume]
    end
    
    subgraph System Components
        SYSTEM[ElevatorSystem]
        CACHE[Status Cache<br>TTL: 100ms]
        LOGGER[ElevatorLogger]
    end
    
    GET_STATUS --> CACHE
    CACHE --> SYSTEM
    GET_ELEVATOR --> SYSTEM
    POST_ELEVATOR --> SYSTEM
    POST_FLOOR --> SYSTEM
    POST_EMERGENCY --> SYSTEM
    RESUME --> SYSTEM
    
    SYSTEM --> LOGGER
```

## Key Components

1. **ElevatorSystem**
   - Central coordinator for all elevators
   - Manages request distribution using priority queue
   - Handles zone-based operations
   - Coordinates emergency operations
   - Maintains system-wide logging

2. **Elevator**
   - Manages individual elevator state
   - Handles movement and door operations
   - Maintains target floor queue
   - Enforces zone restrictions
   - Weight limit: 2200 pounds
   - Door timing controls

3. **Floor**
   - Tracks up/down button states
   - Creates elevator requests
   - Manages weight sensors
   - Handles direction indicators

4. **Request**
   - Represents elevator calls
   - Contains source and target floors
   - Specifies direction and type
   - Supports request prioritization
   - Internal requests have priority

5. **API Layer**
   - FastAPI implementation
   - Status caching (100ms TTL)
   - Request validation
   - Error handling
   - Swagger documentation

6. **Logger**
   - Session-based logging
   - State change tracking
   - Request logging
   - Error logging
   - Console and file output

## Implementation Notes

1. **State Management**
   - Each elevator maintains independent state
   - States: IDLE, MOVING, DOOR_OPEN, DOOR_CLOSING, DOOR_OPENING, EMERGENCY
   - Door operations use cycle-based timers:
     - Opening: 2 cycles
     - Open: 3 cycles
     - Closing: 2 cycles

2. **Request Handling**
   - External requests from floor buttons
   - Internal requests from elevator buttons
   - Priority queue for request management
   - Zone restrictions strictly enforced
   - Special handling for lobby (Floor 1)

3. **Zone System**
   - Three zones with two elevators each:
     - Low-rise: Floors 1-20 (E1, E2)
     - Mid-rise: Floors 21-35 (E3, E4)
     - High-rise: Floors 36-50 (E5, E6)
   - Floor 1 accessible by all elevators
   - Strict zone enforcement otherwise

4. **Safety Features**
   - Emergency stop capability
   - Weight limit monitoring
   - Door timing controls
   - Zone restrictions
   - Request validation
   - Comprehensive logging 