# PyInstaller Warnings Fix

## Changes Made

### 1. Updated Requirements

Added missing dependencies to `backend/requirements.txt`:
- `psutil>=5.9.0`
- `requests>=2.28.0`

These modules are imported in `main.py` but were not listed in the requirements file.

### 2. Updated PyInstaller Spec Files

Added hidden imports to all three spec files:
- `main.spec` (root directory)
- `backend/main.spec`
- `backend/RI Tracker.spec`

Added the following hidden imports:
```python
hiddenimports=[
    'requests', 'urllib3', 'chardet', 'certifi', 'idna',  # requests and its dependencies
    'psutil',
    'pynput', 'pynput.keyboard', 'pynput.mouse',  # pynput and its modules
    'mss', 'mss.tools',
    'screeninfo',
    'webview', 'webview.platforms.winforms',  # webview and Windows-specific platform
    'sqlite3',
    'json', 'threading', 'subprocess', 'platform', 'shutil', 'random', 'tempfile', 'base64',
    'glob', 're', 'pathlib', 'datetime',
],
```

## Testing Instructions

1. Install the updated dependencies:
   ```
   pip install -r backend/requirements.txt
   ```

2. Build the application using PyInstaller:
   ```
   pyinstaller main.spec
   ```

3. Check if the warnings have been reduced or eliminated.

## Handling Remaining Warnings

Some warnings may still appear after these changes. Here's how to handle them:

1. **Platform-specific modules**: Warnings about missing modules like `posix`, `termios`, `grp`, `pwd`, etc. can be safely ignored on Windows as they are POSIX-specific modules.

2. **Optional modules**: Warnings about modules marked as "optional" or "conditional" can usually be ignored if the application runs correctly.

3. **Test-related modules**: Warnings about missing modules like `pytest` can be ignored as they are only used for testing, not for the actual application.

4. **Web framework modules**: Warnings about missing modules like `bottle`, `tornado`, etc. can be ignored if the application doesn't use these web frameworks.

5. **GUI framework modules**: If you're using a specific GUI framework (e.g., PyQt5, winforms), you can ignore warnings about other GUI frameworks.

If you encounter specific issues after building, you may need to add more modules to the `hiddenimports` list in the spec files.

## Note on PyInstaller Warnings

The warnings in `warn-main.txt` don't necessarily indicate problems with the application. As stated in the file itself:

> This file lists modules PyInstaller was not able to find. This does not necessarily mean this module is required for running your program. Python and Python 3rd-party packages include a lot of conditional or optional modules.

The changes made should address the most critical warnings, but some warnings about optional or platform-specific modules may remain.