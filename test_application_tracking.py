import time
import sys
import os
import json

# Add the backend directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the Api class from main.py
from main import Api

def test_application_tracking():
    """Test the application tracking feature"""
    print("Starting application tracking test...")
    
    # Create an instance of the Api class
    api = Api()
    
    # Start the timer
    print("Starting timer...")
    result = api.start_timer("Test Project")
    
    if not result.get("success"):
        print(f"Failed to start timer: {result.get('message')}")
        return
    
    print("Timer started successfully.")
    print("Waiting for 15 seconds to collect application data...")
    
    # Wait for 15 seconds to collect application data
    time.sleep(15)
    
    # Get the current application usage data
    applications_data = api.prepare_applications_for_session()
    
    print(f"Collected data for {len(applications_data)} applications:")
    for app in applications_data:
        print(f"  - {app['name']}: {app['timeSpent']} seconds")
    
    # Stop the timer
    print("Stopping timer...")
    result = api.stop_timer()
    
    if not result.get("success"):
        print(f"Failed to stop timer: {result.get('message')}")
        return
    
    print("Timer stopped successfully.")
    print("Application tracking test completed.")

if __name__ == "__main__":
    test_application_tracking()