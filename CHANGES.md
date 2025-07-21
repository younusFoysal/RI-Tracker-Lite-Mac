# Changes Made to Implement "Remember Me" Functionality

## Issue Description
The application was requiring users to log in every time they opened the software, even if they had previously logged in. The requirement was to save login data so that users don't have to log in every time they open the application, but only when they explicitly log out.

## Changes Made

### Frontend Changes

1. **Login.jsx**:
   - Added a state variable `rememberMe` to track the "Remember me" checkbox state
   - Connected the checkbox to this state with an onChange handler
   - Updated the `handleLogin` function to pass the rememberMe state to the login function

2. **AuthContext.jsx**:
   - Modified the login function to accept a `rememberMe` parameter and pass it to the backend
   - Added a default value of `false` for the rememberMe parameter

### Backend Changes

1. **main.py**:
   - Updated the `login` method to accept a `remember_me` parameter
   - Modified the method to conditionally save authentication data based on the remember_me parameter:
     - If remember_me is True: Save authentication data to the database for persistence between app restarts
     - If remember_me is False: Only store authentication data in memory for the current session

## How This Resolves the Issue

With these changes, the application now behaves as follows:

1. **When "Remember me" is checked during login**:
   - Authentication data (token and user info) is saved to the SQLite database
   - When the application is closed and reopened, it loads this saved data
   - The user is automatically logged in without seeing the login page

2. **When "Remember me" is not checked during login**:
   - Authentication data is only stored in memory
   - When the application is closed, this data is lost
   - The next time the application is opened, the user will see the login page

3. **When the user logs out**:
   - The saved authentication data is cleared from the database
   - The next time the application is opened, the user will see the login page

This implementation satisfies the requirement that users should only need to log in again after explicitly logging out, not every time they open the application.