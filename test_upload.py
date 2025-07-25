import requests
import base64
import os
import tempfile
import mss
import mss.tools

def take_screenshot():
    """Take a screenshot and save it to a temporary file"""
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
        
        return temp_filename
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None

def upload_screenshot_method1(screenshot_path):
    """Upload a screenshot using method 1: standard requests files parameter"""
    if not screenshot_path or not os.path.exists(screenshot_path):
        print("Screenshot path is invalid or file does not exist")
        return None
    
    try:
        # Prepare the file for upload
        files = {'file': open(screenshot_path, 'rb')}
        
        # Set headers with API key
        headers = {
            'x-api-key': '2a978046cf9eebb8f8134281a3e5106d05723cae3eaf8ec58f2596d95feca3de'
        }
        
        # Make the API request
        response = requests.post(
            'http://5.78.136.221:3020/api/files/5a7f64a1-ab0e-4544-8fcb-4a7b2fc3d428/upload',
            files=files,
            headers=headers
        )

        print(f"Method 1 - Response: {response}")
        print(f"Method 1 - Status Code: {response.status_code}")
        print(f"Method 1 - Response Text: {response.text}")
        
        # Clean up the file
        files['file'].close()  # Close the file before deleting
        try:
            os.unlink(screenshot_path)
        except Exception as cleanup_error:
            print(f"Warning: Failed to clean up temporary file: {cleanup_error}")
        
        return response
    except Exception as e:
        print(f"Error uploading screenshot (Method 1): {e}")
        return None

def upload_screenshot_method2(screenshot_path):
    """Upload a screenshot using method 2: base64 encoding with multipart/form-data"""
    if not screenshot_path or not os.path.exists(screenshot_path):
        print("Screenshot path is invalid or file does not exist")
        return None
    
    try:
        # Read the image file and encode it as base64
        with open(screenshot_path, 'rb') as image_file:
            # Prepare the file for upload using base64 encoding
            files = {
                'file': (os.path.basename(screenshot_path), image_file, 'image/png')
            }
            # image_data = image_file.read()
            # base64_encoded = base64.b64encode(image_data).decode('utf-8')


        
            # Set headers with API key and Content-Type
            headers = {
                'x-api-key': '2a978046cf9eebb8f8134281a3e5106d05723cae3eaf8ec58f2596d95feca3de',
                # 'Content-Type': 'multipart/form-data'
            }
        

        
            # Make the API request
            response = requests.post(
                'http://5.78.136.221:3020/api/files/5a7f64a1-ab0e-4544-8fcb-4a7b2fc3d428/upload',
                files=files,
                headers=headers
            )

        print(f"Method 2 - Response: {response}")
        print(f"Method 2 - Status Code: {response.status_code}")
        print(f"Method 2 - Response Text: {response.text}")
        
        # Clean up the file
        try:
            os.unlink(screenshot_path)
        except Exception as cleanup_error:
            print(f"Warning: Failed to clean up temporary file: {cleanup_error}")
        
        return response
    except Exception as e:
        print(f"Error uploading screenshot (Method 2): {e}")
        return None

def upload_screenshot_method3(screenshot_path):
    """Upload a screenshot using method 3: base64 encoding with JSON payload"""
    if not screenshot_path or not os.path.exists(screenshot_path):
        print("Screenshot path is invalid or file does not exist")
        return None
    
    try:
        # Read the image file and encode it as base64
        with open(screenshot_path, 'rb') as image_file:
            image_data = image_file.read()
            base64_encoded = base64.b64encode(image_data).decode('utf-8')
        
        # Set headers with API key and Content-Type for JSON
        headers = {
            'x-api-key': '2a978046cf9eebb8f8134281a3e5106d05723cae3eaf8ec58f2596d95feca3de',
            'Content-Type': 'application/json'
        }
        
        # Prepare the JSON payload with base64 encoded image
        payload = {
            'file': base64_encoded,
            'filename': os.path.basename(screenshot_path)
        }
        
        # Make the API request
        response = requests.post(
            'http://5.78.136.221:3020/api/files/5a7f64a1-ab0e-4544-8fcb-4a7b2fc3d428/upload',
            json=payload,
            headers=headers
        )

        print(f"Method 3 - Response: {response}")
        print(f"Method 3 - Status Code: {response.status_code}")
        print(f"Method 3 - Response Text: {response.text}")
        
        # Clean up the file
        try:
            os.unlink(screenshot_path)
        except Exception as cleanup_error:
            print(f"Warning: Failed to clean up temporary file: {cleanup_error}")
        
        return response
    except Exception as e:
        print(f"Error uploading screenshot (Method 3): {e}")
        return None

if __name__ == "__main__":
    # Take a screenshot
    screenshot_path = take_screenshot()
    
    if screenshot_path:
        print(f"Screenshot saved to: {screenshot_path}")
        
        # Make a copy of the screenshot for each method
        import shutil
        method1_path = screenshot_path + ".method1.png"
        method2_path = screenshot_path + ".method2.png"
        method3_path = screenshot_path + ".method3.png"
        
        shutil.copy(screenshot_path, method1_path)
        shutil.copy(screenshot_path, method2_path)
        shutil.copy(screenshot_path, method3_path)
        
        # Test each method
        print("\n=== Testing Method 1: Standard requests files parameter ===")
        upload_screenshot_method1(method1_path)
        
        print("\n=== Testing Method 2: Base64 encoding with multipart/form-data ===")
        upload_screenshot_method2(method2_path)
        
        print("\n=== Testing Method 3: Base64 encoding with JSON payload ===")
        upload_screenshot_method3(method3_path)
        
        # Clean up the original screenshot
        try:
            os.unlink(screenshot_path)
        except Exception as e:
            print(f"Warning: Failed to clean up original screenshot: {e}")
    else:
        print("Failed to take screenshot")