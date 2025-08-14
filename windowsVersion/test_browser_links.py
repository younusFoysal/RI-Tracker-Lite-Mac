import os
import sys
import time
import sqlite3
import tempfile
from datetime import datetime, timezone, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the Api class from main.py
from main import Api

def test_browser_paths():
    """Test getting browser paths"""
    api = Api()
    browser_paths = api.get_browser_paths()
    
    print("Browser Paths:")
    for browser, paths in browser_paths.items():
        print(f"{browser}: {len(paths)} paths found")
        for path in paths:
            print(f"  - {path}")
    
    return browser_paths

def test_browser_history(long_term=False):
    """Test extracting browser history
    
    Args:
        long_term (bool): If True, use a 24-hour cutoff time to simulate the first check
                          after app startup. If False, use a 10-minute cutoff time.
    """
    api = Api()
    browser_paths = api.get_browser_paths()
    
    # Calculate cutoff time
    if long_term:
        # 24 hours ago (simulating first check after app startup)
        cutoff_time = int(time.time()) - (24 * 60 * 60)
        print("\nBrowser History (last 24 hours - simulating first check after app startup):")
    else:
        # 10 minutes ago (regular check)
        cutoff_time = int(time.time()) - 600
        print("\nBrowser History (last 10 minutes - regular check):")
    
    total_entries = 0
    
    # Test Chrome/Brave/Edge history
    for browser in ['chrome', 'brave', 'edge']:
        history_files = browser_paths.get(browser, [])
        for history_file in history_files:
            history_data = api.get_chrome_history(history_file, cutoff_time)
            print(f"{browser} ({os.path.basename(os.path.dirname(history_file))}): {len(history_data)} entries")
            total_entries += len(history_data)
            
            # Print first 5 entries
            for i, entry in enumerate(history_data[:5]):
                visit_count = entry.get('visit_count', 'N/A')
                print(f"  {i+1}. {entry['title']} - {entry['url']} (Visit count: {visit_count})")
    
    # Test Firefox history
    for history_file in browser_paths.get('firefox', []):
        history_data = api.get_firefox_history(history_file, cutoff_time)
        print(f"Firefox ({os.path.basename(os.path.dirname(history_file))}): {len(history_data)} entries")
        total_entries += len(history_data)
        
        # Print first 5 entries
        for i, entry in enumerate(history_data[:5]):
            visit_count = entry.get('visit_count', 'N/A')
            print(f"  {i+1}. {entry['title']} - {entry['url']} (Visit count: {visit_count})")
    
    # Test Safari history
    for history_file in browser_paths.get('safari', []):
        history_data = api.get_safari_history(history_file, cutoff_time)
        print(f"Safari: {len(history_data)} entries")
        total_entries += len(history_data)
        
        # Print first 5 entries
        for i, entry in enumerate(history_data[:5]):
            visit_count = entry.get('visit_count', 'N/A')
            print(f"  {i+1}. {entry['title']} - {entry['url']} (Visit count: {visit_count})")
    
    print(f"\nTotal entries found: {total_entries}")
    
    return total_entries

def test_first_check_flag():
    """Test the first_check flag in check_browser_links method
    
    This test specifically verifies that the first_check flag in the check_browser_links
    method is working correctly and capturing existing browser history.
    """
    # Create a temporary database file
    temp_dir = tempfile.gettempdir()
    temp_db = os.path.join(temp_dir, f'test_tracker_{int(time.time())}.db')
    
    # Initialize the database
    with sqlite3.connect(temp_db) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT,
                timestamp TEXT,
                duration INTEGER
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS auth_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT,
                user_data TEXT
            )
        ''')
    
    # Monkey patch the db_file variable in main.py
    import backend.main
    original_db_file = backend.main.db_file
    backend.main.db_file = temp_db
    
    try:
        # Create Api instance
        api = Api()
        
        # Set up mock authentication data
        api.auth_token = "test_token"
        api.user_data = {"employeeId": "test_employee", "companyId": "test_company"}
        api.session_id = "test_session"
        
        # Start timer (required for check_browser_links)
        api.start_time = time.time()
        
        # Ensure last_link_check_time is None to trigger first_check flag
        api.last_link_check_time = None
        
        print("\nTesting first_check flag in check_browser_links method...")
        print("This should use a 24-hour window to capture existing browser history")
        
        # Call check_browser_links directly (should use 24-hour window due to first_check flag)
        api.check_browser_links()
        
        # Prepare links for session
        links_data_first_check = api.prepare_links_for_session()
        
        print(f"\nLinks data collected with first_check=True: {len(links_data_first_check)} links")
        for i, link in enumerate(links_data_first_check[:10]):  # Show first 10 links
            print(f"  {i+1}. {link['title']} - {link['url']} ({link['timeSpent']} seconds)")
        
        # Now reset and test with a regular check (not first check)
        api.links_usage = {}
        api.last_link_check_time = time.time() - 60  # Set to 1 minute ago (not first check)
        
        print("\nTesting regular check (not first check) in check_browser_links method...")
        print("This should use a 10-minute window")
        
        # Call check_browser_links again (should use 10-minute window)
        api.check_browser_links()
        
        # Prepare links for session
        links_data_regular_check = api.prepare_links_for_session()
        
        print(f"\nLinks data collected with first_check=False: {len(links_data_regular_check)} links")
        for i, link in enumerate(links_data_regular_check[:10]):  # Show first 10 links
            print(f"  {i+1}. {link['title']} - {link['url']} ({link['timeSpent']} seconds)")
        
        # Compare results
        print("\nComparison of first check vs. regular check:")
        print(f"First check (24-hour window): {len(links_data_first_check)} links")
        print(f"Regular check (10-minute window): {len(links_data_regular_check)} links")
        
        # Clean up
        api.stop_link_tracking()
        api.start_time = None
        
        return {
            "first_check": links_data_first_check,
            "regular_check": links_data_regular_check
        }
    finally:
        # Restore original db_file
        backend.main.db_file = original_db_file
        
        # Clean up temporary database
        try:
            os.remove(temp_db)
        except:
            pass

def test_link_tracking():
    """Test link tracking functionality"""
    # Create a temporary database file
    temp_dir = tempfile.gettempdir()
    temp_db = os.path.join(temp_dir, f'test_tracker_{int(time.time())}.db')
    
    # Initialize the database
    with sqlite3.connect(temp_db) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT,
                timestamp TEXT,
                duration INTEGER
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS auth_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT,
                user_data TEXT
            )
        ''')
    
    # Monkey patch the db_file variable in main.py
    import backend.main
    original_db_file = backend.main.db_file
    backend.main.db_file = temp_db
    
    try:
        # Create Api instance
        api = Api()
        
        # Set up mock authentication data
        api.auth_token = "test_token"
        api.user_data = {"employeeId": "test_employee", "companyId": "test_company"}
        api.session_id = "test_session"
        
        # Start link tracking
        print("\nStarting link tracking...")
        api.start_time = time.time()
        api.start_link_tracking()
        
        # Wait for a few seconds to collect data
        print("Waiting for 5 seconds to collect data...")
        time.sleep(5)
        
        # Check browser links
        api.check_browser_links()
        
        # Prepare links for session
        links_data = api.prepare_links_for_session()
        
        print(f"\nLinks data collected: {len(links_data)} links")
        for i, link in enumerate(links_data[:10]):  # Show first 10 links
            print(f"  {i+1}. {link['title']} - {link['url']} ({link['timeSpent']} seconds)")
        
        # Stop link tracking
        api.stop_link_tracking()
        api.start_time = None
        
        return links_data
    finally:
        # Restore original db_file
        backend.main.db_file = original_db_file
        
        # Clean up temporary database
        try:
            os.remove(temp_db)
        except:
            pass

if __name__ == "__main__":
    print("Testing Browser Link Tracking")
    print("=" * 50)
    
    # Test getting browser paths
    browser_paths = test_browser_paths()
    
    # Test extracting browser history with regular 10-minute window
    print("\n--- Testing Regular Browser History (10-minute window) ---")
    regular_history_entries = test_browser_history(long_term=False)
    
    # Test extracting browser history with extended 24-hour window
    print("\n--- Testing Long-Term Browser History (24-hour window) ---")
    long_term_history_entries = test_browser_history(long_term=True)
    
    # Compare results
    print("\nComparison of regular vs. long-term history checks:")
    print(f"Regular check (10-minute window): {regular_history_entries} entries")
    print(f"Long-term check (24-hour window): {long_term_history_entries} entries")
    print(f"Difference: {long_term_history_entries - regular_history_entries} additional entries in long-term check")
    
    # Test the first_check flag in check_browser_links
    print("\n--- Testing First Check Flag in check_browser_links ---")
    first_check_results = test_first_check_flag()
    
    # Test link tracking functionality
    print("\n--- Testing Link Tracking Functionality ---")
    links_data = test_link_tracking()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"- Regular history check (10-minute window): {regular_history_entries} entries")
    print(f"- Long-term history check (24-hour window): {long_term_history_entries} entries")
    print(f"- First check links: {len(first_check_results['first_check'])} links")
    print(f"- Regular check links: {len(first_check_results['regular_check'])} links")
    print(f"- Link tracking: {len(links_data)} links")
    
    print("\nTest completed successfully!")