import os
import tempfile
import mss
import mss.tools
import requests
import base64
from datetime import datetime, timezone

def upload_screenshot(screenshot_path):
    """Upload a screenshot to the API and return the URL
    
    This is a simplified version of the upload_screenshot method from main.py
    for testing purposes.
    
    Args:
        screenshot_path (str): Path to the screenshot file to upload
        
    Returns:
        dict: Dictionary containing the URL and timestamp of the uploaded screenshot,
              or None if the upload failed
    """
    if not screenshot_path or not os.path.exists(screenshot_path):
        print("Screenshot path is invalid or file does not exist")
        return None
    
    try:
        # Read the image file and encode it as base64
        with open(screenshot_path, 'rb') as image_file:
            image_data = image_file.read()
            base64_encoded = base64.b64encode(image_data).decode('utf-8')
        
        # Set headers with API key
        headers = {
            'x-api-key': '2a978046cf9eebb8f8134281a3e5106d05723cae3eaf8ec58f2596d95feca3de'
        }
        
        # Prepare the file for upload using base64 encoding with multipart/form-data
        # This is Method 2 from test_upload.py which was successful (201 status code)
        files = {
            'file': (os.path.basename(screenshot_path), base64_encoded, 'image/png')
        }
        
        # Make the API request to the correct endpoint
        # Using files=files for multipart/form-data instead of json=files
        response = requests.post(
            'http://5.78.136.221:3020/api/files/5a7f64a1-ab0e-4544-8fcb-4a7b2fc3d428/upload',
            files=files,
            headers=headers
        )

        print(f"Image Upload response: {response}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        # Clean up the temporary file regardless of upload success
        try:
            os.unlink(screenshot_path)
        except Exception as cleanup_error:
            print(f"Warning: Failed to clean up temporary file: {cleanup_error}")
        
        # Process the response
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('success'):
                timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                return {
                    'url': data['data']['url'],
                    'timestamp': timestamp
                }
            else:
                print(f"API returned success=false: {data.get('message', 'No error message')}")
        else:
            print(f"API request failed with status code {response.status_code}")
        
        return None
    except Exception as e:
        print(f"Error uploading screenshot: {e}")
        return None

def test_screenshot_upload():
    """Test the screenshot upload functionality"""
    print("Testing screenshot upload functionality")
    
    # Take a screenshot using mss
    try:
        # Create a temporary file to save the screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        # Use mss to capture screenshots of all monitors
        with mss.mss() as sct:
            # Capture all monitors (monitor 0 is all monitors combined)
            screenshot = sct.grab(sct.monitors[0])
            
            # Save the screenshot to the temporary file
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=temp_filename)
            
            # Log monitor information for debugging
            print(f"Captured screenshot of all monitors: {len(sct.monitors)-1} monitor(s) detected")
            for i, monitor in enumerate(sct.monitors[1:], 1):
                print(f"Monitor {i}: {monitor['width']}x{monitor['height']} at position ({monitor['left']},{monitor['top']})")
        
        print(f"Screenshot saved to: {temp_filename}")
        
        # Upload the screenshot using our simplified function
        result = upload_screenshot(temp_filename)
        
        if result:
            print(f"Screenshot uploaded successfully!")
            print(f"URL: {result['url']}")
            print(f"Timestamp: {result['timestamp']}")
        else:
            print("Failed to upload screenshot")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    # Run the test
    test_screenshot_upload()