#!/usr/bin/env python3
"""
Test script to verify the macOS system application filtering.
This script tests that macOS system applications are properly excluded from tracking.
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

def test_macos_app_filtering():
    """Test that macOS system applications are properly excluded from tracking"""
    print(f"Running test on {platform.system()} platform")
    
    if platform.system() != 'Darwin':
        print("This test is specific to macOS. Skipping on other platforms.")
        return True
    
    # Create an instance of the Api class
    api = Api()
    
    # Initialize application tracking variables
    api.applications_usage = {}
    api.last_app_check_time = time.time()
    
    # Run the check_running_applications method
    print("Checking running applications...")
    api.check_running_applications()
    
    # Print the detected applications
    print("\nDetected applications:")
    for app_name, app_info in api.applications_usage.items():
        print(f"- {app_name}: {app_info['exe']}")
    
    # Check if any system applications were detected
    system_apps_detected = []
    
    # List of common macOS system applications to check for
    macos_system_apps = [
        'Finder', 'Dock', 'SystemUIServer', 'Safari', 'Mail', 'Calendar',
        'Terminal', 'Activity Monitor', 'System Preferences', 'launchd',
        'WindowServer', 'loginwindow'
    ]
    
    for app_name in macos_system_apps:
        if any(app.lower() == app_name.lower() for app in api.applications_usage.keys()):
            system_apps_detected.append(app_name)
    
    # Report results
    if system_apps_detected:
        print(f"\nWARNING: Detected {len(system_apps_detected)} system applications that should be excluded:")
        for app in system_apps_detected:
            print(f"- {app}")
        print("\nTest failed: macOS system applications are not being properly filtered.")
        return False
    else:
        print("\nSuccess: No macOS system applications were detected.")
        print("Test passed: macOS system applications are being properly filtered.")
        return True

if __name__ == "__main__":
    test_macos_app_filtering()