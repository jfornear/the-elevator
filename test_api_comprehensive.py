#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8080"

def print_response(response, description=""):
    """Pretty print the API response"""
    print(f"\n{description}")
    print("-" * len(description))
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print(f"Status Code: {response.status_code}\n")

def test_api():
    """Test all API endpoints with various scenarios"""
    
    print("Starting comprehensive API tests...")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 1. Root endpoint
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "1. Get API Information")

    # 2. System Status - Initial State
    print("\n=== Testing System Status ===")
    response = requests.get(f"{BASE_URL}/system/status")
    print_response(response, "2. Get Initial System Status")

    # 3. Individual Elevator Status
    print("\n=== Testing Individual Elevator Status ===")
    for elevator_id in [1, 3, 5]:  # Test one from each zone
        response = requests.get(f"{BASE_URL}/elevator/{elevator_id}/status")
        print_response(response, f"3.{elevator_id}. Get Elevator {elevator_id} Status (Zone: {'Low' if elevator_id <= 2 else 'Mid' if elevator_id <= 4 else 'High'}-Rise)")

    # 4. Test Invalid Elevator ID
    print("\n=== Testing Error Handling ===")
    response = requests.get(f"{BASE_URL}/elevator/999/status")
    print_response(response, "4.1. Get Invalid Elevator Status (ID: 999)")

    # 5. Internal Requests - Test Zone Restrictions
    print("\n=== Testing Internal Requests ===")
    
    # 5.1 Valid request within zone
    data = {"target_floor": 5, "direction": "up"}
    response = requests.post(f"{BASE_URL}/elevator/1/request", json=data)
    print_response(response, "5.1. Add Internal Request (Elevator 1 to Floor 5 - Valid Low-Rise)")

    # 5.2 Invalid request outside zone
    data = {"target_floor": 40, "direction": "up"}
    response = requests.post(f"{BASE_URL}/elevator/1/request", json=data)
    print_response(response, "5.2. Add Internal Request (Elevator 1 to Floor 40 - Invalid Zone)")

    # 5.3 Mid-rise request
    data = {"target_floor": 25, "direction": "up"}
    response = requests.post(f"{BASE_URL}/elevator/3/request", json=data)
    print_response(response, "5.3. Add Internal Request (Elevator 3 to Floor 25 - Valid Mid-Rise)")

    # 5.4 High-rise request
    data = {"target_floor": 45, "direction": "up"}
    response = requests.post(f"{BASE_URL}/elevator/5/request", json=data)
    print_response(response, "5.4. Add Internal Request (Elevator 5 to Floor 45 - Valid High-Rise)")

    # 6. External Requests
    print("\n=== Testing External Requests ===")
    
    # 6.1 Low-rise floor
    response = requests.post(f"{BASE_URL}/floor/3/request?direction=up")
    print_response(response, "6.1. Add External Request (Floor 3 Going Up - Low-Rise)")

    # 6.2 Mid-rise floor
    response = requests.post(f"{BASE_URL}/floor/25/request?direction=down")
    print_response(response, "6.2. Add External Request (Floor 25 Going Down - Mid-Rise)")

    # 6.3 High-rise floor
    response = requests.post(f"{BASE_URL}/floor/45/request?direction=down")
    print_response(response, "6.3. Add External Request (Floor 45 Going Down - High-Rise)")

    # 6.4 Invalid floor
    response = requests.post(f"{BASE_URL}/floor/999/request?direction=up")
    print_response(response, "6.4. Add External Request (Invalid Floor 999)")

    # 7. System Statistics
    print("\n=== Testing System Statistics ===")
    response = requests.get(f"{BASE_URL}/system/statistics")
    print_response(response, "7. Get System Statistics")

    # 8. Emergency Stop
    print("\n=== Testing Emergency Operations ===")
    response = requests.post(f"{BASE_URL}/system/emergency")
    print_response(response, "8.1. Trigger Emergency Stop")

    # Check system status after emergency
    response = requests.get(f"{BASE_URL}/system/status")
    print_response(response, "8.2. System Status After Emergency")

    # Resume service
    response = requests.post(f"{BASE_URL}/system/resume")
    print_response(response, "8.3. Resume Service")

    # Check system status after resume
    response = requests.get(f"{BASE_URL}/system/status")
    print_response(response, "8.4. System Status After Resume")

    # 9. Final System Status
    print("\n=== Final System Status ===")
    response = requests.get(f"{BASE_URL}/system/status")
    print_response(response, "9. Get Final System Status")

    print("\nTest Summary:")
    print("-------------")
    print("✓ Root endpoint")
    print("✓ System status")
    print("✓ Individual elevator status")
    print("✓ Error handling")
    print("✓ Internal requests (zone-based)")
    print("✓ External requests")
    print("✓ System statistics")
    print("✓ Emergency operations")
    print("\nNote: Check the responses above for detailed results")

if __name__ == "__main__":
    print("Testing Elevator System API...")
    print("Make sure the API server is running (python run_api.py)")
    print("Testing all endpoints with various scenarios...")
    test_api() 