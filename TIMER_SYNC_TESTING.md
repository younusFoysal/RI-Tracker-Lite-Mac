# Timer Synchronization Testing Guide

This document provides instructions for testing the timer synchronization feature that ensures the frontend timer stays in sync with the backend timer, even when the application is minimized.

## Background

Previously, there was an issue where:
1. User starts the timer
2. User minimizes the application for a period (e.g., 12 minutes)
3. Upon reopening the app, the frontend timer shows less time (e.g., 7 minutes) than actually elapsed
4. When the user stops the timer, the backend correctly sends the total time (12 minutes)

This happened because the frontend timer (using JavaScript's `setInterval`) would be throttled or paused when the app was minimized, while the backend timer continued to run correctly.

## Solution Implemented

The solution has two parts:
1. A new backend method `get_current_session_time()` that returns the current elapsed time for an active session
2. A window focus event listener in the frontend that syncs the timer with the backend when the app regains focus

## Manual Testing Steps

### Prerequisites
- Ensure the application is built with the latest changes
- Have a valid user account to log in

### Test Case 1: Basic Timer Functionality

1. Start the application
2. Log in with valid credentials
3. Start the timer by clicking the play button
4. Verify the timer starts counting up
5. After a few minutes, stop the timer
6. Verify the timer stops and the session is recorded correctly

### Test Case 2: Timer Sync After Minimizing

1. Start the application
2. Log in with valid credentials
3. Start the timer by clicking the play button
4. Note the current time displayed on the timer
5. Minimize the application (or switch to another application)
6. Wait for at least 2-3 minutes
7. Restore the application window
8. Verify that the timer immediately updates to show the correct elapsed time
   - The time should jump forward to account for the time the app was minimized
9. Stop the timer
10. Verify the total time recorded matches the actual elapsed time

### Test Case 3: Long Minimized Period

1. Start the application
2. Log in with valid credentials
3. Start the timer by clicking the play button
4. Note the current time displayed on the timer
5. Minimize the application (or switch to another application)
6. Wait for at least 10-15 minutes
7. Restore the application window
8. Verify that the timer immediately updates to show the correct elapsed time
   - The time should jump forward to account for the time the app was minimized
9. Stop the timer
10. Verify the total time recorded matches the actual elapsed time

### Test Case 4: Multiple Minimize/Restore Cycles

1. Start the application
2. Log in with valid credentials
3. Start the timer by clicking the play button
4. Minimize and restore the application several times with different time intervals
5. Each time the application is restored, verify the timer updates correctly
6. Stop the timer
7. Verify the total time recorded matches the actual elapsed time

## Expected Results

- In all test cases, when the application window regains focus after being minimized, the timer should immediately update to show the correct elapsed time
- The final recorded time should always match the actual elapsed time, regardless of how long the application was minimized

## Troubleshooting

If the timer does not sync correctly:
1. Check the browser console for any JavaScript errors
2. Verify that the window focus event listener is being triggered
3. Verify that the backend `get_current_session_time()` method is returning the correct elapsed time
4. Ensure the frontend is correctly updating the timer state with the value from the backend

## Additional Notes

- The timer sync happens only when the window regains focus, so there might be a brief moment where the timer shows the incorrect time before it updates
- The sync is only necessary when the timer is running; if the timer is stopped, no sync is needed