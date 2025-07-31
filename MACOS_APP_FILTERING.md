# macOS System Application Filtering

## Issue Description

The RI-Tracker-Lite application was collecting all running applications and processes on macOS, including system applications and processes. This behavior was undesirable as system applications should be excluded from tracking, similar to how Windows system applications were already being filtered out.

## Implementation Details

### Overview

We've enhanced the application tracking functionality to filter out macOS system applications and processes. This ensures that only user applications are tracked, providing more relevant and focused activity data.

### Changes Made

1. **Added macOS System Process Names**: We added a comprehensive list of macOS system processes and applications to the `system_process_names` list in the `check_running_applications` function.

2. **Added macOS System Directories**: We added macOS system directories to the `system_dirs` list to filter out applications based on their installation paths.

### Code Changes

The following changes were made to the `check_running_applications` function in `main.py`:

```python
# Define system process patterns to exclude
system_process_names = [
    # Windows system processes
    'System', 'Registry', 'smss.exe', 'csrss.exe', 'wininit.exe', 
    # ... other Windows processes ...
    
    # macOS system processes and applications
    'launchd', 'kernel_task', 'WindowServer', 'loginwindow', 'SystemUIServer',
    'Finder', 'Dock', 'Spotlight', 'ControlCenter', 'NotificationCenter',
    'mds', 'mds_stores', 'mdworker', 'distnoted', 'cfprefsd', 'iconservicesd',
    'secd', 'securityd', 'opendirectoryd', 'powerd', 'coreaudiod', 'syslogd',
    'fseventsd', 'systemstats', 'configd', 'watchdogd', 'amfid', 'keybagd',
    'softwareupdated', 'corespeechd', 'mediaremoted', 'endpointsecurityd',
    'logd', 'smd', 'UserEventAgent', 'APFSUserAgent', 'AirPlayUIAgent',
    'Safari', 'Mail', 'Calendar', 'Contacts', 'Notes', 'Photos', 'Messages',
    'FaceTime', 'Maps', 'Music', 'AppStore', 'System Preferences', 'Terminal',
    'Activity Monitor', 'Console', 'Keychain Access', 'Preview', 'TextEdit',
    'Calculator', 'Chess', 'Dictionary', 'Books', 'FindMy', 'Home', 'News',
    'Podcasts', 'Reminders', 'Stocks', 'TV', 'Voice Memos', 'Weather'
]

# System directories patterns
system_dirs = [
    # Windows system directories
    '\\Windows\\', '\\Windows\\System32\\', '\\Windows\\SysWOW64\\',
    # ... other Windows directories ...
    
    # macOS system directories
    '/System/Library/', '/System/Applications/', '/Library/Apple/', 
    '/usr/libexec/', '/usr/sbin/', '/usr/bin/', '/sbin/', '/bin/',
    '/Library/PrivateFrameworks/', '/Library/Frameworks/',
    '/System/Library/CoreServices/', '/System/Library/PrivateFrameworks/'
]
```

## Testing

A test script (`test_macos_app_filtering.py`) was created to verify that macOS system applications are properly excluded from tracking. The test:

1. Initializes the application tracking variables
2. Runs the `check_running_applications` method
3. Checks if any common macOS system applications were detected
4. Reports success if no system applications were detected

The test confirmed that the implementation successfully filters out macOS system applications.

## Benefits

1. **Improved Data Quality**: By excluding system applications, the tracking data is more focused on user activity.
2. **Reduced Noise**: System processes that aren't relevant to user productivity are filtered out.
3. **Consistent Behavior**: The application now behaves consistently across Windows and macOS platforms.
4. **Privacy Enhancement**: Reduces the amount of system information collected.

## Future Considerations

1. **User Configuration**: Allow users to customize which applications are excluded from tracking.
2. **Linux Support**: Extend the filtering to Linux system applications if needed.
3. **Regular Updates**: Keep the list of system applications updated as macOS evolves.

## Conclusion

The implementation successfully addresses the issue by filtering out macOS system applications from tracking, providing a more focused and relevant view of user activity.