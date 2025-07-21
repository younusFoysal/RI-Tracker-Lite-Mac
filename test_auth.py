import sqlite3
import json
import os
import sys
import importlib.util

# Get the absolute path to the main.py file
main_path = os.path.join(os.path.dirname(__file__), 'backend', 'main.py')

# Load the main module
spec = importlib.util.spec_from_file_location("main", main_path)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

# Get the Api class, init_db function, and db_file variable from the main module
Api = main.Api
init_db = main.init_db
db_file = main.db_file

def test_auth_flow():
    """Test the authentication flow"""
    print("Testing authentication flow...")
    
    # Initialize the database
    init_db()
    
    # Create an instance of the Api class
    api = Api()
    
    # Test login with invalid credentials
    print("\nTesting login with invalid credentials...")
    result = api.login("invalid@example.com", "wrongpassword")
    print(f"Login result: {result}")
    assert not result['success'], "Login with invalid credentials should fail"
    
    # Test login with valid credentials (replace with actual credentials for testing)
    print("\nTesting login with valid credentials...")
    print("NOTE: Replace with actual credentials for real testing")
    email = "test@test.com"  # Replace with actual email
    password = "123456"    # Replace with actual password
    
    print(f"Attempting login with email: {email}")
    result = api.login(email, password)
    print(f"Login result: {result}")
    
    # If login is successful, test other auth functions
    if result['success']:
        print("\nLogin successful, testing other auth functions...")
        
        # Test is_authenticated
        auth_status = api.is_authenticated()
        print(f"Authentication status: {auth_status}")
        assert auth_status['authenticated'], "User should be authenticated after login"
        
        # Test get_current_user
        user_result = api.get_current_user()
        print(f"Current user: {user_result}")
        assert user_result['success'], "Should be able to get current user after login"
        
        # Test get_profile
        profile_result = api.get_profile()
        print(f"Profile result: {profile_result}")
        assert profile_result['success'], "Should be able to get profile after login"
        
        # Test logout
        logout_result = api.logout()
        print(f"Logout result: {logout_result}")
        assert logout_result['success'], "Logout should be successful"
        
        # Verify user is no longer authenticated
        auth_status = api.is_authenticated()
        print(f"Authentication status after logout: {auth_status}")
        assert not auth_status['authenticated'], "User should not be authenticated after logout"
    else:
        print("\nSkipping other auth tests because login failed")
    
    print("\nAuth flow test completed")

def check_db_state():
    """Check the current state of the auth_data table"""
    print("\nChecking database state...")
    try:
        with sqlite3.connect(db_file) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM auth_data')
            rows = c.fetchall()
            if rows:
                print(f"Found {len(rows)} auth records:")
                for row in rows:
                    print(f"ID: {row[0]}, Token: {row[1][:10]}..., User data: {row[2][:50]}...")
            else:
                print("No auth records found in database")
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    # Initialize the database first to ensure tables are created
    print("Initializing database...")
    init_db()
    
    # Check initial database state
    check_db_state()
    
    # Run the auth flow test
    test_auth_flow()
    
    # Check final database state
    check_db_state()