# Elevator System Architecture

This document outlines the architecture of the elevator system, including component relationships, data flow, and state management.

## System Components

```mermaid
classDiagram
    class ElevatorSystem {
        +List~Elevator~ elevators
        +List~Floor~ floors
        +PriorityQueue~Request~ request_queue
        +step()
        +add_external_request()
        +add_internal_request()
        +emergency_stop()
        +resume_service()
    }
    
    class Elevator {
        +int id
        +ZoneType zone
        +int current_floor
        +Dict~int,Direction~ target_floors
        +Direction direction
        +ElevatorState state
        +move()
        +add_request()
        +can_serve_floor()
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
    
    ElevatorSystem "1" *-- "many" Elevator : manages
    ElevatorSystem "1" *-- "many" Floor : contains
    ElevatorSystem "1" *-- "many" Request : processes
    Elevator "1" -- "many" Request : handles
    Floor "1" -- "many" Request : creates
```

## Request Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant System
    participant Elevator
    participant Floor
    
    User->>API: Request elevator
    API->>System: add_external_request()
    System->>Floor: Create request
    Floor-->>System: Return request
    System->>System: Find best elevator
    System->>Elevator: Add request
    Elevator-->>System: Confirm request
    System-->>API: Request status
    API-->>User: Response
    
    loop Every step
        System->>Elevator: Update state
        Elevator->>Elevator: Move/change state
        Elevator-->>System: Report status
    end
```

## State Management

```mermaid
stateDiagram-v2
    [*] --> IDLE
    
    IDLE --> MOVING: Has targets
    MOVING --> DOOR_OPENING: At target floor
    DOOR_OPENING --> DOOR_OPEN: Timer complete
    DOOR_OPEN --> DOOR_CLOSING: Timer complete
    DOOR_CLOSING --> IDLE: Timer complete
    
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
    subgraph High-Rise[High-Rise Zone]
        F50[Floor 50] --> F36[Floor 36]
        E5[Elevator 5]
        E6[Elevator 6]
    end
    
    subgraph Mid-Rise[Mid-Rise Zone]
        F35[Floor 35] --> F21[Floor 21]
        E3[Elevator 3]
        E4[Elevator 4]
    end
    
    subgraph Low-Rise[Low-Rise Zone]
        F20[Floor 20] --> F1[Floor 1]
        E1[Elevator 1]
        E2[Elevator 2]
    end
    
    style High-Rise fill:#f9f,stroke:#333
    style Mid-Rise fill:#bbf,stroke:#333
    style Low-Rise fill:#bfb,stroke:#333
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
    end
    
    subgraph System
        SYSTEM[ElevatorSystem]
        CACHE[Status Cache]
    end
    
    GET_STATUS --> CACHE
    CACHE --> SYSTEM
    GET_ELEVATOR --> SYSTEM
    POST_ELEVATOR --> SYSTEM
    POST_FLOOR --> SYSTEM
    POST_EMERGENCY --> SYSTEM
```

## Key Components

1. **ElevatorSystem**
   - Central coordinator for all elevators
   - Manages request distribution
   - Handles zone-based operations
   - Coordinates emergency operations

2. **Elevator**
   - Manages individual elevator state
   - Handles movement and door operations
   - Maintains target floor queue
   - Enforces zone restrictions

3. **Floor**
   - Tracks button states
   - Creates elevator requests
   - Manages weight sensors
   - Handles direction indicators

4. **Request**
   - Represents elevator calls
   - Contains source and target floors
   - Specifies direction and type
   - Supports request prioritization

5. **API Layer**
   - Provides RESTful endpoints
   - Implements status caching
   - Handles real-time updates
   - Manages system control

## Implementation Notes

1. **State Management**
   - Each elevator maintains its own state
   - States include: IDLE, MOVING, DOOR_OPEN, DOOR_CLOSING, DOOR_OPENING, EMERGENCY
   - State transitions are timer-controlled for door operations

2. **Request Handling**
   - External requests come from floor buttons
   - Internal requests come from elevator buttons
   - Requests are prioritized based on type and direction
   - Zone restrictions are enforced during assignment

3. **Zone System**
   - Three zones: Low-rise, Mid-rise, High-rise
   - Two elevators per zone
   - All elevators can serve lobby (Floor 1)
   - Strict zone enforcement otherwise

4. **Safety Features**
   - Emergency stop capability
   - Weight limits
   - Door timing controls
   - Zone restrictions
   - Request validation 