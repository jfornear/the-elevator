#!/usr/bin/env python3

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8080"

def print_response(response):
    """Pretty print the API response"""
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print(f"Status Code: {response.status_code}\n")

def test_api():
    """Test all API endpoints"""
    
    print("\n1. Get System Status")
    print("-------------------")
    response = requests.get(f"{BASE_URL}/system/status")
    print_response(response)

    print("\n2. Get Individual Elevator Status (Elevator 1)")
    print("--------------------------------------------")
    response = requests.get(f"{BASE_URL}/elevator/1/status")
    print_response(response)

    print("\n3. Add Internal Request (Elevator 1 to Floor 5)")
    print("--------------------------------------------")
    data = {
        "target_floor": 5,
        "direction": "up"
    }
    response = requests.post(f"{BASE_URL}/elevator/1/request", json=data)
    print_response(response)

    print("\n4. Add External Request (From Floor 3, Going Up)")
    print("--------------------------------------------")
    response = requests.post(f"{BASE_URL}/floor/3/request?direction=up")
    print_response(response)

    print("\n5. Get System Statistics")
    print("----------------------")
    response = requests.get(f"{BASE_URL}/system/statistics")
    print_response(response)

    print("\n6. Check System Status Again (should show updated targets)")
    print("-------------------------------------------------")
    response = requests.get(f"{BASE_URL}/system/status")
    print_response(response)

if __name__ == "__main__":
    print("Testing Elevator System API...")
    print("Make sure the API server is running (python run_api.py)")
    print("Testing endpoints...")
    test_api() 