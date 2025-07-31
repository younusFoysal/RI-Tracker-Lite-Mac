# macOS Timer Crash Fix and Permission Handling

## Issue Description

The RI-Tracker-Lite application was crashing on macOS when users clicked the "Start Timer" button. The crash was occurring with exit code 133 (interrupted by signal 5: SIGTRAP).

## Root Cause Analysis

After investigating the code, we identified that the crash was related to the use of the `pynput` library for system-wide keyboard and mouse tracking. On macOS, `pynput` requires special permissions to monitor input events, and if these permissions aren't properly granted, it can cause the application to crash.

The crash specifically occurred during the `start_timer` method execution, which initializes activity tracking using `pynput` listeners for keyboard and mouse events.

## Solution Implemented

We implemented the following changes to fix the issue:

### Initial Fix (Version 1)

1. Added platform-specific detection for macOS (Darwin) in the pynput initialization code
2. Automatically disabled system-wide activity tracking on macOS to prevent the crash
3. Added informative log messages to explain the fallback behavior
4. Ensured the application gracefully falls back to browser-based activity tracking when system-wide tracking is disabled

### Enhanced Solution (Version 2)

After confirming that pynput is a cross-platform library that should work on macOS with proper permissions, we implemented an enhanced solution:

1. Added proper permission detection and handling for macOS
2. Created a mechanism to check if input monitoring permissions are granted
3. Added a method to guide users through the permission granting process
4. Implemented a toggle to enable/disable system-wide tracking
5. Updated the activity tracking to gracefully handle permission issues

## Code Changes

### Enhanced Permission Handling

1. Modified the pynput import section to support macOS with permission checking:

```python
# Import pynput for system-wide keyboard and mouse tracking
try:
    from pynput import keyboard, mouse
    
    # Check if we're on macOS
    if platform.system() == 'Darwin':
        # pynput is available, but we need to check permissions on macOS
        # We'll set this to True initially, but the actual check will happen
        # when the user tries to enable system-wide tracking
        print("macOS detected. System-wide activity tracking will require permissions.")
        PYNPUT_AVAILABLE = True
        MACOS_PERMISSIONS_CHECKED = False
    else:
        # On other platforms, we can use pynput directly
        PYNPUT_AVAILABLE = True
        MACOS_PERMISSIONS_CHECKED = True
except ImportError:
    print("pynput library not available. System-wide activity tracking will be disabled.")
    PYNPUT_AVAILABLE = False
    MACOS_PERMISSIONS_CHECKED = False
```

2. Added methods to check and request permissions:

```python
def check_macos_permissions(self):
    """Check if pynput has necessary permissions on macOS"""
    if platform.system() != 'Darwin':
        # Not on macOS, so permissions are not an issue
        return {"success": True, "has_permissions": True}
        
    try:
        # Try to create a temporary listener to check permissions
        # This will raise an exception if permissions are not granted
        temp_listener = keyboard.Listener(on_press=lambda key: None)
        temp_listener.start()
        temp_listener.stop()
        
        # If we get here, permissions are granted
        global MACOS_PERMISSIONS_CHECKED
        MACOS_PERMISSIONS_CHECKED = True
        self.macos_permissions_checked = True
        
        return {"success": True, "has_permissions": True}
    except Exception as e:
        error_str = str(e).lower()
        if "permission" in error_str or "accessibility" in error_str or "privacy" in error_str:
            # Permission-related error
            return {"success": True, "has_permissions": False, "message": str(e)}
        else:
            # Some other error
            return {"success": False, "message": f"Error checking permissions: {str(e)}"}

def request_macos_permissions(self):
    """Guide the user to enable input monitoring permissions on macOS"""
    if platform.system() != 'Darwin':
        return {"success": False, "message": "Not on macOS, permissions not required"}
        
    # Open System Preferences to the Security & Privacy pane
    try:
        # First check if we already have permissions
        check_result = self.check_macos_permissions()
        if check_result.get("has_permissions", False):
            return {"success": True, "message": "Permissions already granted"}
            
        # Open System Preferences to the Security & Privacy pane, Input Monitoring tab
        subprocess.run([
            "open", 
            "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent"
        ])
        
        return {
            "success": True, 
            "message": "Please enable input monitoring for this application in System Preferences"
        }
    except Exception as e:
        return {"success": False, "message": f"Error requesting permissions: {str(e)}"}
```

3. Updated the activity tracking initialization to handle permissions properly:

```python
# For macOS, check permissions if system tracking is enabled but permissions haven't been checked
if platform.system() == 'Darwin' and self.system_tracking_enabled and not self.macos_permissions_checked:
    permission_check = self.check_macos_permissions()
    if not permission_check.get("has_permissions", False):
        print("macOS input monitoring permissions not granted. System-wide tracking disabled.")
        self.system_tracking_enabled = False
```

## Benefits of the Enhanced Solution

1. **Cross-Platform Compatibility**: Properly supports pynput on all platforms including macOS.
2. **User Control**: Allows users to enable system-wide tracking on macOS if they choose to grant permissions.
3. **Graceful Degradation**: Falls back to browser-based tracking if permissions aren't granted.
4. **User Guidance**: Helps users through the permission granting process.
5. **Stability**: Prevents crashes while still offering full functionality when possible.

## Testing

A test script (`test_macos_fix.py`) has been created to verify the macOS permission handling. This script:

1. Checks the current permission status
2. Guides the user through granting permissions if needed
3. Tests enabling system-wide tracking
4. Verifies that activity tracking works without crashing

## Future Considerations

1. Adding a user interface element to guide users through the permission process
2. Implementing a persistent setting to remember the user's preference for system-wide tracking
3. Exploring alternative methods for activity tracking on macOS as a backup

The enhanced solution provides the best balance of functionality, user control, and stability across all platforms.