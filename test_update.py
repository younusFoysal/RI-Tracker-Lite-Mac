import os
import sys
import requests
import json
import time

# Add the backend directory to the path so we can import from it
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_dir)

# Import the Api class from main.py
from backend.main import Api, APP_VERSION, GITHUB_REPO

def test_version_comparison():
    """Test the version comparison function"""
    api = Api()
    
    # Test cases
    test_cases = [
        ("1.0.0", "1.0.1", True),  # Newer patch version
        ("1.0.1", "1.1.0", True),  # Newer minor version
        ("1.1.0", "2.0.0", True),  # Newer major version
        ("1.0.0", "1.0.0", False), # Same version
        ("1.0.1", "1.0.0", False), # Older version
        ("1.2.3", "1.2.3.4", True), # More segments
        ("1.2.3.4", "1.2.3", False) # Fewer segments
    ]
    
    for v1, v2, expected in test_cases:
        result = api.compare_versions(v1, v2)
        print(f"Comparing {v1} to {v2}: {'✓' if result == expected else '✗'} (got {result}, expected {expected})")

def test_check_for_updates():
    """Test the check_for_updates function"""
    api = Api()
    
    print(f"\nChecking for updates (current version: {APP_VERSION})...")
    result = api.check_for_updates()
    
    print(f"Success: {result.get('success', False)}")
    if result.get('success'):
        print(f"Current version: {result.get('current_version')}")
        print(f"Latest version: {result.get('latest_version')}")
        print(f"Update available: {result.get('update_available')}")
        if result.get('update_available'):
            print(f"Download URL: {result.get('download_url')}")
    else:
        print(f"Error: {result.get('message')}")

def test_download_update(download_url):
    """Test the download_update function"""
    if not download_url:
        print("\nNo download URL provided, skipping download test")
        return None
        
    api = Api()
    
    print(f"\nDownloading update from {download_url}...")
    result = api.download_update(download_url)
    
    print(f"Success: {result.get('success', False)}")
    if result.get('success'):
        print(f"Downloaded to: {result.get('file_path')}")
        return result.get('file_path')
    else:
        print(f"Error: {result.get('message')}")
        return None

def test_install_update(file_path):
    """Test the install_update function"""
    if not file_path:
        print("\nNo file path provided, skipping installation test")
        return
        
    api = Api()
    
    print(f"\nInstalling update from {file_path}...")
    # Note: This will actually try to install the update and restart the app
    # So we'll just print what would happen
    print(f"Would call api.install_update({file_path})")
    print("This would install the update and restart the app")
    print("Test completed without actually installing")

def main():
    """Run all tests"""
    print("=== Testing Update Functionality ===\n")
    
    # Test version comparison
    print("Testing version comparison...")
    test_version_comparison()
    
    # Test check for updates
    test_check_for_updates()
    
    # Ask if we should continue with download test
    download_url = input("\nEnter download URL to test download (or press Enter to skip): ").strip()
    if download_url:
        file_path = test_download_update(download_url)
        
        # Ask if we should continue with install test
        if file_path and os.path.exists(file_path):
            install = input("\nDo you want to test installation? (y/N): ").strip().lower()
            if install == 'y':
                test_install_update(file_path)
    
    print("\n=== Test Completed ===")

if __name__ == "__main__":
    main()