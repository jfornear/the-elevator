# Local Setup Guide

This guide explains how to set up and run the elevator system on your local machine.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/the-elevator.git
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

There are several ways to run the elevator system:

### 1. Run Full Demo (Recommended)
This will start both the API server and the visualization:
```bash
python run_demo.py
```

The demo will:
- Start the API server (automatically finds an available port)
- Launch the visualization interface
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

### 3. Run Tests
To run the test suite:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_elevator.py

# Run with verbose output
pytest -v
```

## API Endpoints

Once running, the following endpoints are available:

- `GET /system/status` - Get status of all elevators
- `GET /elevator/{id}/status` - Get specific elevator status
- `POST /elevator/{id}/request` - Send internal request
- `POST /floor/{number}/request` - Send external request
- `POST /system/emergency` - Trigger emergency mode

Visit `http://localhost:8080/docs` for interactive API documentation.

## Directory Structure

```
the-elevator/
├── src/                 # Source code
│   ├── api.py          # API implementation
│   ├── elevator.py     # Elevator logic
│   ├── system.py       # System coordination
│   └── visualizer.py   # ASCII visualization
├── tests/              # Test files
├── docs/               # Documentation
├── logs/               # System logs
├── run_api.py         # API server runner
└── run_demo.py        # Demo runner
```

## Configuration

The system comes with default settings:
- 6 elevators
- 50 floors
- 3 zones (Low/Mid/High-rise)
- Door timing controls
- Weight limits (2200 lbs per elevator)

## Logging

- Logs are stored in the `logs/` directory
- New log file created for each session
- Logs include:
  - System initialization
  - Elevator movements
  - Request handling
  - State changes
  - Errors

## Troubleshooting

1. **Port Already in Use**
   ```bash
   # Check if another instance is running
   ps aux | grep run_api.py
   # Kill the process if needed
   kill <process_id>
   ```

2. **Visualization Issues**
   - Ensure terminal window is large enough
   - Try resizing terminal
   - Check if your terminal supports ASCII graphics

3. **API Connection Failed**
   - Verify the port number in `.elevator_port`
   - Check if API server is running
   - Ensure no firewall blocking local connections

## Development Setup

For development work:

1. **Install Development Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Tests During Development**
   ```bash
   # Run tests with coverage
   pytest --cov=src

   # Run tests in watch mode
   pytest-watch
   ```

3. **Code Style**
   - Follow PEP 8 guidelines
   - Use type hints
   - Keep functions focused and small
   - Add docstrings for public interfaces

## Support

If you encounter any issues:
1. Check the logs in `logs/` directory
2. Ensure all dependencies are installed
3. Verify Python version compatibility
4. Check for port conflicts 