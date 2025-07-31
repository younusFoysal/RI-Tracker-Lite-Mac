import os
import sys
import time

# This script tests the PyInstaller path handling fix
# It simulates starting and stopping the timer to verify the fix works

def main():
    print("Testing PyInstaller path handling fix")
    print("=====================================")
    
    # Check if running as PyInstaller executable
    if getattr(sys, 'frozen', False):
        print("Running as PyInstaller executable")
        print(f"sys._MEIPASS: {sys._MEIPASS}")
    else:
        print("Running as Python script")
    
    # Print current directory and script location
    print(f"Current directory: {os.getcwd()}")
    print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Print DATA_DIR and db_file path
    from backend.main import DATA_DIR, db_file
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"db_file: {db_file}")
    
    # Test frontend path resolution
    base_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    frontend_path = os.path.join(base_dir, "dist", "index.html")
    print(f"Frontend path: {frontend_path}")
    print(f"Frontend file exists: {os.path.exists(frontend_path)}")
    
    # Simulate timer operations
    print("\nSimulating timer operations...")
    
    try:
        # Import the Api class
        from backend.main import Api
        
        # Create an instance
        api = Api()
        
        # Start timer
        print("Starting timer...")
        start_result = api.start_timer("Test Project")
        print(f"Start result: {start_result['success']}")
        
        # Wait a bit
        print("Waiting 3 seconds...")
        time.sleep(3)
        
        # Stop timer
        print("Stopping timer...")
        stop_result = api.stop_timer()
        print(f"Stop result: {stop_result['success']}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()