# System-Wide Activity Tracking Fix

## Issue Description

Users reported that idle time was high even when they were continuously working on keyboard and mouse. Investigation revealed that the keyboard activity rate was always 0, indicating that the app was not properly tracking keyboard activity. The issue occurred specifically when users minimized the app and worked in other applications like VS Code or Microsoft Word.

## Root Cause

The original implementation relied on JavaScript event listeners in the frontend (App.jsx) to detect keyboard and mouse activity. These event listeners only work when the app window is in focus. When the app is minimized or not in focus, it doesn't receive keyboard or mouse events from other applications, resulting in:

1. No keyboard activity being recorded
2. High idle time despite active user work
3. Inaccurate productivity metrics

## Solution Implemented

We implemented system-wide keyboard and mouse activity tracking using the `pynput` library in Python. This allows the app to detect keyboard and mouse activity regardless of whether the app window is in focus or minimized.

### Changes Made:

1. Added the `pynput` library to the project dependencies in `requirements.txt`
2. Added import for `pynput` with fallback handling in `main.py`
3. Added system-wide tracking variables in the `Api` class `__init__` method
4. Implemented callback functions for keyboard and mouse events
5. Modified the `start_activity_tracking` and `stop_activity_tracking` methods to initialize, start, and stop the system-wide listeners

### Fallback Mechanism:

If the `pynput` library is not available or if there's an error starting the system-wide listeners, the application will fall back to the current behavior of only tracking activity within the app window.

## How to Test

1. Install the `pynput` library:
   ```
   pip install pynput>=1.7.6
   ```

2. Run the test script:
   ```
   python test_system_activity_tracking.py
   ```

3. When prompted, use your keyboard and mouse for 10 seconds. The script will then display the activity stats, including keyboard and mouse activity rates.

4. For a more comprehensive test:
   - Start the RI Tracker app
   - Start the timer
   - Minimize the app
   - Work in other applications (e.g., VS Code, Microsoft Word) for a few minutes
   - Restore the app and check the activity stats
   - The keyboard activity rate should be > 0 if you used the keyboard

## Expected Results

- Keyboard activity is tracked even when the app is minimized
- Mouse activity is tracked even when the app is minimized
- Idle time is calculated correctly based on actual user activity
- Activity rates (keyboard and mouse) reflect actual usage

## Notes for Developers

- The `pynput` library requires different permissions on different operating systems:
  - On macOS, the app needs Accessibility permissions
  - On Linux, the app may need X11 permissions
  - On Windows, no special permissions are required

- If you encounter issues with system-wide tracking, check the console for error messages related to `pynput` initialization.

- The system-wide tracking is only active when the timer is running, to avoid unnecessary resource usage.