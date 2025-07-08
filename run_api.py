#!/usr/bin/env python3

import uvicorn
import socket
import logging
import json
import os
from src.api import app
from src.utils import cleanup_old_logs

def find_available_port(start_port=8080, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    return None

def write_port_file(port):
    """Write the port number to a temporary file."""
    port_file = os.path.join(os.path.dirname(__file__), '.elevator_port')
    with open(port_file, 'w') as f:
        json.dump({'port': port}, f)

def main():
    # Clean up old logs before starting
    cleanup_old_logs(max_age_days=7, keep_min=10)
    
    # Find an available port
    port = find_available_port(start_port=8080)
    if not port:
        print("Error: Could not find an available port!")
        return
    
    # Write port to file for demo to read
    write_port_file(port)
    
    # Start the API server
    print(f"Starting Elevator System API Server on 0.0.0.0:{port}...")
    print(f"API documentation available at http://localhost:{port}/docs")
    print("Press Ctrl+C to exit")
    
    # Configure uvicorn logging
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = '%(asctime)s - %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelprefix)s %(message)s"
    
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info",
            log_config=log_config
        )
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Error: Port {port} is already in use!")
            print("Please stop any other running instances of the elevator system.")
        else:
            print(f"Error starting server: {e}")
    finally:
        # Clean up port file
        try:
            os.remove(os.path.join(os.path.dirname(__file__), '.elevator_port'))
        except OSError:
            pass

if __name__ == "__main__":
    main() 