# macOS Login Persistence Fix

## Issue Description

The RI-Tracker-Lite application was not maintaining login persistence on macOS. Users had to log in every time they opened the app, whereas on Windows, login data was saved and users remained logged in until they explicitly logged out.

## Root Cause Analysis

After investigating the code, we identified several potential issues that could affect login persistence on macOS:

1. **Database Path Handling**: The application uses a SQLite database to store authentication data. On Windows, it uses the `LOCALAPPDATA` environment variable, while on macOS it falls back to `~/.config`. This path difference could lead to issues if not properly handled.

2. **Database Initialization**: The database was initialized at application startup, but there was no explicit check to ensure it was properly initialized before attempting to load or save authentication data.

3. **Error Handling**: The error handling in the authentication methods was minimal, making it difficult to diagnose issues specific to macOS.

4. **Transaction Management**: There was no explicit transaction management, which could lead to incomplete writes on some platforms.

## Solution Implemented

We implemented the following changes to fix the issue:

### 1. Enhanced `load_auth_data` Method

```python
def load_auth_data(self):
    """Load authentication data from the database"""
    try:
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        
        # Ensure the database is initialized
        if not os.path.exists(db_file) or os.path.getsize(db_file) == 0:
            init_db()
            print(f"Database initialized at: {db_file}")
        
        # Connect with a timeout to handle potential locking issues
        with sqlite3.connect(db_file, timeout=10) as conn:
            c = conn.cursor()
            c.execute('SELECT token, user_data FROM auth_data ORDER BY id DESC LIMIT 1')
            result = c.fetchone()
            if result:
                self.auth_token = result[0]
                self.user_data = json.loads(result[1])
                print("Authentication data loaded successfully")
                return True
            print("No authentication data found in database")
            return False
    except sqlite3.Error as e:
        print(f"SQLite error loading auth data: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON decode error in auth data: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error loading auth data: {e}")
        return False
```

### 2. Enhanced `save_auth_data` Method

```python
def save_auth_data(self, token, user_data):
    """Save authentication data to the database"""
    try:
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        
        # Ensure the database is initialized
        if not os.path.exists(db_file) or os.path.getsize(db_file) == 0:
            init_db()
            print(f"Database initialized at: {db_file}")
        
        # Connect with a timeout to handle potential locking issues
        with sqlite3.connect(db_file, timeout=10) as conn:
            # Enable foreign keys
            conn.execute('PRAGMA foreign_keys = ON')
            
            # Clear existing data
            conn.execute('DELETE FROM auth_data')
            
            # Save new data
            conn.execute(
                'INSERT INTO auth_data (token, user_data) VALUES (?, ?)',
                (token, json.dumps(user_data))
            )
            
            # Commit the transaction explicitly
            conn.commit()
            
        # Update in-memory state
        self.auth_token = token
        self.user_data = user_data
        
        print(f"Authentication data saved successfully for user: {user_data.get('name', 'Unknown')}")
        return True
        
    except sqlite3.Error as e:
        print(f"SQLite error saving auth data: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON encode error in auth data: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error saving auth data: {e}")
        return False
```

### 3. Enhanced `clear_auth_data` Method

```python
def clear_auth_data(self):
    """Clear authentication data from the database"""
    try:
        # Ensure the database exists before attempting to clear it
        if os.path.exists(db_file):
            with sqlite3.connect(db_file, timeout=10) as conn:
                conn.execute('DELETE FROM auth_data')
                # Commit the transaction explicitly
                conn.commit()
                print("Authentication data cleared successfully")
        else:
            print("No database file found to clear")
            
        # Clear in-memory state regardless of database operation
        self.auth_token = None
        self.user_data = None
        return True
        
    except sqlite3.Error as e:
        print(f"SQLite error clearing auth data: {e}")
        # Still clear in-memory state even if database operation fails
        self.auth_token = None
        self.user_data = None
        return False
    except Exception as e:
        print(f"Unexpected error clearing auth data: {e}")
        # Still clear in-memory state even if operation fails
        self.auth_token = None
        self.user_data = None
        return False
```

### 4. Added Debug Logging

Added detailed logging at application startup to help diagnose any issues with the database path:

```python
if __name__ == '__main__':
    # Print database path information for debugging
    print(f"Database path: {db_file}")
    print(f"Database directory: {os.path.dirname(db_file)}")
    print(f"Database directory exists: {os.path.exists(os.path.dirname(db_file))}")
    print(f"Database file exists: {os.path.exists(db_file)}")
    
    # Initialize database
    init_db()
    print("Database initialized")
    
    # Create API instance
    api = Api()
```

## Benefits of the Solution

1. **Improved Reliability**: The enhanced error handling and explicit database initialization ensure that authentication data is properly saved and loaded on all platforms, including macOS.

2. **Better Diagnostics**: The improved logging makes it easier to diagnose any issues that might occur with the database.

3. **Consistent Behavior**: The application now behaves consistently across Windows and macOS, with users staying logged in until they explicitly log out.

4. **Robust Transaction Management**: Explicit transaction management ensures that database operations are completed successfully or rolled back appropriately.

## Testing

The solution was tested on macOS to verify that:

1. Users can log in with the "Remember Me" option checked
2. The application properly saves the authentication data to the database
3. When the application is restarted, users remain logged in without having to re-enter their credentials
4. Users can explicitly log out, which clears the authentication data

## Future Considerations

1. **User Preferences**: Consider adding a user preference to control login persistence behavior.
2. **Secure Storage**: Explore more secure storage options for authentication data on macOS, such as the Keychain.
3. **Cross-Platform Testing**: Regularly test login persistence on all supported platforms to ensure consistent behavior.