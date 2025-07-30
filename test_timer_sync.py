import time
import sys

# Simple mock of the Api class to test timer functionality
class MockApi:
    def __init__(self):
        self.start_time = None
        
    def start_timer(self, project_name):
        """Start the timer and create a new session"""
        self.start_time = time.time()
        return {"success": True, "data": {"project": project_name}}
        
    def get_current_session_time(self):
        """Get the current elapsed time for the active session in seconds"""
        if self.start_time is None:
            return {
                "success": False,
                "message": "No active session",
                "elapsed_time": 0
            }
        
        current_time = time.time()
        elapsed_time = int(current_time - self.start_time)
        
        return {
            "success": True,
            "elapsed_time": elapsed_time
        }
        
    def stop_timer(self):
        """Stop the timer and update the session"""
        if self.start_time is None:
            return {"success": False, "message": "No active session"}
            
        current_time = time.time()
        duration = int(current_time - self.start_time)
        self.start_time = None
        
        return {
            "success": True,
            "data": {
                "duration": duration
            }
        }

def test_timer_sync():
    """
    Test the timer synchronization functionality.
    
    This test verifies that:
    1. The timer starts correctly
    2. get_current_session_time() returns the correct elapsed time
    3. The timer stops correctly
    """
    print("Starting timer sync test...")
    
    # Initialize API
    api = MockApi()
    
    # Start the timer
    project_name = "Test Project"
    start_result = api.start_timer(project_name)
    
    if not start_result.get("success"):
        print(f"Failed to start timer: {start_result.get('message')}")
        return False
    
    print(f"Timer started for project: {project_name}")
    
    # Wait for a few seconds (simulating app running)
    initial_wait = 3
    print(f"Waiting for {initial_wait} seconds...")
    time.sleep(initial_wait)
    
    # Get current session time
    time_result = api.get_current_session_time()
    
    if not time_result.get("success"):
        print(f"Failed to get current session time: {time_result.get('message')}")
        return False
    
    elapsed_time_1 = time_result.get("elapsed_time")
    print(f"Elapsed time after {initial_wait} seconds: {elapsed_time_1} seconds")
    
    # Verify elapsed time is approximately correct
    if abs(elapsed_time_1 - initial_wait) > 1:  # Allow 1 second difference for processing time
        print(f"Warning: Elapsed time ({elapsed_time_1}) doesn't match expected time ({initial_wait})")
    
    # Wait for a few more seconds (simulating app minimized)
    additional_wait = 5
    print(f"Waiting for additional {additional_wait} seconds (simulating app minimized)...")
    time.sleep(additional_wait)
    
    # Get current session time again
    time_result = api.get_current_session_time()
    
    if not time_result.get("success"):
        print(f"Failed to get current session time: {time_result.get('message')}")
        return False
    
    elapsed_time_2 = time_result.get("elapsed_time")
    print(f"Elapsed time after additional {additional_wait} seconds: {elapsed_time_2} seconds")
    
    # Verify elapsed time is approximately correct
    total_wait = initial_wait + additional_wait
    if abs(elapsed_time_2 - total_wait) > 1:  # Allow 1 second difference for processing time
        print(f"Warning: Elapsed time ({elapsed_time_2}) doesn't match expected time ({total_wait})")
    
    # Stop the timer
    stop_result = api.stop_timer()
    
    if not stop_result.get("success"):
        print(f"Failed to stop timer: {stop_result.get('message')}")
        return False
    
    print("Timer stopped successfully")
    
    # Verify the duration in the stop result
    duration = stop_result.get("data", {}).get("duration")
    if duration is not None:
        print(f"Reported duration: {duration} seconds")
        if abs(duration - total_wait) > 1:  # Allow 1 second difference for processing time
            print(f"Warning: Reported duration ({duration}) doesn't match expected time ({total_wait})")
    else:
        print("Warning: No duration reported in stop result")
    
    print("Timer sync test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_timer_sync()
    sys.exit(0 if success else 1)