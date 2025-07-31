#!/usr/bin/env python3
"""
Test script to verify the keyboard activity tracking fix.
This script simulates keyboard activity and checks if the keyboard activity rate is properly tracked.
"""

import os
import sys
import time

# Add the backend directory to the path so we can import from it
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)

# Import the Api class from main.py
from main import Api

def test_keyboard_tracking():
    """Test keyboard activity tracking"""
    print("Testing keyboard activity tracking...")
    
    # Create an instance of the Api class
    api = Api()
    
    # Start a timer
    print("Starting timer...")
    api.start_timer("Test Project")
    
    # Simulate keyboard activity
    print("Simulating keyboard activity...")
    for i in range(10):
        api.record_keyboard_activity()
        time.sleep(0.6)  # Sleep longer than the throttle interval (0.5s)
        print(f"Keyboard event {i+1} sent")
    
    # Wait a moment for the activity metrics to update
    time.sleep(1)
    
    # Get activity stats
    stats = api.get_activity_stats()
    print(f"Activity stats: {stats}")
    
    # Check if keyboard activity rate is greater than 0
    keyboard_rate = stats.get('keyboard_rate', 0)
    if keyboard_rate > 0:
        print(f"SUCCESS: Keyboard activity rate is {keyboard_rate}")
    else:
        print(f"FAILURE: Keyboard activity rate is still 0")
    
    # Stop the timer
    api.stop_timer()
    print("Timer stopped")
    
    return keyboard_rate > 0

if __name__ == "__main__":
    test_keyboard_tracking()