# Local Setup Guide

This guide explains how to set up and run the elevator system simulator on your local machine.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git
- Terminal with ASCII support for visualization

## Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/jfornear/the-elevator.git
   cd the-elevator
   ```

2. **Create a Virtual Environment**
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the System

### 1. Run Full Demo (Recommended)
This will start both the API server and the visualization:
```bash
python run_demo.py
```

The demo will:
- Start the API server (automatically finds an available port)
- Launch the ASCII visualization interface
- Show real-time elevator movements
- Handle keyboard interrupts gracefully

### 2. Run API Server Only
If you only need the API server:
```bash
python run_api.py
```

This will:
- Start the FastAPI server on port 8080 (or next available port)
- Provide access to the API endpoints
- Make Swagger documentation available at `http://localhost:8080/docs`

### 3. Use Command Line Interface
The system includes a CLI for direct interaction:
```bash
# Get system status
python src/cli.py status

# Get specific elevator status
python src/cli.py elevator-status 1

# Request elevator from inside
python src/cli.py request-elevator 1 5  # Elevator 1 to floor 5

# Call elevator from floor
python src/cli.py call-elevator 3 up  # Call to floor 3, going up

# Monitor system in real-time
python src/cli.py monitor

# Emergency controls
python src/cli.py emergency  # Stop all elevators
python src/cli.py resume    # Resume operation
```

CLI Options:
- `--api-url`: Custom API URL (default: http://localhost:8080)
- `--help`: Show help message
- `monitor --interval`: Update interval (default: 1 second)

### 4. Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_elevator.py

# Run with verbose output
pytest -v
```

## System Configuration

Current system settings:
- 6 elevators in 3 zones:
  - Low-rise (E1, E2): Floors 1-20
  - Mid-rise (E3, E4): Floors 21-35
  - High-rise (E5, E6): Floors 36-50
- Door timing:
  - Opening: 2 cycles
  - Open: 3 cycles
  - Closing: 2 cycles
- Weight limit: 2200 lbs per elevator
- API cache TTL: 100ms

## API Endpoints

Core endpoints available at `http://localhost:8080`:

- `GET /system/status` - Get all elevator status
- `GET /elevator/{id}/status` - Get specific elevator
- `POST /elevator/{id}/request` - Internal request
- `POST /floor/{number}/request` - External request
- `POST /system/emergency` - Emergency stop
- `POST /system/resume` - Resume operation

Visit `/docs` for interactive Swagger documentation.

## Logging

System logs are stored in `logs/`:
- Format: `elevator_system_YYYYMMDD_HHMMSS.log`
- Contains:
  - System initialization
  - Elevator movements
  - Request handling
  - State changes
  - Errors

Monitor logs:
```bash
# View latest
tail -n 50 logs/elevator_system_*.log

# Monitor real-time
tail -f logs/elevator_system_*.log

# Search for specific elevator
grep "E1" logs/elevator_system_*.log
```

## Troubleshooting

1. **Port Conflicts**
   ```bash
   # Check running instances
   ps aux | grep run_api.py
   # Kill if needed
   kill <process_id>
   ```

2. **Visualization Issues**
   - Ensure terminal is 80+ columns wide
   - Try resizing terminal
   - Check ASCII support

3. **API Connection Failed**
   - Check `.elevator_port` file
   - Verify API server is running
   - Try different port with `--api-url`

4. **Common Issues**
   - "Port in use": Stop other instances
   - "No visualization": Resize terminal
   - "Connection refused": Check API server
   - "Import error": Verify venv activation

## Development

1. **Project Structure**
   ```
   the-elevator/
   ├── src/                 # Source code
   │   ├── api.py          # API implementation
   │   ├── elevator.py     # Core logic
   │   ├── system.py       # Coordination
   │   └── visualizer.py   # ASCII display
   ├── tests/              # Test files
   ├── docs/               # Documentation
   └── logs/               # System logs
   ```

2. **Code Style**
   - Follow PEP 8
   - Use type hints
   - Add docstrings
   - Keep functions focused

3. **Testing**
   - Write unit tests
   - Add integration tests
   - Test zone behavior
   - Verify safety features 