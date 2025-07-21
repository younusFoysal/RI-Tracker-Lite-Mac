# CORS Issue Fix Documentation

## Problem Description

The application was experiencing CORS (Cross-Origin Resource Sharing) errors when making API calls after building the executable. This occurred because the API was being called from `http://127.0.0.1:25640`, which is the local server address when running the packaged application.

## Solution Implemented

To resolve the CORS issues, we've implemented a proxy approach where the Python backend handles all API calls to the remote server instead of the frontend making direct calls. This eliminates CORS issues because:

1. The Python backend doesn't have the same origin policy restrictions that browsers enforce
2. The frontend now communicates only with the local Python backend via PyWebView's JavaScript bridge
3. The Python backend forwards requests to the remote API and returns the responses to the frontend

## Changes Made

### 1. Backend Changes (main.py)

- Added a new `auth_data` table to the SQLite database to store authentication tokens and user data
- Implemented methods to:
  - Load and save authentication data from/to the database
  - Login to the remote API and store the token
  - Get profile data using the stored token
  - Logout and clear stored authentication data
  - Check if the user is authenticated
  - Get current user data

### 2. Frontend Changes

#### AuthContext.jsx
- Updated to use the Python backend API methods instead of making direct API calls
- Replaced direct fetch calls with `window.pywebview.api` calls to the Python backend methods
- Added a `checkAuthStatus` function to check authentication status on initial load
- Updated the login and logout functions to use the Python backend
- Added a `getProfile` function to get profile data using the Python backend

#### App.jsx
- Updated to use the Python backend for fetching employee data instead of making direct API calls

## Verification Steps

To verify that the CORS issues are resolved when running the application as an executable:

1. Build the executable using PyInstaller:
   ```
   cd backend
   pyinstaller --onefile --windowed --icon=icon.ico main.py
   ```

2. Run the generated executable (located in the `dist` folder)

3. Attempt to log in with valid credentials

4. Verify that no CORS errors appear in the browser console (you can check this by running the executable with the `--dev` flag to enable developer tools)

5. Verify that you can successfully log in and view your profile information

## Troubleshooting

If you encounter any issues:

1. Check the Python console output for error messages
2. Verify that the `requests` package is installed (`pip install requests`)
3. Ensure that the remote API endpoints are accessible from the machine running the executable
4. Check that the database file (`tracker.db`) is writable by the application

## Additional Notes

- The authentication token is now stored securely in the SQLite database instead of localStorage
- The frontend no longer needs to handle the token directly, as all authenticated requests are made through the Python backend
- This approach provides better security as sensitive information like tokens are not exposed to the frontend

## Future Improvements

- Implement token refresh functionality
- Add error handling for network connectivity issues
- Implement a more robust database schema with encryption for sensitive data
- Add logging for better debugging