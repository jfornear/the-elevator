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
================================================================================
                           Elevator System - 19:47:15
================================================================================
Elevator Status:
#1: Floor 1, Direction: idle, State: idle, Weight: 0lbs, Targets: []
#2: Floor 1, Direction: idle, State: idle, Weight: 0lbs, Targets: []
#3: Floor 1, Direction: idle, State: idle, Weight: 0lbs, Targets: []
#4: Floor 1, Direction: idle, State: idle, Weight: 0lbs, Targets: []
#5: Floor 32, Direction: up, State: moving, Weight: 0lbs, Targets: [42]
#6: Floor 21, Direction: up, State: moving, Weight: 0lbs, Targets: [43]
--------------------------------------------------------------------------------
50 |                                                                          
49 |                                                                          
48 |                                                                          
47 |                                                                          
46 |                                                                          
45 |                                                                          
44 |                                                                          
43 |                                             *                            
42 |                                     *                                    
41 |                                                                          
40 |                                                                          
39 |                                                                          
38 |                                                                          
37 |                                                                          
36 |                                                                          
35 |                                                                          
34 |                                                                          
33 |                                                                          
32 |                                  [E5||||]                               ↑
31 |                                                                          
30 |                                                                          
29 |                                                                          
28 |                                                                          
27 |                                                                          
26 |                                                                          
25 |                                                                          
24 |                                                                          
23 |                                                                          
22 |                                                                          
21 |                                          [E6||||]                       ↑
20 |                                                                          
19 |                                                                          
18 |                                                                          
17 |                                                                          
16 |                                                                          
15 |                                                                          
14 |                                                                          
13 |                                                                          
12 |                                                                          
11 |                                                                          
10 |                                                                          
 9 |                                                                          
 8 |                                                                          
 7 |                                                                          
 6 |                                                                          
 5 |                                                                          
 4 |                                                                          
 3 |                                                                          
 2 |                                                                          
 1 |  [E1||||] [E2||||] [E3||||] [E4||||]                                     
================================================================================
Legend:
[ || ] - Open doors   [||||] - Closed doors   * - Target floor   [!!!!] - Emergency
↑/↓ - Moving up/down   E# - Elevator number
```

https://github.com/user-attachments/assets/0ca6b33a-c6f0-4d4a-9fa3-2774348a5309

### 6. Command Line Interface (CLI)
The system includes a powerful CLI tool for interacting with the elevator system:

```bash
# Get system status (all elevators)
python src/cli.py status

# Get specific elevator status
python src/cli.py elevator-status 1

# Request elevator from inside (internal request)
python src/cli.py request-elevator 1 5  # Request elevator 1 to go to floor 5

# Request elevator from floor (external request)
python src/cli.py call-elevator 3 up  # Call elevator to floor 3, going up

# Get system statistics
python src/cli.py stats

# Monitor system status in real-time (updates every second)
python src/cli.py monitor

# Trigger emergency mode
python src/cli.py emergency

# Resume normal operation
python src/cli.py resume
```

**CLI Options:**
- `--api-url`: Specify custom API URL (default: http://localhost:8080)
- `--help`: Show help message and available commands
- `monitor --interval`: Set custom update interval for monitoring (default: 1 second)

### 7. Logging System
The system maintains detailed logs of all elevator operations:

**Log Location:**
- Logs are stored in the `logs/` directory
- Each session creates a new log file: `elevator_system_YYYYMMDD_HHMMSS.log`

**What's Logged:**
1. System Events:
   - System initialization
   - Elevator initialization with zones
   - API requests (except status polling)
   
2. Elevator State Changes:
   - Movement between floors
   - Direction changes (up/down/idle)
   - Door operations (opening/closing)
   - State transitions
   - Emergency events

**Monitoring Logs:**
```bash
# View latest log file
cat logs/elevator_system_*.log | tail -n 1

# Monitor logs in real-time
tail -f logs/elevator_system_*.log

# Search logs for specific elevator
grep "E1" logs/elevator_system_*.log
```

**Log Format:**
```
2025-07-09 19:40:16,008 [INFO] === Starting New Elevator System Session ===
2025-07-09 19:40:16,008 [INFO] Initialized E1 - Zone: low_rise, Floors: (1, 20)
2025-07-09 19:40:16,008 [INFO] E1 state change: idle -> moving
2025-07-09 19:40:16,008 [INFO] E1 floor change: 1 -> 2
2025-07-09 19:40:16,008 [INFO] E1 direction change: idle -> up
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

