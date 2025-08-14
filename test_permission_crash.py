#!/usr/bin/env python3
"""
Test script to diagnose macOS permission-related crashes in RI Tracker.
This script tests different components in isolation to identify what's causing the crash.
"""

import os
import sys
import platform
import time
import threading

print("=" * 80)
print("RI Tracker macOS Permission Crash Diagnostic")
print("=" * 80)

# Check if we're on macOS
if platform.system() != 'Darwin':
    print("This test script is intended for macOS only.")
    sys.exit(1)

print("\nTesting pynput import...")
try:
    from pynput import keyboard, mouse
    print("✓ pynput imported successfully")
except ImportError as e:
    print(f"✗ Failed to import pynput: {e}")
    print("  This could indicate pynput is not installed or incompatible.")
    sys.exit(1)

print("\nTesting keyboard listener creation (without starting)...")
try:
    kb_listener = keyboard.Listener(on_press=lambda key: None)
    print("✓ Keyboard listener created successfully")
except Exception as e:
    print(f"✗ Failed to create keyboard listener: {e}")
    print("  This could indicate an issue with pynput configuration.")

print("\nTesting mouse listener creation (without starting)...")
try:
    m_listener = mouse.Listener(on_move=lambda x, y: None, on_click=lambda x, y, button, pressed: None, on_scroll=lambda x, y, dx, dy: None)
    print("✓ Mouse listener created successfully")
except Exception as e:
    print(f"✗ Failed to create mouse listener: {e}")
    print("  This could indicate an issue with pynput configuration.")

print("\nTesting permission check (starting keyboard listener)...")
try:
    kb_listener = keyboard.Listener(on_press=lambda key: None)
    kb_listener.start()
    print("✓ Keyboard listener started successfully - permissions appear to be granted")
    kb_listener.stop()
except Exception as e:
    print(f"✗ Failed to start keyboard listener: {e}")
    print("  This likely indicates permissions are not granted.")

print("\nTesting subprocess for opening System Preferences...")
try:
    import subprocess
    print("Attempting to open System Preferences (Input Monitoring)...")
    subprocess.run([
        "open", 
        "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent"
    ])
    print("✓ System Preferences command executed")
except Exception as e:
    print(f"✗ Failed to open System Preferences: {e}")
    print("  This could be causing the crash when requesting permissions.")

print("\nTesting threading Timer...")
try:
    def timer_test():
        print("✓ Timer function executed successfully")
    
    print("Starting a timer for 1 second...")
    timer = threading.Timer(1.0, timer_test)
    timer.daemon = True
    timer.start()
    time.sleep(1.5)  # Wait for timer to complete
    print("Timer test completed")
except Exception as e:
    print(f"✗ Failed in timer test: {e}")
    print("  This could be causing issues with the delayed permission request.")

print("\nTest completed. Check the results above to identify potential issues.")
print("=" * 80)