import time
import threading
from backend.main import Api

def simulate_activity(api, activity_type, count, interval):
    """Simulate user activity by calling record_activity method"""
    print(f"Simulating {count} {activity_type} events with {interval}s interval")
    for i in range(count):
        if activity_type == 'keyboard':
            api.record_keyboard_activity()
        else:
            api.record_mouse_activity()
        time.sleep(interval)

def test_activity_tracking():
    """Test the activity tracking mechanism"""
    api = Api()
    
    # Start timer
    print("Starting timer...")
    api.start_timer("Test Project")
    
    # Initial stats
    print("\nInitial stats:")
    print(api.get_activity_stats())
    
    # Simulate keyboard activity
    simulate_activity(api, 'keyboard', 5, 0.2)
    
    # Check stats after keyboard activity
    print("\nStats after keyboard activity:")
    print(api.get_activity_stats())
    
    # Simulate mouse activity
    simulate_activity(api, 'mouse', 5, 0.2)
    
    # Check stats after mouse activity
    print("\nStats after mouse activity:")
    print(api.get_activity_stats())
    
    # Simulate idle period (longer than idle threshold)
    idle_time = api.idle_threshold + 5
    print(f"\nSimulating idle period of {idle_time}s...")
    time.sleep(idle_time)
    
    # Force an activity check
    api.check_idle_status()
    
    # Check stats after idle period
    print("\nStats after idle period:")
    print(api.get_activity_stats())
    
    # Simulate more activity after idle
    simulate_activity(api, 'keyboard', 3, 0.2)
    
    # Check stats after more activity
    print("\nStats after more activity:")
    print(api.get_activity_stats())
    
    # Stop timer
    print("\nStopping timer...")
    result = api.stop_timer()
    
    # Final stats from result
    print("\nFinal stats from result:")
    print(f"Active time: {result.get('data', {}).get('activeTime')}s")
    print(f"Idle time: {result.get('data', {}).get('idleTime')}s")
    print(f"Keyboard activity rate: {result.get('data', {}).get('keyboardActivityRate')}")
    print(f"Mouse activity rate: {result.get('data', {}).get('mouseActivityRate')}")
    
    # Verify total time
    total_time = result.get('data', {}).get('activeTime', 0) + result.get('data', {}).get('idleTime', 0)
    expected_time = int(time.time() - api.start_time) if api.start_time else 0
    print(f"\nTotal time (active + idle): {total_time}s")
    print(f"Expected total time: {expected_time}s")
    print(f"Difference: {abs(total_time - expected_time)}s")

if __name__ == "__main__":
    # Disable actual API calls
    Api.create_session = lambda self: {"success": True, "data": {"_id": "test_session"}}
    Api.update_session = lambda self, active_time, idle_time, keyboard_rate, mouse_rate: {
        "success": True, 
        "data": {
            "activeTime": active_time,
            "idleTime": idle_time,
            "keyboardActivityRate": keyboard_rate,
            "mouseActivityRate": mouse_rate
        }
    }
    
    test_activity_tracking()