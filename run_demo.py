#!/usr/bin/env python3

import subprocess
import time
import sys
import signal
import os
import json
import requests

def wait_for_api(timeout=10):
    """Wait for API server to be ready."""
    start_time = time.time()
    port_file = '.elevator_port'
    
    # Wait for port file to appear
    while time.time() - start_time < timeout:
        if os.path.exists(port_file):
            try:
                with open(port_file, 'r') as f:
                    port = json.load(f)['port']
                    
                # Try to connect to API
                try:
                    response = requests.get(f"http://localhost:{port}/", timeout=0.1)
                    if response.status_code == 200:
                        return True
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    pass
            except (OSError, json.JSONDecodeError, KeyError):
                pass
        time.sleep(0.1)
    return False

def run_demo():
    """Run both the API server and the demo."""
    try:
        # Start the API server
        print("Starting API server...")
        api_process = subprocess.Popen(["python", "run_api.py"])
        
        # Wait for API server to be ready
        print("Waiting for API server to start...")
        if not wait_for_api():
            print("Error: API server failed to start!")
            api_process.terminate()
            return
        
        # Start the demo
        print("Starting demo...")
        demo_process = subprocess.Popen(["python", "src/demo.py"])
        
        # Wait for either process to finish
        demo_process.wait()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up processes
        print("Cleaning up...")
        try:
            api_process.terminate()
            demo_process.terminate()
            api_process.wait(timeout=5)
            demo_process.wait(timeout=5)
        except (subprocess.TimeoutExpired, ProcessLookupError):
            # Force kill if graceful shutdown fails
            try:
                api_process.kill()
                demo_process.kill()
            except ProcessLookupError:
                pass
        
        # Clean up port file if it exists
        try:
            os.remove('.elevator_port')
        except OSError:
            pass
        
        print("Done!")

if __name__ == "__main__":
    run_demo() 