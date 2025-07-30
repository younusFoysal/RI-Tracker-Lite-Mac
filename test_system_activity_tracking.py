import time
import os
import sys
import json
import subprocess

# Add the backend directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the Api class from main.py
from main import Api

def test_system_activity_tracking():
    """
    Test the system-wide activity tracking functionality.
    
    This test:
    1. Creates an instance of the Api class
    2. Starts a timer
    3. Waits for a few seconds to simulate activity
    4. Gets the activity stats
    5. Stops the timer
    6. Prints the results
    
    Expected results:
    - keyboard_activity_rate should be > 0 if keyboard activity occurred
    - mouse_activity_rate should be > 0 if mouse activity occurred
    """
    print("Starting system activity tracking test...")
    
    # Create an instance of the Api class
    api = Api()
    
    # Start a timer
    print("Starting timer...")
    result = api.start_timer("Test Project")
    if not result["success"]:
        print(f"Failed to start timer: {result.get('message', 'Unknown error')}")
        return
    
    print("Timer started. Please use your keyboard and mouse for the next 10 seconds...")
    
    # Wait for 10 seconds to allow for activity
    time.sleep(10)
    
    # Get the activity stats
    stats = api.get_activity_stats()
    if not stats["success"]:
        print(f"Failed to get activity stats: {stats.get('message', 'Unknown error')}")
        api.stop_timer()
        return
    
    # Stop the timer
    print("Stopping timer...")
    api.stop_timer()
    
    # Print the results
    print("\nActivity Stats:")
    print(f"Active Time: {stats['active_time']} seconds")
    print(f"Idle Time: {stats['idle_time']} seconds")
    print(f"Keyboard Activity Rate: {stats['keyboard_rate']} events per minute")
    print(f"Mouse Activity Rate: {stats['mouse_rate']} events per minute")
    print(f"Is Idle: {stats['is_idle']}")
    
    # Check if keyboard activity was detected
    if stats['keyboard_rate'] > 0:
        print("\nSUCCESS: Keyboard activity was detected!")
    else:
        print("\nWARNING: No keyboard activity was detected. Please make sure you used the keyboard during the test.")
    
    # Check if mouse activity was detected
    if stats['mouse_rate'] > 0:
        print("SUCCESS: Mouse activity was detected!")
    else:
        print("WARNING: No mouse activity was detected. Please make sure you moved the mouse during the test.")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_system_activity_tracking()