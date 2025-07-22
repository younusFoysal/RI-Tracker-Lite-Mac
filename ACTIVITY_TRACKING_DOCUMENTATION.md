# Activity Tracking Implementation

## Overview

This document describes the implementation of activity tracking in the RI Tracker application. The activity tracking mechanism tracks user activity (keyboard and mouse events) to calculate:

- Active time: Time when the user is actively using the application
- Idle time: Time when the user is not interacting with the application
- Keyboard activity rate: Number of keyboard events per minute
- Mouse activity rate: Number of mouse events per minute

## Implementation Details

### Backend (Python)

The activity tracking mechanism is implemented in the `Api` class in `backend/main.py`. The following components were added or modified:

1. **Activity Tracking Variables**:
   - `last_activity_time`: Timestamp of the last user activity
   - `is_idle`: Flag indicating if the user is currently idle
   - `idle_threshold`: Time (in seconds) after which a user is considered idle (default: 60 seconds)
   - `keyboard_events`: Counter for keyboard events
   - `mouse_events`: Counter for mouse events
   - `activity_timer`: Timer for periodic activity checks
   - `activity_check_interval`: Interval (in seconds) between activity checks
   - `last_active_check_time`: Timestamp of the last activity check
   - `last_keyboard_event_time` and `last_mouse_event_time`: Timestamps for throttling event counting

2. **Activity Tracking Methods**:
   - `record_activity`: Records user activity (keyboard or mouse) and updates activity counters
   - `check_idle_status`: Checks if the user is idle and updates active/idle time accordingly
   - `update_activity_metrics`: Updates keyboard and mouse activity rates
   - `start_activity_tracking`: Starts the activity tracking thread
   - `stop_activity_tracking`: Stops the activity tracking thread

3. **JavaScript Interface Methods**:
   - `record_keyboard_activity`: Interface method for the frontend to report keyboard activity
   - `record_mouse_activity`: Interface method for the frontend to report mouse activity
   - `get_activity_stats`: Returns current activity statistics

4. **Timer Methods**:
   - `start_timer`: Initializes activity tracking variables and starts the tracking thread
   - `stop_timer`: Calculates final active/idle time and updates the session with all metrics

### Frontend (JavaScript/React)

The frontend was updated to report user activity to the backend:

1. **Event Listeners**:
   - Added event listeners for keyboard events (`keydown`)
   - Added event listeners for mouse events (`mousemove`, `click`)
   - These event listeners call the backend methods `record_keyboard_activity` and `record_mouse_activity`

## How It Works

1. When the timer is started:
   - All activity tracking variables are initialized
   - The activity tracking thread is started
   - The user is considered active

2. During timer operation:
   - The frontend reports keyboard and mouse events to the backend
   - The backend records these events and updates the last activity time
   - The activity tracking thread periodically checks if the user is idle
   - If the user is idle for more than the idle threshold, they are marked as idle
   - Active and idle time are updated accordingly

3. When the timer is stopped:
   - Final active and idle time are calculated
   - Activity metrics (keyboard and mouse activity rates) are updated
   - The session is updated with all metrics
   - The activity tracking thread is stopped

## Throttling

To prevent excessive event counting (e.g., when the user is continuously moving the mouse), a throttling mechanism is implemented:

- Keyboard events are only counted if enough time has passed since the last counted keyboard event
- Mouse events are only counted if enough time has passed since the last counted mouse event
- The throttle interval is set to 0.5 seconds by default

## Edge Cases

The implementation handles several edge cases:

1. **Transition from active to idle**:
   - When the user becomes idle, the time since the last activity check is added to active time
   - The idle time starts counting from that point

2. **Transition from idle to active**:
   - When the user becomes active again, the time since the last activity check is added to idle time
   - The active time starts counting from that point

3. **Final time calculation**:
   - When the timer is stopped, the final active/idle time is calculated based on the current state
   - The total time (active + idle) is verified to match the total duration
   - Any discrepancies are adjusted to ensure consistency

## Future Improvements

Potential future improvements to the activity tracking mechanism:

1. **Configurable idle threshold**: Allow users to configure the idle threshold
2. **Activity visualization**: Visualize active and idle periods in the UI
3. **More detailed activity metrics**: Track more detailed activity metrics (e.g., keystrokes per minute)
4. **Automatic break detection**: Detect and suggest breaks based on activity patterns