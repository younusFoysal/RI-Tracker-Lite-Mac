import time
import sys
import os
import json
import psutil

# Add the backend directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the Api class from main.py
from main import Api

def get_all_processes():
    """Get a list of all running processes"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            proc_info = proc.info
            if proc_info['exe']:
                processes.append({
                    'name': os.path.basename(proc_info['exe']),
                    'exe': proc_info['exe']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes

def test_application_tracking():
    """Test the application tracking feature"""
    print("Starting application tracking test...")
    
    # Get all processes before filtering
    print("\nGetting all processes before filtering...")
    all_processes = get_all_processes()
    print(f"Total processes with executable paths: {len(all_processes)}")
    
    # Count system processes
    system_processes = [p for p in all_processes if '\\Windows\\' in p['exe'] or '\\Program Files\\Common Files\\' in p['exe'] or '\\ProgramData\\' in p['exe']]
    print(f"System processes (based on path): {len(system_processes)} ({len(system_processes)/len(all_processes)*100:.1f}%)")
    
    # Print sample of system processes
    print("\nSample of system processes (first 5):")
    for i, proc in enumerate(system_processes[:5]):
        print(f"  - {proc['name']} ({proc['exe']})")
    
    # Print sample of non-system processes
    non_system = [p for p in all_processes if p not in system_processes]
    print("\nSample of non-system processes (first 5):")
    for i, proc in enumerate(non_system[:5]):
        print(f"  - {proc['name']} ({proc['exe']})")
    
    # Create an instance of the Api class
    api = Api()
    
    # Start the timer
    print("\nStarting timer...")
    result = api.start_timer("Test Project")
    
    if not result.get("success"):
        print(f"Failed to start timer: {result.get('message')}")
        return
    
    print("Timer started successfully.")
    print("Waiting for 20 seconds to collect application data...")
    
    # Wait for 20 seconds to collect application data
    time.sleep(20)
    
    # Get the current application usage data
    applications_data = api.prepare_applications_for_session()
    
    # Get the raw applications usage data
    raw_applications = api.applications_usage
    
    print(f"\nCollected data for {len(applications_data)} applications after filtering:")
    
    # Check if any system processes are still being tracked
    system_apps_tracked = []
    user_apps_tracked = []
    
    for app in applications_data:
        app_name = app['name']
        app_time = app['timeSpent']
        app_exe = raw_applications.get(app_name, {}).get('exe', 'Unknown')
        
        # Check if this is a system process
        is_system = False
        if '\\Windows\\' in app_exe or '\\Program Files\\Common Files\\' in app_exe or '\\ProgramData\\' in app_exe:
            is_system = True
            system_apps_tracked.append((app_name, app_exe))
        else:
            user_apps_tracked.append((app_name, app_exe))
    
    # Print user applications being tracked
    print("\nUser applications being tracked (sample of 5):")
    for app_name, app_exe in user_apps_tracked[:5]:
        print(f"  - {app_name}")
        print(f"    Path: {app_exe}")
    
    # Print system applications being tracked (if any)
    if system_apps_tracked:
        print("\nWARNING: Some system processes are still being tracked:")
        for app_name, app_exe in system_apps_tracked[:5]:
            print(f"  - {app_name}")
            print(f"    Path: {app_exe}")
    else:
        print("\nNo system processes are being tracked. Filtering is working correctly!")
    
    # Calculate filtering effectiveness
    filtering_percentage = ((len(all_processes) - len(applications_data)) / len(all_processes)) * 100 if len(all_processes) > 0 else 0
    print(f"\nFiltering effectiveness: {filtering_percentage:.1f}% of processes filtered out")
    
    # Stop the timer
    print("\nStopping timer...")
    result = api.stop_timer()
    
    if not result.get("success"):
        print(f"Failed to stop timer: {result.get('message')}")
        return
    
    print("Timer stopped successfully.")
    print("Application tracking test completed.")

if __name__ == "__main__":
    test_application_tracking()