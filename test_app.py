#!/usr/bin/env python3
"""
Test script for the Flask application
"""
import requests
import json
import time
import threading
from app import app

def test_endpoints():
    """Test all application endpoints"""
    base_url = "http://localhost:5000"
    
    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "url": f"{base_url}/health",
            "expected_status": 200
        },
        {
            "name": "Homepage",
            "method": "GET", 
            "url": f"{base_url}/",
            "expected_status": 200
        },
        {
            "name": "Predict Endpoint",
            "method": "POST",
            "url": f"{base_url}/api/ask",
            "data": {"test": "data", "value": 123},
            "expected_status": 400
        },
        {
            "name": "404 Test",
            "method": "GET",
            "url": f"{base_url}/nonexistent",
            "expected_status": 404
        }
    ]
    
    print("Testing Flask Application Endpoints...")
    print("-" * 50)
    
    for test in tests:
        try:
            if test["method"] == "GET":
                response = requests.get(test["url"], timeout=5)
            elif test["method"] == "POST":
                response = requests.post(
                    test["url"], 
                    json=test.get("data", {}),
                    timeout=5
                )
            
            status_ok = response.status_code == test["expected_status"]
            status_icon = "✅" if status_ok else "❌"
            
            print(f"{status_icon} {test['name']}: {response.status_code}")
            
            if not status_ok:
                print(f"   Expected: {test['expected_status']}, Got: {response.status_code}")
                print(f"   Response: {response.text[:100]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {test['name']}: Connection error - {str(e)}")
        except Exception as e:
            print(f"❌ {test['name']}: Error - {str(e)}")
    
    print("-" * 50)
    print("Testing complete!")

if __name__ == "__main__":
    print("Starting Flask app in test mode...")
    print("Note: Run 'python app.py' in another terminal to start the server first")
    print("Then run this test script")
    
    try:
        test_endpoints()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")