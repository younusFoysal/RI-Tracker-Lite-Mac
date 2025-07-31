# PyInstaller Path Fix for RI Tracker

## Issue Description
When running the application directly through `main.py`, the timer works fine, but when built as an executable with PyInstaller, stopping the timer causes an error.

## Root Cause
The issue is related to how PyInstaller packages resources. When an application is packaged with PyInstaller, it extracts resources to a temporary directory at runtime, accessible through `sys._MEIPASS`. The application was not handling this special path correctly for the frontend files.

## Fix Implemented
Added proper PyInstaller resource path handling in `main.py`:

```python
# Handle PyInstaller bundled resources
# When running as a PyInstaller executable, resources are in a temporary directory
# accessible through sys._MEIPASS
base_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

# Get the appropriate URL
if DEBUG:
    url = os.path.join(base_dir, "dist", "index.html")
    debug = True
    print("Running in DEVELOPMENT mode with DevTools enabled")
else:
    url = os.path.join(base_dir, "dist", "index.html")
    debug = False
    print("Running in PRODUCTION mode")
```

This change ensures that the application correctly locates the frontend files whether running as a script or as a PyInstaller executable.

## Testing the Fix

1. Build the executable with PyInstaller:
   ```
   pyinstaller --onefile --noconsole --icon=icon.ico --add-data "dist;dist" main.py
   ```

2. Run the executable and test the timer functionality:
   - Start the timer
   - Let it run for a few minutes
   - Stop the timer
   - Verify that no errors occur

3. Alternatively, you can run the test script to verify the path handling:
   ```
   python test_pyinstaller_paths.py
   ```

## Additional Notes

- The database file is stored in the user's local app data folder, which is a good practice and works correctly even when packaged as an executable.
- The fix only affects how the application locates the frontend files, not the database or other user data.
- This fix is compatible with all platforms (Windows, macOS, Linux) as it uses platform-independent path handling.