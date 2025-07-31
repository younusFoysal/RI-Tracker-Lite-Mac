import os
import sys
import json

# This script tests the encoding fix by simulating the print operations
# that were causing the 'charmap' codec error

def main():
    print("Testing encoding fix for 'charmap' codec error")
    print("=============================================")
    
    # Test printing non-ASCII characters
    print("\nSimulating print operations with special characters...")
    
    # Create test data with non-ASCII characters
    test_data = {
        "links": [
            {
                "url": "https://example.com/test",
                "title": "Test page with special characters: áéíóúñ",
                "timeSpent": 60,
                "timestamp": "2025-07-30T22:10:00.000Z"
            },
            {
                "url": "https://example.com/test2",
                "title": "Another test with emoji: 😀🔥💻",
                "timeSpent": 120,
                "timestamp": "2025-07-30T22:15:00.000Z"
            }
        ],
        "applications": [
            {
                "name": "Application with special chars: 你好",
                "timeSpent": 300,
                "timestamp": "2025-07-30T22:20:00.000Z"
            }
        ]
    }
    
    # Test 1: Original problematic print (would cause error)
    print("\nTest 1: Original problematic print (might cause error):")
    try:
        print(f"Update Session: {test_data}")
        print("✓ Success - No encoding error")
    except UnicodeEncodeError as e:
        print(f"✗ Error - UnicodeEncodeError: {e}")
    except Exception as e:
        print(f"✗ Error - Other exception: {e}")
    
    # Test 2: Our fixed approach
    print("\nTest 2: Our fixed approach:")
    try:
        # Use safe printing to handle non-ASCII characters
        print("Update Session data prepared (details omitted for encoding safety)")
        print("✓ Success - No encoding error")
    except Exception as e:
        print(f"✗ Error - Exception: {e}")
    
    # Test 3: Alternative approach using json.dumps with ensure_ascii=True
    print("\nTest 3: Alternative approach using json.dumps with ensure_ascii=True:")
    try:
        safe_json = json.dumps(test_data, ensure_ascii=True)
        print(f"Update Session: {safe_json}")
        print("✓ Success - No encoding error")
    except Exception as e:
        print(f"✗ Error - Exception: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()