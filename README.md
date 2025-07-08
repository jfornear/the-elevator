# Elevator System Simulator

An elevator system simulator that models real-world building elevator operations, featuring multiple elevators with zone-based operations and intelligent request handling.

## Overview

The system simulates a modern office building's elevator system with:
- 6 elevators serving 50 floors
- Zone-based operation (Low/Mid/High-rise)
- Real-time visualization
- RESTful API for control and monitoring
- Intelligent request handling and dispatch
- Comprehensive safety features

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone https://github.com/jfornear/the-elevator.git
   cd the-elevator
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

2. **Run the Demo**
   ```bash
   python run_demo.py
   ```
   This will start both the API server and the visualization demo.

3. **API Documentation**
   Once running, visit:
   ```
   http://localhost:8080/docs
   ```
   For interactive API documentation and testing interface.

## Features

### 1. Core System Features
- **Multi-Elevator Management**
  - 6 elevators serving 50 floors
  - Zone-based operation (Low/Mid/High-rise zones)
  - Real-time elevator status tracking
  - Emergency stop and resume functionality
  - Comprehensive logging system

### 2. Smart Request Handling
- **Request Types**
  - Internal requests (from inside elevators)
  - External requests (from floor buttons)
  - Zone-based request distribution
  - Direction-based optimization
  - Special lobby (floor 1) handling for all elevators

- **Intelligent Dispatch**
  - Zone-aware elevator assignment
  - Direction-optimized routing
  - Load balancing across elevators
  - Priority-based request queue
  - Efficient request merging for same-direction trips

### 3. State Management
- **Elevator States**
  - IDLE: Ready for new requests
  - MOVING: Traveling between floors
  - DOOR_OPENING: Door opening cycle
  - DOOR_OPEN: Door fully open
  - DOOR_CLOSING: Door closing cycle
  - EMERGENCY: Emergency stop mode

- **Safety Features**
  - Zone restrictions enforcement
  - Emergency stop capability
  - Door operation safety timers
  - Weight limit monitoring (2200 pounds max)
  - Invalid request rejection

### 4. API Integration
- **RESTful Endpoints**
  ```
  GET /system/status          # Get status of all elevators
  GET /elevator/{id}/status   # Get specific elevator status
  POST /elevator/{id}/request # Send internal request
  POST /floor/{number}/request # Send external request
  GET /system/statistics      # Get system statistics
  POST /system/emergency      # Trigger emergency mode
  ```

- **Interactive Documentation**
  - Swagger UI at `/docs`
  - OpenAPI schema at `/openapi.json`
  - Try endpoints directly in browser
  - Detailed request/response schemas
  - Authentication (if configured)

### 5. Visualization
The system provides a real-time ASCII visualization:
```
========================================
         Elevator System - 14:30
========================================
Elevator Status:
#1: Floor 15 ↑ [Moving]    Zone: Low-Rise
#2: Floor 8  ↓ [Idle]     Zone: Low-Rise
#3: Floor 25 ↑ [Moving]    Zone: Mid-Rise
#4: Floor 1  - [Door Open] Zone: Mid-Rise
#5: Floor 30 ↓ [Moving]    Zone: High-Rise
#6: Floor 40 ↑ [Moving]    Zone: High-Rise

50 |                  [E6]
49 |                   *
48 |
...
30 |                  [E5]
...
25 |         [E3]
...
15 |   [E1]
...
08 |      [E2]
...
01 |            [E4]
========================================
```

## Development

### Project Structure
```
elevator/
├── src/
│   ├── elevator.py         # Core elevator logic
│   ├── elevator_system.py  # System coordination
│   ├── api.py             # REST API endpoints
│   ├── floor.py           # Floor management
│   ├── request.py         # Request handling
│   ├── visualizer.py      # ASCII visualization
│   ├── logger.py          # Logging system
│   └── demo.py            # Demo scenarios
├── tests/
│   ├── test_elevator.py   # Elevator unit tests
│   └── test_system.py     # System integration tests
├── run_api.py             # API server runner
├── run_demo.py            # Demo runner
└── requirements.txt       # Dependencies
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_elevator.py

# Run with coverage
pytest --cov=src tests/
```

### Demo Scenarios
The system simulates typical office building traffic patterns:
- Morning rush (8:00-10:00): Up traffic
- Lunch rush (11:00-14:00): Mixed traffic
- Evening rush (16:00-18:00): Down traffic
- Regular hours: Distributed traffic

## Future Improvements

### Priority Enhancements
- **Configurable Building Setup**
  - Adjustable number of elevators and floors
  - Customizable zone assignments
  - Basic speed and capacity settings

- **Core Safety Features**
  - Emergency stop improvements
  - Door safety enhancements
  - Weight limit monitoring

- **Basic Traffic Optimization**
  - Peak time handling
  - Improved request grouping
  - Energy efficiency mode

These represent the highest-priority improvements that would enhance the system's flexibility, safety, and efficiency.

