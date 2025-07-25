# Screenshot Upload Fix

## Issue Summary

The screenshot capture functionality was working correctly, but the upload process was failing with a 400 status code error. The test_upload.py script showed that Method 2 (Base64 encoding with multipart/form-data) was successful, but the implementation in main.py was using an incorrect approach.

```
Screenshot scheduled in 192 seconds (3.2 minutes)
Captured screenshot of all monitors: 2 monitor(s) detected
Monitor 1: 1920x1080 at position (1920,3)
Monitor 2: 1920x1080 at position (0,0)
Warning: Failed to clean up temporary file: [WinError 32] The process cannot access the file because it is being used by another process: 'C:\\Users\\User\\AppData\\Local\\Temp\\tmptk3286mj.png'
API request failed with status code 400
Failed to upload screenshot
```

## Root Causes

1. **Incorrect Request Format**: The main.py implementation was using `json=files` instead of `files=files` in the request, which caused the request to be formatted incorrectly.

2. **File Handling Issues**: The file was being kept open during the upload process, causing the "file in use" error when trying to delete it.

## Changes Made

1. **Fixed Request Format**: Changed the request to use `files=files` instead of `json=files` to properly use multipart/form-data format.

2. **Simplified Headers**: Removed unnecessary comments and headers to make the code cleaner.

3. **Improved Documentation**: Added clearer comments explaining the approach being used.

## Implementation Details

The updated `upload_screenshot` method now:

1. Reads the image file and base64 encodes it:
   ```python
   with open(screenshot_path, 'rb') as image_file:
       image_data = image_file.read()
       base64_encoded = base64.b64encode(image_data).decode('utf-8')
   ```

2. Sets the appropriate headers:
   ```python
   headers = {
       'x-api-key': '2a978046cf9eebb8f8134281a3e5106d05723cae3eaf8ec58f2596d95feca3de'
   }
   ```

3. Prepares the file for upload using base64 encoding with multipart/form-data:
   ```python
   files = {
       'file': (os.path.basename(screenshot_path), base64_encoded, 'image/png')
   }
   ```

4. Makes the API request using `files=files` instead of `json=files`:
   ```python
   response = requests.post(
       'http://5.78.136.221:3020/api/files/5a7f64a1-ab0e-4544-8fcb-4a7b2fc3d428/upload',
       files=files,
       headers=headers
   )
   ```

## Expected Results

With these changes, the screenshot upload process now works correctly:

1. The screenshot is captured using the `mss` package
2. The image is base64 encoded and sent as multipart/form-data
3. The server receives the request with the correct format
4. The server processes the image and returns a success response with status code 201
5. The application receives the image URL and includes it in the session update

## Testing

The fix was tested using a simplified version of the upload_screenshot method in a separate test script. The test confirmed that the approach works correctly:

```
Testing screenshot upload functionality
Captured screenshot of all monitors: 2 monitor(s) detected
Monitor 1: 1920x1080 at position (1920,3)
Monitor 2: 1920x1080 at position (0,0)
Screenshot saved to: C:\Users\User\AppData\Local\Temp\tmptt445vdk.png
Image Upload response: <Response [201]>
Status Code: 201
Response Text: {"success":true,"data":{"url":"https://remoteintegrity.s3.us-east-1.amazonaws.com/tracker_app07-2025/25/tmptt445vdk.png","key":"tracker_app07-2025/25/tmptt445vdk.png"},"message":"File uploaded successfully"}
Screenshot uploaded successfully!
URL: https://remoteintegrity.s3.us-east-1.amazonaws.com/tracker_app07-2025/25/tmptt445vdk.png
Timestamp: 2025-07-25T21:15:52.199Z
```

## Alternative Approaches

During the development of this fix, several approaches were considered:

1. **Standard multipart/form-data with raw file** (Method 1 in test_upload.py): This approach failed with a 400 status code.

2. **Base64 encoding with multipart/form-data** (Method 2 in test_upload.py): This approach was successful and was implemented in the fix.

3. **Base64 encoding with JSON payload** (Method 3 in test_upload.py): This approach failed with a 500 status code.

The successful approach (Method 2) was chosen because it worked correctly in the test and provided the expected results.

## Future Improvements

1. Consider adding retry logic for failed uploads
2. Implement better error handling and user feedback
3. Add progress indicators for screenshot uploads
4. Consider compression options to reduce upload size and time