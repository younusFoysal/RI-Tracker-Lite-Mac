# Multi-Monitor Screenshot Implementation

## Overview

The application now supports capturing screenshots from multiple monitors using the `mss` Python package. This implementation is cross-platform and works on Windows, macOS, and Linux.

## Changes Made

1. Added `mss` and `mss.tools` imports to `main.py`
2. Updated the `take_screenshot` method to use `mss` instead of platform-specific code
3. Added logging of monitor information for debugging purposes

## How It Works

The screenshot functionality works as follows:

1. When a session is active, screenshots are scheduled at random intervals between 1-8 minutes
2. When it's time to take a screenshot, the `take_screenshot` method is called
3. The method uses `mss` to capture a screenshot of all monitors combined
4. The screenshot is saved to a temporary file
5. The screenshot is uploaded to the RemoteIntegrity file server
6. The screenshot URL and timestamp are included in the next session update

## Testing

To test the multi-monitor screenshot functionality:

1. Ensure you have multiple monitors connected to your computer
2. Run the application
3. Start a session by clicking the play button
4. Wait for a screenshot to be taken (this happens at a random time between 1-8 minutes)
5. Check the console output for monitor information
6. After the session update (which happens every 10 minutes), verify that the screenshot was uploaded and included in the session data

## Debugging

The application logs monitor information when a screenshot is taken:

```
Captured screenshot of all monitors: X monitor(s) detected
Monitor 1: WIDTHxHEIGHT at position (LEFT,TOP)
Monitor 2: WIDTHxHEIGHT at position (LEFT,TOP)
...
```

This information can be used to verify that all monitors are being detected and captured.

## Cross-Platform Compatibility

The `mss` package is designed to work on Windows, macOS, and Linux. The implementation should work on all these platforms without modification.

## Requirements

The `mss` package is included in the `requirements.txt` file with version `>=10.0.0`. It will be installed automatically when the application is deployed.

## Future Improvements

Possible future improvements to the screenshot functionality:

1. Add an option to capture individual monitors instead of all monitors combined
2. Add an option to adjust the screenshot quality or resolution
3. Add an option to blur sensitive information in screenshots
4. Add an option to disable screenshots for specific applications or windows