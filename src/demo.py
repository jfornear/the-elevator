#!/usr/bin/env python3

import time
import random
import requests
import json
from datetime import datetime
from src.visualizer import ElevatorVisualizer
import os

class ElevatorAPIDemo:
    def __init__(self, api_url=None):
        self.api_url = api_url
        self.total_floors = 50  # From system configuration
        self.visualizer = ElevatorVisualizer(self.total_floors)
        
        # Try to find the API server
        if not self.api_url:
            # First try to read from port file
            port_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.elevator_port')
            try:
                with open(port_file, 'r') as f:
                    port = json.load(f)['port']
                    self.api_url = f"http://localhost:{port}"
            except (OSError, json.JSONDecodeError, KeyError):
                # If port file not found or invalid, try default ports
                self.api_url = "http://localhost:8080"
        
        # Verify connection
        if not self._check_api_connection():
            for port in range(8080, 8090):
                self.api_url = f"http://localhost:{port}"
                if self._check_api_connection():
                    break
            else:
                raise ConnectionError("Could not connect to API server on any port!")
                
    def _check_api_connection(self):
        """Check if we can connect to the API server."""
        try:
            response = requests.get(f"{self.api_url}/", timeout=0.1)
            return response.status_code == 200
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return False

    def can_accept_request(self, elevator, target_floor, direction=None):
        """Check if elevator can accept a new request."""
        # Check if elevator can serve this floor
        if not self.can_serve_floor(elevator, target_floor):
            return False
            
        # Skip if elevator is in emergency mode or door is moving
        if elevator["state"] in ["emergency", "door_opening", "door_closing"]:
            return False
            
        # Skip if elevator is already serving this floor
        if target_floor in elevator["target_floors"]:
            return False
            
        # If elevator is idle, it can accept any request
        if elevator["direction"] == "idle":
            return True
            
        # If no direction specified, elevator can accept request
        if not direction:
            return True
            
        # Check if request aligns with elevator's current direction
        if elevator["direction"] == "up":
            # If going up, can only accept:
            # - Up requests above current floor
            # - Down requests after highest target
            highest_target = max(elevator["target_floors"]) if elevator["target_floors"] else elevator["current_floor"]
            if direction == "up" and target_floor > elevator["current_floor"]:
                return True
            if direction == "down" and target_floor > highest_target:
                return True
        elif elevator["direction"] == "down":
            # If going down, can only accept:
            # - Down requests below current floor
            # - Up requests after lowest target
            lowest_target = min(elevator["target_floors"]) if elevator["target_floors"] else elevator["current_floor"]
            if direction == "down" and target_floor < elevator["current_floor"]:
                return True
            if direction == "up" and target_floor < lowest_target:
                return True
                
        return False

    def find_best_elevator(self, elevators, target_floor, current_floor=None, direction=None):
        """Find the best elevator to serve a request."""
        best_elevator = None
        min_score = float('inf')
        
        for elevator in elevators:
            # Check if elevator can accept this request
            if not self.can_accept_request(elevator, target_floor, direction):
                continue
            
            # Calculate priority score (lower is better)
            score = len(elevator["target_floors"]) * 10  # Penalize busy elevators
            
            # Add distance factor
            if current_floor:
                score += abs(elevator["current_floor"] - current_floor)
            else:
                score += abs(elevator["current_floor"] - target_floor)
            
            # Prefer idle elevators
            if elevator["state"] == "idle":
                score -= 5
            elif elevator["state"] == "door_open":
                score -= 3  # Second best option
            
            # Prefer elevators already moving in the right direction
            if direction and elevator["direction"] == direction:
                score -= 2
            
            if score < min_score:
                min_score = score
                best_elevator = elevator
        
        return best_elevator

    def generate_traffic(self):
        """Generate simple traffic patterns using the API."""
        # 20% chance to generate a new request
        if random.random() < 0.2:
            try:
                # Get system status with timeout
                status_response = requests.get(f"{self.api_url}/system/status", timeout=0.1)
                if status_response.status_code != 200:
                    return
                    
                elevators = status_response.json()["elevators"]
                
                # Cache elevator states
                elevator_states = {e["id"]: e for e in elevators}
                
                # Decide if we're going up from lobby or down to lobby
                if random.random() < 0.5:  # Going up from lobby
                    # Pick a random floor to go to
                    target_floor = random.randint(2, self.total_floors)
                    
                    # Find best elevator for this request
                    best_elevator = self.find_best_elevator(elevators, target_floor, current_floor=1, direction="up")
                    
                    if best_elevator:
                        # If elevator is not at lobby and not already coming to lobby
                        if best_elevator["current_floor"] != 1 and 1 not in best_elevator["target_floors"]:
                            # Request elevator to lobby
                            response = requests.post(
                                f"{self.api_url}/floor/1/request",
                                params={"direction": "up"},
                                timeout=0.1
                            )
                            if response.status_code != 200:
                                return
                                
                            # Update cached state instead of making a new request
                            elevator_states[best_elevator["id"]]["target_floors"].append(1)
                            
                        # Only send target request if elevator is at lobby or coming to lobby
                        if best_elevator["current_floor"] == 1 or 1 in best_elevator["target_floors"]:
                            requests.post(
                                f"{self.api_url}/elevator/{best_elevator['id']}/request",
                                json={"target_floor": target_floor},
                                timeout=0.1
                            )
                else:  # Going down to lobby
                    # Pick a random floor to start from
                    start_floor = random.randint(2, self.total_floors)
                    
                    # Find best elevator for this request
                    best_elevator = self.find_best_elevator(elevators, start_floor, direction="down")
                    
                    if best_elevator:
                        # First request elevator to pickup floor
                        response = requests.post(
                            f"{self.api_url}/floor/{start_floor}/request",
                            params={"direction": "down"},
                            timeout=0.1
                        )
                        if response.status_code != 200:
                            return
                        
                        # Update cached state instead of making a new request
                        elevator_states[best_elevator["id"]]["target_floors"].append(start_floor)
                        
                        # Only send to lobby if elevator is heading to pickup floor
                        if start_floor in best_elevator["target_floors"]:
                            requests.post(
                                f"{self.api_url}/elevator/{best_elevator['id']}/request",
                                json={"target_floor": 1},
                                timeout=0.1
                            )
            except (requests.exceptions.Timeout, requests.exceptions.RequestException):
                # Handle timeouts and other request errors gracefully
                return

    def can_serve_floor(self, elevator, floor):
        """Check if elevator can serve the given floor based on its zone."""
        zone_range = elevator["zone_range"]
        return zone_range[0] <= floor <= zone_range[1]

    def get_system_status(self):
        """Get current system status through API for visualization."""
        try:
            response = requests.get(f"{self.api_url}/system/status", timeout=0.1)
            if response.status_code == 200:
                status = response.json()
                # Convert API response to visualizer format
                return {
                    "elevators": [{
                        "id": e["id"],
                        "current_floor": e["current_floor"],
                        "direction": e["direction"],
                        "state": e["state"],
                        "target_floors": e["target_floors"],
                        "zone": e["zone"],
                        "current_weight": 0  # Added for visualizer compatibility
                    } for e in status["elevators"]]
                }
        except (requests.exceptions.Timeout, requests.exceptions.RequestException):
            # Return last known status on error
            return self._last_status if hasattr(self, '_last_status') else None
        return None

    def run(self):
        """Run the demo."""
        print("Starting elevator system demo...")
        print("Press Ctrl+C to exit")
        
        last_status_time = 0
        status_interval = 0.2  # Only update status every 200ms
        last_traffic_time = 0
        traffic_interval = 0.5  # Only generate traffic every 500ms
        
        try:
            while True:
                current_time = time.time()
                
                # Generate traffic periodically
                if current_time - last_traffic_time >= traffic_interval:
                    self.generate_traffic()
                    last_traffic_time = current_time
                
                # Update visualization periodically
                if current_time - last_status_time >= status_interval:
                    status = self.get_system_status()
                    if status:
                        self._last_status = status
                        self.visualizer.draw_system(status)
                    last_status_time = current_time
                
                time.sleep(0.05)  # Smaller delay for better responsiveness
                
        except KeyboardInterrupt:
            print("\nStopping demo...")

if __name__ == "__main__":
    demo = ElevatorAPIDemo()
    demo.run() 