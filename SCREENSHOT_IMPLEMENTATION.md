# Multi-Monitor Screenshot Implementation

## Overview

The application now supports capturing screenshots from multiple monitors using the `mss` Python package. This implementation is cross-platform and works on Windows, macOS, and Linux.

## Changes Made

1. Added `mss` and `mss.tools` imports to `main.py`
2. Updated the `take_screenshot` method to use `mss` instead of platform-specific code
3. Added logging of monitor information for debugging purposes
4. Updated the `upload_screenshot` method to use base64 encoding and JSON payload
5. Fixed the API endpoint to use the correct URL

## How It Works

The screenshot functionality works as follows:

1. When a session is active, screenshots are scheduled at random intervals between 1-8 minutes
2. When it's time to take a screenshot, the `take_screenshot` method is called
3. The method uses `mss` to capture a screenshot of all monitors combined
4. The screenshot is saved to a temporary file
5. The screenshot is read, base64 encoded, and uploaded to the RemoteIntegrity file server
6. The screenshot URL and timestamp are included in the next session update

## Screenshot Upload Process

The screenshot upload process has been improved to handle the server requirements:

1. The image file is read and base64 encoded
2. A JSON payload is created with the base64 encoded image and filename
3. The Content-Type header is set to 'application/json'
4. The API key is included in the headers
5. The request is sent to the correct HTTPS endpoint
6. The temporary file is deleted after the upload attempt

This approach resolves the 400 status code error that was occurring with the previous implementation.

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

The application also logs information about the upload process:

```
Image Upload response: <Response [200]>
```

If the upload fails, it will log:

```
API request failed with status code XXX
Failed to upload screenshot
```

## Cross-Platform Compatibility

The `mss` package is designed to work on Windows, macOS, and Linux. The implementation should work on all these platforms without modification.

## Requirements

The `mss` package is included in the `requirements.txt` file with version `>=10.0.0`. It will be installed automatically when the application is deployed.

## Troubleshooting

If you encounter issues with the screenshot functionality:

1. Check that the API endpoint is correct and accessible
2. Verify that the API key is valid
3. Check that the image file is being properly base64 encoded
4. Ensure that the JSON payload is correctly formatted
5. Look for any error messages in the console output

## Future Improvements

Possible future improvements to the screenshot functionality:

1. Add an option to capture individual monitors instead of all monitors combined
2. Add an option to adjust the screenshot quality or resolution
3. Add an option to blur sensitive information in screenshots
4. Add an option to disable screenshots for specific applications or windows
5. Implement retry logic for failed uploads
6. Add progress indicators for screenshot uploads