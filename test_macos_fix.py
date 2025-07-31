#!/usr/bin/env python3
"""
Test script to verify the macOS permission handling for pynput.
This script tests the enhanced permission handling for pynput on macOS,
ensuring that the application can properly check for and request permissions.
"""

import os
import sys
import platform
import time

# Add the backend directory to the path so we can import from it
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)

# Import the Api class from main.py
from main import Api

def test_macos_permissions():
    """Test macOS permission handling for pynput"""
    print(f"Running test on {platform.system()} platform")
    
    # Create an instance of the Api class
    api = Api()
    
    # Get initial system tracking status
    status = api.get_system_tracking_status()
    print(f"Initial system tracking status: {status}")
    
    if platform.system() == 'Darwin':
        print("\n=== Testing macOS Permission Handling ===")
        
        # Check permissions
        print("\nChecking permissions...")
        perm_check = api.check_macos_permissions()
        print(f"Permission check result: {perm_check}")
        
        if not perm_check.get("has_permissions", False):
            # Request permissions
            print("\nPermissions not granted. Requesting permissions...")
            print("This will open System Preferences. Please grant permissions if prompted.")
            request_result = api.request_macos_permissions()
            print(f"Permission request result: {request_result}")
            
            # Wait for user to potentially grant permissions
            print("\nWaiting 10 seconds for you to grant permissions...")
            time.sleep(10)
            
            # Check permissions again
            print("\nChecking permissions again...")
            perm_check = api.check_macos_permissions()
            print(f"Permission check result: {perm_check}")
        
        # Try to enable system tracking
        print("\nTrying to enable system tracking...")
        toggle_result = api.toggle_system_tracking(True)
        print(f"Toggle result: {toggle_result}")
        
        # Get updated status
        status = api.get_system_tracking_status()
        print(f"Updated system tracking status: {status}")
    else:
        print("\nNot running on macOS, skipping permission tests")
    
    # Test activity tracking
    print("\n=== Testing Activity Tracking ===")
    print("Starting activity tracking...")
    try:
        # Start activity tracking
        api.start_activity_tracking()
        print("Activity tracking started successfully")
        
        # Simulate some activity
        print("Simulating activity for 3 seconds...")
        for i in range(3):
            api.record_activity('keyboard')
            api.record_activity('mouse')
            time.sleep(1)
            print(".", end="", flush=True)
        print("\nActivity simulation complete")
        
        # Get activity stats
        stats = api.get_activity_stats()
        print(f"Activity stats: {stats}")
        
        # Clean up
        api.stop_activity_tracking()
        print("Activity tracking stopped successfully")
        
        print("\nTest passed: No crash occurred")
        return True
    except Exception as e:
        print(f"\nTest failed: An error occurred: {e}")
        return False

if __name__ == "__main__":
    test_macos_permissions()