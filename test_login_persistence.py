#!/usr/bin/env python3
"""
Test script to verify the macOS login persistence fix.
This script tests that authentication data is properly saved and loaded,
ensuring that users remain logged in after restarting the application.
"""

import os
import sys
import json
import sqlite3
import time

# Add the backend directory to the path so we can import from it
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)

# Import from main.py
from main import Api, db_file

def test_login_persistence():
    """Test that authentication data is properly saved and loaded"""
    print(f"Running login persistence test")
    print(f"Database path: {db_file}")
    
    # Create an instance of the Api class
    api = Api()
    
    # Check if there's existing auth data
    print("\n=== Checking existing authentication data ===")
    auth_check = api.is_authenticated()
    print(f"Initial authentication check: {auth_check}")
    
    if auth_check.get('authenticated', False):
        print("Already authenticated, retrieving user data...")
        user_data = api.get_current_user()
        if user_data.get('success', False):
            print(f"User data: {user_data['user'].get('name', 'Unknown')}")
        else:
            print("Could not retrieve user data")
    else:
        print("Not authenticated")
    
    # Force reload of auth data
    print("\n=== Forcing reload of authentication data ===")
    reload_result = api.reload_auth_data()
    print(f"Reload result: {reload_result}")
    
    # Check authentication again
    auth_check = api.is_authenticated()
    print(f"Authentication check after reload: {auth_check}")
    
    # Directly check the database
    print("\n=== Directly checking database ===")
    try:
        if os.path.exists(db_file):
            with sqlite3.connect(db_file) as conn:
                c = conn.cursor()
                c.execute('SELECT token, user_data FROM auth_data ORDER BY id DESC LIMIT 1')
                result = c.fetchone()
                if result:
                    token = result[0]
                    user_data_str = result[1]
                    print(f"Token exists in DB: {token is not None}")
                    print(f"Token length: {len(token) if token else 0}")
                    
                    try:
                        user_data = json.loads(user_data_str)
                        print(f"User data parsed successfully")
                        print(f"User name: {user_data.get('name', 'Unknown')}")
                        print(f"User data keys: {list(user_data.keys())}")
                    except json.JSONDecodeError as e:
                        print(f"Error parsing user data: {e}")
                        print(f"First 100 chars of user data: {user_data_str[:100]}...")
                else:
                    print("No authentication data found in database")
        else:
            print(f"Database file does not exist: {db_file}")
    except Exception as e:
        print(f"Error checking database: {e}")
    
    # Simulate application restart
    print("\n=== Simulating application restart ===")
    print("Creating new Api instance...")
    new_api = Api()
    
    # Check if auth data is loaded in the new instance
    auth_check = new_api.is_authenticated()
    print(f"Authentication check in new instance: {auth_check}")
    
    if auth_check.get('authenticated', False):
        print("Successfully authenticated after restart")
        user_data = new_api.get_current_user()
        if user_data.get('success', False):
            print(f"User data after restart: {user_data['user'].get('name', 'Unknown')}")
            return True
        else:
            print("Could not retrieve user data after restart")
            return False
    else:
        print("Not authenticated after restart")
        return False

if __name__ == "__main__":
    test_login_persistence()