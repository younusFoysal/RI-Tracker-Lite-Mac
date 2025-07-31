#!/usr/bin/env python3
"""
Test script to verify the macOS fix for the timer crash.
This script simulates starting the timer to check if the pynput initialization
is properly handled on macOS.
"""

import os
import sys
import platform

# Add the backend directory to the path so we can import from it
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)

# Import the Api class from main.py
from main import Api

def test_start_timer():
    """Test starting the timer to verify it doesn't crash on macOS"""
    print(f"Running test on {platform.system()} platform")
    
    # Create an instance of the Api class
    api = Api()
    
    # Check if system tracking is enabled
    print(f"System tracking enabled: {api.system_tracking_enabled}")
    
    # Simulate starting the timer
    print("Starting timer...")
    try:
        # We don't need to actually start the timer, just initialize the activity tracking
        api.start_activity_tracking()
        print("Activity tracking started successfully")
        
        # Clean up
        api.stop_activity_tracking()
        print("Activity tracking stopped successfully")
        
        print("Test passed: No crash occurred")
        return True
    except Exception as e:
        print(f"Test failed: An error occurred: {e}")
        return False

if __name__ == "__main__":
    test_start_timer()