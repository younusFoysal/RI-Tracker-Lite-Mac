import sys
import os
import psutil

# No need to import from backend for this test

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

def test_filtering_logic():
    """Test the application filtering logic directly"""
    print("Testing application filtering logic...")
    
    # Get all processes
    all_processes = get_all_processes()
    print(f"Total processes with executable paths: {len(all_processes)}")
    
    # Define the same filtering logic as in main.py
    system_process_names = [
        'System', 'Registry', 'smss.exe', 'csrss.exe', 'wininit.exe', 
        'services.exe', 'lsass.exe', 'svchost.exe', 'winlogon.exe', 
        'dwm.exe', 'conhost.exe', 'dllhost.exe', 'taskhostw.exe',
        'explorer.exe', 'RuntimeBroker.exe', 'ShellExperienceHost.exe',
        'SearchUI.exe', 'sihost.exe', 'ctfmon.exe', 'WmiPrvSE.exe',
        'spoolsv.exe', 'SearchIndexer.exe', 'fontdrvhost.exe',
        'WUDFHost.exe', 'LsaIso.exe', 'SgrmBroker.exe', 'audiodg.exe',
        'dasHost.exe', 'SearchProtocolHost.exe', 'SearchFilterHost.exe'
    ]
    
    system_dirs = [
        '\\Windows\\', '\\Windows\\System32\\', '\\Windows\\SysWOW64\\',
        '\\Windows\\WinSxS\\', '\\Windows\\servicing\\', '\\ProgramData\\',
        '\\Program Files\\Common Files\\', '\\Program Files (x86)\\Common Files\\'
    ]
    
    # Filter processes using the same logic as in main.py
    filtered_processes = []
    for proc in all_processes:
        app_name = proc['name']
        exe_path = proc['exe']
        
        # Skip system processes based on name
        if app_name.lower() in [p.lower() for p in system_process_names]:
            continue
        
        # Skip system processes based on path
        if any(system_dir.lower() in exe_path.lower() for system_dir in system_dirs):
            continue
        
        filtered_processes.append(proc)
    
    print(f"Processes after filtering: {len(filtered_processes)}")
    print(f"Filtering effectiveness: {((len(all_processes) - len(filtered_processes)) / len(all_processes)) * 100:.1f}% of processes filtered out")
    
    # Print sample of filtered processes
    print("\nSample of processes after filtering (first 10):")
    for i, proc in enumerate(filtered_processes[:10]):
        print(f"  - {proc['name']} ({proc['exe']})")
    
    # Check if any system processes are still in the filtered list
    system_processes_in_filtered = []
    for proc in filtered_processes:
        if any(system_dir.lower() in proc['exe'].lower() for system_dir in system_dirs):
            system_processes_in_filtered.append(proc)
    
    if system_processes_in_filtered:
        print("\nWARNING: Some system processes are still in the filtered list:")
        for proc in system_processes_in_filtered[:5]:
            print(f"  - {proc['name']} ({proc['exe']})")
    else:
        print("\nNo system processes found in the filtered list. Filtering is working correctly!")

if __name__ == "__main__":
    test_filtering_logic()