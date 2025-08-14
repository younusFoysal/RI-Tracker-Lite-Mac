import os
import webview
import sqlite3
import time
import sys
import requests
import json
import threading
import subprocess
import platform
import shutil
import random
import tempfile
import base64
import mss
import mss.tools
import psutil
import glob
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from config import URLS
import screeninfo


from tzlocal import get_localzone

local_tz = str(get_localzone())

# Import pynput for system-wide keyboard and mouse tracking
try:
    from pynput import keyboard, mouse
    PYNPUT_AVAILABLE = True
except ImportError:
    print("pynput library not available. System-wide activity tracking will be disabled.")
    PYNPUT_AVAILABLE = False


APP_NAME = "RI_Tracker"
APP_VERSION = "1.0.15"  # Current version of the application
# GITHUB_REPO = "younusFoysal/RI-Tracker-Lite"
GITHUB_REPO = "RemoteIntegrity/RI-Tracker-Lite-Releases"
DATA_DIR = os.path.join(os.getenv('LOCALAPPDATA') or os.path.expanduser("~/.config"), APP_NAME)

# Ensure the directory exists
os.makedirs(DATA_DIR, exist_ok=True)



# Save db in local app data
db_file = os.path.join(DATA_DIR, 'tracker.db')
#db_file = 'tracker.db'

def init_db():
    with sqlite3.connect(db_file) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT,
                timestamp TEXT,
                duration INTEGER
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS auth_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT,
                user_data TEXT
            )
        ''')

class Api:
    def __init__(self):
        self.start_time = None
        self.current_project = None
        self.auth_token = None
        self.user_data = None
        self.session_id = None
        self.active_time = 0
        self.idle_time = 0
        self.keyboard_activity_rate = 0
        self.mouse_activity_rate = 0
        self.user_note = "I am working on Task"
        
        # Window reference for UI interactions
        self.window = None
        
        # Activity tracking variables
        self.last_activity_time = None
        self.is_idle = False
        self.idle_threshold = 60  # seconds of inactivity before considered idle
        self.keyboard_events = 0
        self.mouse_events = 0
        self.activity_timer = None
        self.activity_check_interval = 1  # seconds between activity checks
        self.last_active_check_time = None
        
        # System-wide activity tracking variables (pynput)
        self.keyboard_listener = None
        self.mouse_listener = None
        self.system_tracking_enabled = PYNPUT_AVAILABLE
        
        # Stats update variables
        self.stats_timer = None
        self.stats_update_interval = 600  # 10 minutes in seconds
        
        # Session update variables
        self.session_update_timer = None
        self.session_update_interval = 600  # 10 minutes in seconds
        
        # Throttling variables to prevent excessive event counting
        self.last_keyboard_event_time = 0
        self.last_mouse_event_time = 0
        self.event_throttle_interval = 0.5  # seconds between counting events
        
        # Screenshot variables
        self.screenshot_timer = None
        self.screenshot_min_interval = 60  # 1 minute in seconds
        self.screenshot_max_interval = 480  # 8 minutes in seconds
        self.current_screenshot = None
        self.screenshot_timestamp = None
        self.screenshots_for_session = []
        
        # Application tracking variables
        self.applications_usage = {}  # Dictionary to store application usage: {app_name: {timeSpent: seconds, lastSeen: timestamp}}
        self.last_app_check_time = None
        self.app_check_interval = 5  # seconds between application checks
        self.app_timer = None
        self.applications_for_session = []  # List to store applications for the current session update
        
        # Browser link tracking variables
        self.links_usage = {}  # Dictionary to store link usage: {url: {title: string, timeSpent: seconds, lastSeen: timestamp}}
        self.last_link_check_time = None
        self.link_check_interval = 30  # seconds between link checks
        self.link_timer = None
        self.links_for_session = []  # List to store links for the current session update
        self.supported_browsers = ['chrome', 'brave', 'edge', 'firefox', 'safari']
        
        self.load_auth_data()

    def load_auth_data(self):
        """Load authentication data from the database"""
        try:
            with sqlite3.connect(db_file) as conn:
                c = conn.cursor()
                c.execute('SELECT token, user_data FROM auth_data ORDER BY id DESC LIMIT 1')
                result = c.fetchone()
                if result:
                    self.auth_token = result[0]
                    self.user_data = json.loads(result[1])
                    return True
                return False
        except Exception as e:
            print(f"Error loading auth data: {e}")
            return False

    def save_auth_data(self, token, user_data):
        """Save authentication data to the database"""
        try:
            with sqlite3.connect(db_file) as conn:
                # Clear existing data
                conn.execute('DELETE FROM auth_data')
                # Save new data
                conn.execute(
                    'INSERT INTO auth_data (token, user_data) VALUES (?, ?)',
                    (token, json.dumps(user_data))
                )
            self.auth_token = token
            self.user_data = user_data
            return True
        except Exception as e:
            print(f"Error saving auth data: {e}")
            return False

    def clear_auth_data(self):
        """Clear authentication data from the database"""
        try:
            with sqlite3.connect(db_file) as conn:
                conn.execute('DELETE FROM auth_data')
            self.auth_token = None
            self.user_data = None
            return True
        except Exception as e:
            print(f"Error clearing auth data: {e}")
            return False

    def login(self, email, password, remember_me=False):
        """Login to the remote API and store the token if remember_me is True"""
        try:
            response = requests.post(
                URLS["LOGIN"],
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"}
            )
            data = response.json()
            
            if data.get('success'):
                # Store token and user data
                token = data['data']['token']
                user_data = data['data']['employee']
                
                # Only save auth data if remember_me is True
                if remember_me:
                    self.save_auth_data(token, user_data)
                else:
                    # If not remembering, just set in memory but don't save to database
                    self.auth_token = token
                    self.user_data = user_data
                window.evaluate_js('window.toastFromPython("Login successful!", "success")')
                return {"success": True, "data": data['data']}
            else:
                return {"success": False, "message": data.get('message', 'Login failed')}
        except Exception as e:
            print(f"Login error: {e}")
            return {"success": False, "message": f"An error occurred during login: {str(e)}"}

    def get_profile(self):
        """Get user profile data using the stored token"""
        if not self.auth_token:
            return {"success": False, "message": "Not authenticated"}
        
        try:
            # Get employee ID from stored user data
            employee_id = self.user_data.get('employeeId')
            if not employee_id:
                return {"success": False, "message": "Employee ID not found"}
                
            response = requests.get(
                f"{URLS['PROFILE']}/{employee_id}",
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            )
            data = response.json()
            
            if data.get('success'):
                return {"success": True, "data": data['data']}
            else:
                return {"success": False, "message": data.get('message', 'Failed to get profile')}
        except Exception as e:
            print(f"Profile error: {e}")
            return {"success": False, "message": f"An error occurred: {str(e)}"}

    def logout(self):
        """Logout and clear stored authentication data"""
        result = self.clear_auth_data()
        return {"success": result}

    def is_authenticated(self):
        """Check if user is authenticated"""
        return {"authenticated": self.auth_token is not None}

    def get_current_user(self):
        """Get current user data"""
        if self.user_data:
            return {"success": True, "user": self.user_data}
        return {"success": False, "message": "No user data available"}
        
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
        
    def test_long_error_message(self):
        """Test function to simulate a long error message"""
        # Simulate a long error message for testing the UI
        long_message = "Employee already has an active session. Please stop the current session before starting a new one. Active session ID: jhbasuydgfbyus6854657234jbhj"
        window.evaluate_js('window.toastFromPython("Test long error message", "error")')
        return {"success": False, "message": long_message}

    def create_session(self, user_note="I am working on Task"):
        """Create a new session via API
        
        Args:
            user_note: User's note about what they're working on
        """
        if not self.auth_token:
            window.evaluate_js('window.toastFromPython("Not authenticated. Please log in.", "error")')
            return {"success": False, "message": "Not authenticated"}
        
        try:
            # Get employee and company IDs
            employee_id = self.user_data.get('employeeId')
            company_id = None
            
            # Try to get company ID from user data first
            if self.user_data.get('companyId'):
                if isinstance(self.user_data['companyId'], dict):
                    company_id = self.user_data['companyId'].get('_id')
                else:
                    company_id = self.user_data['companyId']
            
            if not employee_id or not company_id:
                # If not found in user_data, try to get from profile
                profile = self.get_profile()
                if profile.get('success') and profile.get('data'):
                    if not employee_id:
                        employee_id = profile['data'].get('_id')
                    if not company_id and profile['data'].get('companyId'):
                        if isinstance(profile['data']['companyId'], dict):
                            company_id = profile['data']['companyId'].get('_id')
                        else:
                            company_id = profile['data']['companyId']
            
            if not employee_id or not company_id:
                window.evaluate_js('window.toastFromPython("Employee ID or Company ID not found. Please check your profile.", "error")')
                return {"success": False, "message": "Employee ID or Company ID not found"}


            # Step 1: get local time with tz info (e.g., Dhaka time if user machine is set to Dhaka timezone)
            local_time = datetime.now().astimezone()

            # Step 2: convert local time to UTC
            utc_time = local_time.astimezone(timezone.utc)

            # Step 3: format UTC time as ISO string for backend
            start_time = utc_time.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

            # Create session data
            #start_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

            session_data = {
                "employeeId": employee_id,
                "companyId": company_id,
                "startTime": start_time,
                "notes": "Session from RI Tracker Lite APP v1.",
                "userNote": user_note
                # "timezone": "America/New_York"
                #"timezone": "UTC"
            }
            
            # Send request to create session
            response = requests.post(
                URLS["SESSIONS"],
                json=session_data,
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            )
            
            data = response.json()
            
            if data.get('success'):
                self.session_id = data['data']['_id']
                return {"success": True, "data": data['data']}
            else:
                error_message = data.get('message', 'Failed to create session')
                # Check if the error message contains information about an active session
                if "active session" in error_message.lower():
                    # Format the message to be more readable
                    error_message = f"Employee already has an active session. Please stop the current session before starting a new one. Active session ID: {error_message.split('ID:')[-1].strip() if 'ID:' in error_message else 'Unknown'}"
                
                window.evaluate_js('window.toastFromPython("Failed to create session!", "error")')
                return {"success": False, "message": error_message}
        except Exception as e:
            print(f"Create session error: {e}")
            window.evaluate_js('window.toastFromPython("Failed to create session!", "error")')
            return {"success": False, "message": f"An error occurred: {str(e)}"}
    
    def update_session(self, active_time, idle_time=0, keyboard_rate=0, mouse_rate=0, is_final_update=False, user_note="I am working on Task"):
        """Update an existing session via API
        
        Args:
            active_time: Time spent actively working (in seconds)
            idle_time: Time spent idle (in seconds)
            keyboard_rate: Keyboard activity rate (events per minute)
            mouse_rate: Mouse activity rate (events per minute)
            is_final_update: Whether this is the final update (when timer is stopped)
            user_note: User's note about what they're working on
        """
        if not self.auth_token or not self.session_id:
            return {"success": False, "message": "Not authenticated or no active session"}
        
        try:
            # Step 1: get local time with tz info (e.g., Dhaka time if user machine is set to Dhaka timezone)
            local_time = datetime.now().astimezone()

            # Step 2: convert local time to UTC
            utc_time = local_time.astimezone(timezone.utc)

            # Step 3: format UTC time as ISO string for backend
            end_time = utc_time.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

            # Create session update data
            # end_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

            # Prepare screenshots data
            screenshots_data = self.screenshots_for_session.copy()
            
            # If no screenshots were captured during this interval, add a fallback
            if not screenshots_data and not is_final_update:
                # Try to take a screenshot now
                screenshot_path = self.take_screenshot()
                if screenshot_path:
                    screenshot_data = self.upload_screenshot(screenshot_path)
                    if screenshot_data:
                        screenshots_data.append({
                            'timestamp': screenshot_data['timestamp'],
                            'imageUrl': screenshot_data['url']
                        })
            
            # Get application usage data
            applications_data = self.prepare_applications_for_session()
            
            # Get link usage data
            links_data = self.prepare_links_for_session()
            
            update_data = {
                "activeTime": active_time,
                "idleTime": idle_time,
                "keyboardActivityRate": keyboard_rate,
                "mouseActivityRate": mouse_rate,
                "screenshots": screenshots_data,
                "applications": applications_data,
                "links": links_data,
                "notes": "Session from RI Tracker Lite APP v1.",
                "userNote": user_note
                # "timezone": "UTC"
            }
            
            # Only include endTime when this is the final update (timer is stopped)
            if is_final_update:
                update_data["endTime"] = end_time
            # Use safe printing to handle non-ASCII characters
            try:
                print("Update Session data prepared (details omitted for encoding safety)")
            except Exception as e:
                print(f"Print error: {str(e)}")
            
            # Send request to update session with timeout
            # Use a 30-second timeout to prevent hanging for long-running sessions
            response = requests.patch(
                f'{URLS["SESSIONS"]}/{self.session_id}',
                json=update_data,
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                # timeout=30  # 30 second timeout
            )
            
            data = response.json()
            
            if data.get('success'):
                # Only reset session_id if this is the final update
                if is_final_update:
                    self.session_id = None
                return {"success": True, "data": data['data']}
            else:
                return {"success": False, "message": data.get('message', 'Failed to update session')}
        # except requests.exceptions.Timeout:
        #     print("Update session timeout: Request timed out after 30 seconds")
        #     # For final updates, we should still consider the timer stopped locally
        #     if is_final_update:
        #         self.session_id = None
        #     return {"success": False, "message": "Request timed out. The server took too long to respond."}
        # except requests.exceptions.ConnectionError:
        #     print("Update session connection error: Failed to connect to the server")
        #     # For final updates, we should still consider the timer stopped locally
        #     if is_final_update:
        #         self.session_id = None
        #     return {"success": False, "message": "Connection error. Failed to connect to the server."}
        # except requests.exceptions.RequestException as e:
        #     print(f"Update session request error: {e}")
        #     # For final updates, we should still consider the timer stopped locally
        #     if is_final_update:
        #         self.session_id = None
        #     return {"success": False, "message": f"Request error: {str(e)}"}
        except Exception as e:
            print(f"Update session error: {e}")
            # For final updates, we should still consider the timer stopped locally
            # if is_final_update:
            #     self.session_id = None
            return {"success": False, "message": f"An error occurred: {str(e)}"}
    
    def start_stats_updates(self):
        """Start periodic stats updates"""
        if self.stats_timer:
            return
            
        def update_stats():
            if not self.start_time:
                return
                
            # Get updated stats
            self.get_daily_stats()
            self.get_weekly_stats()
            
            # Schedule the next update if timer is still running
            if self.start_time:
                self.stats_timer = threading.Timer(self.stats_update_interval, update_stats)
                self.stats_timer.daemon = True
                self.stats_timer.start()
        
        # Start the stats update timer
        self.stats_timer = threading.Timer(self.stats_update_interval, update_stats)
        self.stats_timer.daemon = True
        self.stats_timer.start()
        
        # Get initial stats
        daily_stats = self.get_daily_stats()
        weekly_stats = self.get_weekly_stats()
        return {"daily": daily_stats, "weekly": weekly_stats}
    
    def stop_stats_updates(self):
        """Stop periodic stats updates"""
        if self.stats_timer:
            self.stats_timer.cancel()
            self.stats_timer = None
            
    def start_session_updates(self):
        """Start periodic session updates"""
        if self.session_update_timer:
            return
            
        def update_session_periodically():
            if not self.start_time:
                return
                
            # Update activity metrics
            self.update_activity_metrics()
            
            # Get current activity stats
            current_time = time.time()
            
            # Perform final activity check
            if self.last_active_check_time is not None:
                if self.is_idle:
                    # Add idle time
                    idle_time = current_time - self.last_active_check_time
                    self.idle_time += idle_time
                    self.last_active_check_time = current_time
                else:
                    # Add active time
                    active_time = current_time - self.last_active_check_time
                    self.active_time += active_time
                    self.last_active_check_time = current_time
            
            # Update the session with current metrics (not final update)
            result = self.update_session(
                active_time=int(self.active_time),
                idle_time=int(self.idle_time),
                keyboard_rate=self.keyboard_activity_rate,
                mouse_rate=self.mouse_activity_rate,
                is_final_update=False,
                user_note=self.user_note if hasattr(self, 'user_note') else "I am working on Task"
            )
            
            # Clear the screenshots array for the next interval
            self.screenshots_for_session = []
            
            # Clear the applications usage data for the next interval
            self.applications_usage = {}
            
            # Clear the links usage data for the next interval
            self.links_usage = {}
            
            # Schedule a new screenshot for the next interval
            self.schedule_screenshot()
            
            # Schedule the next update if timer is still running
            if self.start_time:
                self.session_update_timer = threading.Timer(self.session_update_interval, update_session_periodically)
                self.session_update_timer.daemon = True
                self.session_update_timer.start()
        
        # Start the session update timer
        self.session_update_timer = threading.Timer(self.session_update_interval, update_session_periodically)
        self.session_update_timer.daemon = True
        self.session_update_timer.start()
        
        # Schedule the first screenshot
        self.schedule_screenshot()
        
    def stop_session_updates(self):
        """Stop periodic session updates"""
        if self.session_update_timer:
            self.session_update_timer.cancel()
            self.session_update_timer = None
        
        # Also stop any pending screenshot timer
        if self.screenshot_timer:
            self.screenshot_timer.cancel()
            self.screenshot_timer = None
    
    def take_screenshot(self):
        """Take a screenshot of all monitors
        
        This method captures a screenshot of all monitors and saves it to a temporary file.
        It uses the mss package for cross-platform compatibility and multi-monitor support.
        
        Returns:
            str: Path to the temporary file containing the screenshot, or None if the capture failed
        """
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
            
            # Record the timestamp when the screenshot was taken (in UTC)
            self.screenshot_timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            
            # Return the filename for upload
            return temp_filename
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None
    
    def upload_screenshot(self, screenshot_path):
        """Upload a screenshot to the API and return the URL
        
        This method uploads a screenshot to the RemoteIntegrity file server using the API
        details provided in App.jsx. It handles the API request, processes the response,
        and cleans up the temporary file after upload.
        
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
                # Prepare the file for upload using base64 encoding
                files = {
                    'file': (os.path.basename(screenshot_path), image_file, 'image/png')
                }

                # Set headers with API key from App.jsx
                # Note: We don't manually set Content-Type for multipart/form-data
                # as requests will set it automatically with the correct boundary
                headers = {
                    'x-api-key': '2a978046cf9eebb8f8134281a3e5106d05723cae3eaf8ec58f2596d95feca3de'
                }

                # Make the API request to the correct endpoint
                # Using files=files for multipart/form-data instead of json=files
                response = requests.post(
                    'http://5.78.136.221:3020/api/files/5a7f64a1-ab0e-4544-8fcb-4a7b2fc3d428/upload',
                    files=files,
                    headers=headers
                )

            print(f"Image Upload response: {response.json()}")

            # Clean up the temporary file regardless of upload success
            try:
                os.unlink(screenshot_path)
            except Exception as cleanup_error:
                print(f"Warning: Failed to clean up temporary file: {cleanup_error}")
            
            # Process the response
            if response.status_code == 201:
                data = response.json()
                if data.get('success'):
                    return {
                        'url': data['data']['url'],
                        'timestamp': self.screenshot_timestamp
                    }
                else:
                    print(f"API returned success=false: {data.get('message', 'No error message')}")
            else:
                print(f"API request failed with status code {response.status_code}")
            
            return None
        except Exception as e:
            print(f"Error uploading screenshot: {e}")
            return None
            
    def schedule_screenshot(self):
        """Schedule a screenshot to be taken at a random time between 1-8 minutes
        
        This method schedules a screenshot to be taken at a random time between
        self.screenshot_min_interval (1 minute) and self.screenshot_max_interval (8 minutes).
        The screenshot is then uploaded to the server and stored for the next session update.
        
        The method ensures that only one screenshot timer is active at a time by canceling
        any existing timer before creating a new one.
        
        Returns:
            None
        """
        if not self.start_time:
            print("Cannot schedule screenshot: Timer not running")
            return
            
        # Clear any existing screenshot timer to avoid multiple timers
        if self.screenshot_timer:
            self.screenshot_timer.cancel()
            self.screenshot_timer = None
            
        # Generate a random interval between min and max (1-8 minutes)
        random_interval = random.randint(self.screenshot_min_interval, self.screenshot_max_interval)
        
        def take_and_upload_screenshot():
            """Inner function to take and upload a screenshot when the timer fires"""
            if not self.start_time:
                print("Timer stopped before screenshot could be taken")
                return
                
            # Take a screenshot
            screenshot_path = self.take_screenshot()
            
            if screenshot_path:
                # Upload the screenshot
                screenshot_data = self.upload_screenshot(screenshot_path)
                
                if screenshot_data:
                    # Store the screenshot data for the next session update
                    self.screenshots_for_session.append({
                        'timestamp': screenshot_data['timestamp'],
                        'imageUrl': screenshot_data['url']
                    })
                    print(f"Screenshot taken and uploaded: {screenshot_data['url']}")
                else:
                    print("Failed to upload screenshot")
            else:
                print("Failed to take screenshot")
        
        # Schedule the screenshot using a timer
        self.screenshot_timer = threading.Timer(random_interval, take_and_upload_screenshot)
        self.screenshot_timer.daemon = True  # Allow the program to exit even if timer is still running
        self.screenshot_timer.start()
        
        print(f"Screenshot scheduled in {random_interval} seconds ({random_interval/60:.1f} minutes)")
    
    def start_timer(self, project_name, user_note="I am working on Task"):
        """Start the timer and create a new session
        
        Args:
            project_name: The name of the project
            user_note: User's note about what they're working on
        """
        current_time = time.time()
        self.start_time = current_time
        self.current_project = project_name
        self.user_note = user_note
        
        # Reset all activity tracking variables
        self.active_time = 0
        self.idle_time = 0
        self.keyboard_events = 0
        self.mouse_events = 0
        self.keyboard_activity_rate = 0
        self.mouse_activity_rate = 0
        self.is_idle = False
        self.last_activity_time = current_time
        self.last_active_check_time = current_time
        self.last_keyboard_event_time = 0
        self.last_mouse_event_time = 0
        
        # Reset screenshot variables
        self.screenshots_for_session = []
        self.screenshot_timestamp = None
        if self.screenshot_timer:
            self.screenshot_timer.cancel()
            self.screenshot_timer = None
            
        # Reset application tracking variables
        self.applications_usage = {}
        self.last_app_check_time = current_time
        self.applications_for_session = []
        if self.app_timer:
            self.app_timer.cancel()
            self.app_timer = None
            
        # Reset link tracking variables
        self.links_usage = {}
        self.last_link_check_time = current_time
        self.links_for_session = []
        if self.link_timer:
            self.link_timer.cancel()
            self.link_timer = None
        
        # Start activity tracking
        self.start_activity_tracking()
        
        # Start application tracking
        self.start_application_tracking()
        
        # Start link tracking
        self.start_link_tracking()
        
        # Start stats updates
        stats = self.start_stats_updates()
        
        # Create a new session
        result = self.create_session(user_note)
        
        # Start session updates (every 10 minutes)
        self.start_session_updates()
        
        # Add stats to the result
        if result.get("success"):
            result["stats"] = stats
            
        return result

    def stop_timer(self):
        """Stop the timer and update the session"""
        if self.start_time:
            current_time = time.time()
            
            # Perform final activity check
            # Instead of using check_idle_status which would add more time,
            # we'll manually handle the final time calculation
            if self.last_active_check_time is not None:
                if self.is_idle:
                    # Add final idle time
                    final_idle_time = current_time - self.last_active_check_time
                    self.idle_time += final_idle_time
                else:
                    # Add final active time
                    final_active_time = current_time - self.last_active_check_time
                    self.active_time += final_active_time
            
            # Update activity metrics
            self.update_activity_metrics()
            
            # Stop activity tracking
            self.stop_activity_tracking()
            
            # Stop application tracking
            self.stop_application_tracking()
            
            # Stop link tracking
            self.stop_link_tracking()
            
            # Stop session updates
            self.stop_session_updates()
            
            # Calculate total duration
            duration = int(current_time - self.start_time)
            
            # Ensure active_time + idle_time = duration (approximately)
            # This handles any potential rounding errors or missed time
            total_tracked = self.active_time + self.idle_time
            if abs(total_tracked - duration) > 1:  # Allow 1 second difference for rounding
                # If there's a significant difference, adjust active_time
                self.active_time = max(0, duration - self.idle_time)
            
            # Convert to integers for API
            self.active_time = int(self.active_time)
            self.idle_time = int(self.idle_time)
            
            # Store in local database
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with sqlite3.connect(db_file) as conn:
                conn.execute(
                    'INSERT INTO time_entries (project_name, timestamp, duration) VALUES (?, ?, ?)',
                    (self.current_project, timestamp, duration)
                )
            
            # Update the session with all metrics (final update)
            result = self.update_session(
                active_time=self.active_time,
                idle_time=self.idle_time,
                keyboard_rate=self.keyboard_activity_rate,
                mouse_rate=self.mouse_activity_rate,
                is_final_update=True,
                user_note=self.user_note if hasattr(self, 'user_note') else "I am working on Task"
            )
            
            # Stop stats updates
            self.stop_stats_updates()
            
            # Get final stats
            daily_stats = self.get_daily_stats()
            weekly_stats = self.get_weekly_stats()
            
            # Add stats to the result
            if result.get("success"):
                result["stats"] = {
                    "daily": daily_stats,
                    "weekly": weekly_stats
                }
            
            # Reset timer state
            self.start_time = None
            self.current_project = None
            
            return result
        
        return {"success": False, "message": "Timer not running"}

    def record_activity(self, activity_type='mouse'):
        """Record user activity (keyboard or mouse)"""
        current_time = time.time()
        self.last_activity_time = current_time
        
        # If user was idle, add the idle time
        if self.is_idle and self.last_active_check_time is not None:
            idle_duration = current_time - self.last_active_check_time
            self.idle_time += idle_duration
            self.is_idle = False
        
        # Update activity counters with throttling
        if activity_type == 'keyboard':
            # Only count keyboard events if enough time has passed since the last one
            if current_time - self.last_keyboard_event_time >= self.event_throttle_interval:
                self.keyboard_events += 1
                self.last_keyboard_event_time = current_time
        else:  # mouse
            # Only count mouse events if enough time has passed since the last one
            if current_time - self.last_mouse_event_time >= self.event_throttle_interval:
                self.mouse_events += 1
                self.last_mouse_event_time = current_time
    
    def check_idle_status(self):
        """Check if user is idle based on last activity time"""
        if not self.start_time or not self.last_activity_time:
            return
            
        current_time = time.time()
        time_since_last_activity = current_time - self.last_activity_time
        
        # If previously active but now idle
        if not self.is_idle and time_since_last_activity >= self.idle_threshold:
            # Transition from active to idle
            self.is_idle = True
            
            # Add time from last check to now as active time
            if self.last_active_check_time is not None:
                active_duration = current_time - self.last_active_check_time
                self.active_time += active_duration
            
            self.last_active_check_time = current_time
        
        # If previously idle but still idle, update idle time
        elif self.is_idle and self.last_active_check_time is not None:
            idle_duration = current_time - self.last_active_check_time
            self.idle_time += idle_duration
            self.last_active_check_time = current_time
            
        # If active and still active, update active time
        elif not self.is_idle and self.last_active_check_time is not None:
            active_duration = current_time - self.last_active_check_time
            self.active_time += active_duration
            self.last_active_check_time = current_time
    
    def update_activity_metrics(self):
        """Update activity metrics based on current state"""
        if not self.start_time:
            return
            
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Calculate activity rates (events per minute)
        if elapsed > 0:
            minutes = elapsed / 60
            self.keyboard_activity_rate = int(self.keyboard_events / minutes) if minutes > 0 else 0
            self.mouse_activity_rate = int(self.mouse_events / minutes) if minutes > 0 else 0
    
    def start_activity_tracking(self):
        """Start the activity tracking thread and system-wide input listeners"""
        if self.activity_timer:
            return
            
        def activity_check():
            if not self.start_time:
                return
                
            self.check_idle_status()
            self.update_activity_metrics()
            
            # Schedule the next check if timer is still running
            if self.start_time:
                self.activity_timer = threading.Timer(self.activity_check_interval, activity_check)
                self.activity_timer.daemon = True
                self.activity_timer.start()
        
        # Initialize activity tracking
        self.last_activity_time = time.time()
        self.last_active_check_time = self.last_activity_time
        self.is_idle = False
        
        # Start system-wide input listeners if enabled
        if self.system_tracking_enabled:
            try:
                # Start keyboard listener
                self.keyboard_listener = keyboard.Listener(
                    on_press=self.on_keyboard_event,
                    on_release=None
                )
                self.keyboard_listener.daemon = True
                self.keyboard_listener.start()
                
                # Start mouse listener
                self.mouse_listener = mouse.Listener(
                    on_move=self.on_mouse_event,
                    on_click=self.on_mouse_event,
                    on_scroll=self.on_mouse_event
                )
                self.mouse_listener.daemon = True
                self.mouse_listener.start()
                
                print("System-wide activity tracking started")
            except Exception as e:
                print(f"Error starting system-wide activity tracking: {e}")
                self.system_tracking_enabled = False
        
        # Start the activity check timer
        self.activity_timer = threading.Timer(self.activity_check_interval, activity_check)
        self.activity_timer.daemon = True
        self.activity_timer.start()
    
    def stop_activity_tracking(self):
        """Stop the activity tracking thread and system-wide input listeners"""
        if self.activity_timer:
            self.activity_timer.cancel()
            self.activity_timer = None
        
        # Stop system-wide input listeners
        if self.system_tracking_enabled:
            try:
                if self.keyboard_listener:
                    self.keyboard_listener.stop()
                    self.keyboard_listener = None
                
                if self.mouse_listener:
                    self.mouse_listener.stop()
                    self.mouse_listener = None
                
                print("System-wide activity tracking stopped")
            except Exception as e:
                print(f"Error stopping system-wide activity tracking: {e}")
    
    def record_keyboard_activity(self):
        """JavaScript interface method to record keyboard activity"""
        if self.start_time:
            self.record_activity('keyboard')
            return {"success": True}
        return {"success": False, "message": "Timer not running"}
    
    def record_mouse_activity(self):
        """JavaScript interface method to record mouse activity"""
        if self.start_time:
            self.record_activity('mouse')
            return {"success": True}
        return {"success": False, "message": "Timer not running"}
    
    # System-wide activity tracking callback functions for pynput
    def on_keyboard_event(self, *args):
        """Callback function for keyboard events from pynput"""
        if self.start_time:
            self.record_activity('keyboard')
    
    def on_mouse_event(self, *args):
        """Callback function for mouse events from pynput"""
        if self.start_time:
            self.record_activity('mouse')
    
    def get_activity_stats(self):
        """Get current activity statistics"""
        if not self.start_time:
            return {"success": False, "message": "Timer not running"}
            
        return {
            "success": True,
            "active_time": self.active_time,
            "idle_time": self.idle_time,
            "keyboard_rate": self.keyboard_activity_rate,
            "mouse_rate": self.mouse_activity_rate,
            "is_idle": self.is_idle
        }
        
    def check_running_applications(self):
        """Check running applications and update application usage data
        
        This method uses psutil to get information about running processes,
        filters out system processes, and updates the application usage data.
        """
        if not self.start_time:
            return
            
        current_time = time.time()
        
        # If this is the first check, initialize last_app_check_time
        if self.last_app_check_time is None:
            self.last_app_check_time = current_time
            
        # Calculate time elapsed since last check
        time_elapsed = current_time - self.last_app_check_time
        self.last_app_check_time = current_time
        
        # Get current timestamp in ISO format
        current_timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        
        # Define system process patterns to exclude
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
        
        # System directories patterns
        system_dirs = [
            '\\Windows\\', '\\Windows\\System32\\', '\\Windows\\SysWOW64\\',
            '\\Windows\\WinSxS\\', '\\Windows\\servicing\\', '\\ProgramData\\',
            '\\Program Files\\Common Files\\', '\\Program Files (x86)\\Common Files\\'
        ]
        
        # Get list of running processes
        try:
            # Get all running processes
            active_apps = {}
            
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'username']):
                try:
                    # Get process info
                    proc_info = proc.info
                    
                    # Skip processes without a name or executable
                    if not proc_info['name'] or not proc_info['exe']:
                        continue
                    
                    # Use the executable name as the app name
                    app_name = os.path.basename(proc_info['exe'])
                    exe_path = proc_info['exe']
                    
                    # Skip system processes based on name
                    if app_name.lower() in [p.lower() for p in system_process_names]:
                        continue
                    
                    # Skip system processes based on path
                    if any(system_dir.lower() in exe_path.lower() for system_dir in system_dirs):
                        continue
                    
                    # Add to active apps
                    if app_name not in active_apps:
                        active_apps[app_name] = {
                            'name': app_name,
                            'exe': exe_path
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Update application usage data
            for app_name, app_info in active_apps.items():
                if app_name in self.applications_usage:
                    # Update existing application
                    self.applications_usage[app_name]['timeSpent'] += time_elapsed
                    self.applications_usage[app_name]['lastSeen'] = current_timestamp
                else:
                    # Add new application
                    self.applications_usage[app_name] = {
                        'name': app_name,
                        'timeSpent': time_elapsed,
                        'lastSeen': current_timestamp,
                        'exe': app_info['exe']
                    }
                    
        except Exception as e:
            print(f"Error checking running applications: {e}")
            
    def start_application_tracking(self):
        """Start the application tracking thread"""
        if self.app_timer:
            return
            
        def app_check():
            if not self.start_time:
                return
                
            self.check_running_applications()
            
            # Schedule the next check if timer is still running
            if self.start_time:
                self.app_timer = threading.Timer(self.app_check_interval, app_check)
                self.app_timer.daemon = True
                self.app_timer.start()
        
        # Initialize application tracking
        self.last_app_check_time = time.time()
        
        # Start the application check timer
        self.app_timer = threading.Timer(self.app_check_interval, app_check)
        self.app_timer.daemon = True
        self.app_timer.start()
    
    def stop_application_tracking(self):
        """Stop the application tracking thread"""
        if self.app_timer:
            self.app_timer.cancel()
            self.app_timer = None
            
    def prepare_applications_for_session(self):
        """Prepare application data for session updates
        
        This method converts the application usage data from the applications_usage
        dictionary to the format required by the API.
        
        Returns:
            list: A list of application usage data in the format required by the API
        """
        applications_data = []
        
        # Get current timestamp in ISO format
        current_timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        
        # Convert applications_usage dictionary to list of application usage data
        for app_name, app_info in self.applications_usage.items():
            # Only include applications with significant usage (more than 1 second)
            if app_info['timeSpent'] > 1:
                applications_data.append({
                    'name': app_name,
                    'timeSpent': int(app_info['timeSpent']),  # Convert to integer
                    'timestamp': app_info['lastSeen'] if 'lastSeen' in app_info else current_timestamp
                })
        
        # Sort by timeSpent in descending order
        applications_data.sort(key=lambda x: x['timeSpent'], reverse=True)
        
        return applications_data
        
    def get_browser_paths(self):
        """Get browser history database paths based on platform
        
        This method returns a dictionary of browser history database paths
        for each supported browser on the current platform.
        
        Returns:
            dict: A dictionary of browser history database paths
        """
        browser_paths = {}
        system = platform.system()
        home = os.path.expanduser("~")
        
        if system == "Windows":
            # Windows paths
            local_app_data = os.environ.get('LOCALAPPDATA', os.path.join(home, 'AppData', 'Local'))
            app_data = os.environ.get('APPDATA', os.path.join(home, 'AppData', 'Roaming'))
            
            # Chrome
            chrome_path = os.path.join(local_app_data, 'Google', 'Chrome', 'User Data')
            browser_paths['chrome'] = self._find_chromium_history_files(chrome_path)
            
            # Brave
            brave_path = os.path.join(local_app_data, 'BraveSoftware', 'Brave-Browser', 'User Data')
            browser_paths['brave'] = self._find_chromium_history_files(brave_path)
            
            # Edge
            edge_path = os.path.join(local_app_data, 'Microsoft', 'Edge', 'User Data')
            browser_paths['edge'] = self._find_chromium_history_files(edge_path)
            
            # Firefox
            firefox_path = os.path.join(app_data, 'Mozilla', 'Firefox', 'Profiles')
            browser_paths['firefox'] = self._find_firefox_history_files(firefox_path)
            
        elif system == "Darwin":  # macOS
            # Chrome
            chrome_path = os.path.join(home, 'Library', 'Application Support', 'Google', 'Chrome')
            browser_paths['chrome'] = self._find_chromium_history_files(chrome_path)
            
            # Brave
            brave_path = os.path.join(home, 'Library', 'Application Support', 'BraveSoftware', 'Brave-Browser')
            browser_paths['brave'] = self._find_chromium_history_files(brave_path)
            
            # Edge
            edge_path = os.path.join(home, 'Library', 'Application Support', 'Microsoft Edge')
            browser_paths['edge'] = self._find_chromium_history_files(edge_path)
            
            # Firefox
            firefox_path = os.path.join(home, 'Library', 'Application Support', 'Firefox', 'Profiles')
            browser_paths['firefox'] = self._find_firefox_history_files(firefox_path)
            
            # Safari
            safari_history = os.path.join(home, 'Library', 'Safari', 'History.db')
            if os.path.exists(safari_history):
                browser_paths['safari'] = [safari_history]
            else:
                browser_paths['safari'] = []
                
        else:  # Linux
            # Chrome
            chrome_path = os.path.join(home, '.config', 'google-chrome')
            browser_paths['chrome'] = self._find_chromium_history_files(chrome_path)
            
            # Brave
            brave_path = os.path.join(home, '.config', 'BraveSoftware', 'Brave-Browser')
            browser_paths['brave'] = self._find_chromium_history_files(brave_path)
            
            # Edge
            edge_path = os.path.join(home, '.config', 'microsoft-edge')
            browser_paths['edge'] = self._find_chromium_history_files(edge_path)
            
            # Firefox
            firefox_path = os.path.join(home, '.mozilla', 'firefox')
            browser_paths['firefox'] = self._find_firefox_history_files(firefox_path)
            
            # Safari is not available on Linux
            browser_paths['safari'] = []
            
        return browser_paths
        
    def _find_chromium_history_files(self, base_path):
        """Find Chromium-based browser history files
        
        This method finds history database files for Chromium-based browsers
        (Chrome, Brave, Edge) by searching for 'History' files in profile directories.
        
        Args:
            base_path (str): Base path to the browser's user data directory
            
        Returns:
            list: A list of paths to history database files
        """
        history_files = []
        
        if not os.path.exists(base_path):
            return history_files
            
        try:
            # Look for profile directories (Default, Profile 1, Profile 2, etc.)
            profiles = ['Default'] + [f'Profile {i}' for i in range(1, 10)]
            
            for profile in profiles:
                profile_path = os.path.join(base_path, profile)
                history_file = os.path.join(profile_path, 'History')
                
                if os.path.exists(history_file):
                    history_files.append(history_file)
        except Exception as e:
            print(f"Error finding Chromium history files: {e}")
            
        return history_files
        
    def _find_firefox_history_files(self, profiles_path):
        """Find Firefox history files
        
        This method finds history database files for Firefox by searching for
        'places.sqlite' files in profile directories.
        
        Args:
            profiles_path (str): Path to Firefox profiles directory
            
        Returns:
            list: A list of paths to history database files
        """
        history_files = []
        
        if not os.path.exists(profiles_path):
            return history_files
            
        try:
            # Firefox profiles are in directories with random names
            # Look for places.sqlite in each profile directory
            for root, dirs, files in os.walk(profiles_path):
                for file in files:
                    if file == 'places.sqlite':
                        history_files.append(os.path.join(root, file))
        except Exception as e:
            print(f"Error finding Firefox history files: {e}")
            
        return history_files
        
    def get_chrome_history(self, history_file, cutoff_time):
        """Extract history from Chrome/Brave/Edge
        
        This method extracts recent browsing history from a Chromium-based browser's
        history database file.
        
        Args:
            history_file (str): Path to the history database file
            cutoff_time (int): Unix timestamp for the cutoff time
            
        Returns:
            list: A list of dictionaries containing URL, title, and visit time
        """
        history_data = []
        
        # Validate inputs
        if not history_file or not os.path.exists(history_file):
            print(f"Chrome history file does not exist: {history_file}")
            return history_data
            
        # Ensure cutoff_time is valid
        try:
            cutoff_time = int(cutoff_time)
        except (TypeError, ValueError):
            print(f"Invalid cutoff time: {cutoff_time}, using current time - 600 seconds")
            cutoff_time = int(time.time()) - 600
            
        # Always use long-term check mode to ensure we capture all history since timer started
        is_long_term_check = True
        
        # Create a copy of the history file to avoid database lock issues
        temp_dir = tempfile.gettempdir()
        temp_history = os.path.join(temp_dir, f'temp_history_{random.randint(1000, 9999)}.db')
        
        try:
            # Copy the history file to a temporary location
            try:
                shutil.copy2(history_file, temp_history)
                print(f"Successfully copied Chrome history file: {history_file}")
            except (shutil.Error, IOError) as e:
                print(f"Error copying history file {history_file}: {e}")
                return history_data
            
            # Connect to the database
            try:
                conn = sqlite3.connect(temp_history)
                cursor = conn.cursor()
                
                # Query for recent history
                # For long-term checks (first check after app starts), use a larger limit
                # to ensure we capture more history entries
                limit = 5000 if is_long_term_check else 1000
                
                # For long-term checks, also include visit count to prioritize frequently visited URLs
                if is_long_term_check:
                    query = """
                    SELECT urls.url, urls.title, visits.visit_time, urls.visit_count
                    FROM urls JOIN visits ON urls.id = visits.url
                    WHERE visits.visit_time > ?
                    ORDER BY visits.visit_time DESC, urls.visit_count DESC
                    LIMIT ?
                    """
                    
                    # Chrome stores time as microseconds since Jan 1, 1601 UTC
                    # Convert from Unix timestamp to Chrome timestamp
                    chrome_cutoff = (cutoff_time + 11644473600) * 1000000
                    
                    cursor.execute(query, (chrome_cutoff, limit))
                    
                    print(f"Executing Chrome history query with extended limit ({limit}) for long-term check")
                    
                    for url, title, visit_time, visit_count in cursor.fetchall():
                        try:
                            # Convert Chrome timestamp to Unix timestamp
                            unix_time = visit_time // 1000000 - 11644473600
                            
                            # Skip invalid timestamps
                            if unix_time <= 0 or unix_time > time.time() + 86400:  # Allow 1 day in the future for clock skew
                                continue
                                
                            # Format timestamp as ISO string
                            timestamp = datetime.fromtimestamp(unix_time, timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                            
                            # Skip empty URLs
                            if not url:
                                continue
                                
                            history_data.append({
                                'url': url,
                                'title': title or url,
                                'timestamp': timestamp,
                                'visit_time': unix_time,
                                'visit_count': visit_count
                            })
                        except Exception as entry_error:
                            print(f"Error processing Chrome history entry: {entry_error}")
                            continue
                else:
                    # Regular query for short-term checks
                    query = """
                    SELECT urls.url, urls.title, visits.visit_time
                    FROM urls JOIN visits ON urls.id = visits.url
                    WHERE visits.visit_time > ?
                    ORDER BY visits.visit_time DESC
                    LIMIT ?
                    """
                    
                    # Chrome stores time as microseconds since Jan 1, 1601 UTC
                    # Convert from Unix timestamp to Chrome timestamp
                    chrome_cutoff = (cutoff_time + 11644473600) * 1000000
                    
                    cursor.execute(query, (chrome_cutoff, limit))
                    
                    for url, title, visit_time in cursor.fetchall():
                        try:
                            # Convert Chrome timestamp to Unix timestamp
                            unix_time = visit_time // 1000000 - 11644473600
                            
                            # Skip invalid timestamps
                            if unix_time <= 0 or unix_time > time.time() + 86400:  # Allow 1 day in the future for clock skew
                                continue
                                
                            # Format timestamp as ISO string
                            timestamp = datetime.fromtimestamp(unix_time, timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                            
                            # Skip empty URLs
                            if not url:
                                continue
                                
                            history_data.append({
                                'url': url,
                                'title': title or url,
                                'timestamp': timestamp,
                                'visit_time': unix_time
                            })
                        except Exception as entry_error:
                            print(f"Error processing Chrome history entry: {entry_error}")
                            continue
                
                print(f"Found {len(history_data)} Chrome history entries from {os.path.basename(history_file)}")
                conn.close()
            except sqlite3.Error as sql_error:
                print(f"SQLite error when reading Chrome history: {sql_error}")
                return history_data
        except Exception as e:
            print(f"Error extracting Chrome history: {e}")
        finally:
            # Clean up the temporary file
            try:
                if os.path.exists(temp_history):
                    os.remove(temp_history)
            except Exception as cleanup_error:
                print(f"Error cleaning up temporary Chrome history file: {cleanup_error}")
                pass
                
        return history_data
        
    def get_firefox_history(self, history_file, cutoff_time):
        """Extract history from Firefox
        
        This method extracts recent browsing history from a Firefox history database file.
        
        Args:
            history_file (str): Path to the history database file
            cutoff_time (int): Unix timestamp for the cutoff time
            
        Returns:
            list: A list of dictionaries containing URL, title, and visit time
        """
        history_data = []
        
        # Validate inputs
        if not history_file or not os.path.exists(history_file):
            print(f"Firefox history file does not exist: {history_file}")
            return history_data
            
        # Ensure cutoff_time is valid
        try:
            cutoff_time = int(cutoff_time)
        except (TypeError, ValueError):
            print(f"Invalid cutoff time: {cutoff_time}, using current time - 600 seconds")
            cutoff_time = int(time.time()) - 600
            
        # Always use long-term check mode to ensure we capture all history since timer started
        is_long_term_check = True
        
        # Create a copy of the history file to avoid database lock issues
        temp_dir = tempfile.gettempdir()
        temp_history = os.path.join(temp_dir, f'temp_history_{random.randint(1000, 9999)}.db')
        
        try:
            # Copy the history file to a temporary location
            try:
                shutil.copy2(history_file, temp_history)
                print(f"Successfully copied Firefox history file: {history_file}")
            except (shutil.Error, IOError) as e:
                print(f"Error copying Firefox history file {history_file}: {e}")
                return history_data
            
            # Connect to the database
            try:
                conn = sqlite3.connect(temp_history)
                cursor = conn.cursor()
                
                # Query for recent history
                # For long-term checks (first check after app starts), use a larger limit
                # to ensure we capture more history entries
                limit = 5000 if is_long_term_check else 1000
                
                # For long-term checks, also include visit count to prioritize frequently visited URLs
                if is_long_term_check:
                    query = """
                    SELECT p.url, p.title, h.visit_date, p.visit_count
                    FROM moz_places p JOIN moz_historyvisits h ON p.id = h.place_id
                    WHERE h.visit_date > ?
                    ORDER BY h.visit_date DESC, p.visit_count DESC
                    LIMIT ?
                    """
                    
                    # Firefox stores time as microseconds since Jan 1, 1970 UTC
                    firefox_cutoff = cutoff_time * 1000000
                    
                    cursor.execute(query, (firefox_cutoff, limit))
                    
                    print(f"Executing Firefox history query with extended limit ({limit}) for long-term check")
                    
                    for url, title, visit_time, visit_count in cursor.fetchall():
                        try:
                            # Convert Firefox timestamp to Unix timestamp
                            unix_time = visit_time // 1000000
                            
                            # Skip invalid timestamps
                            if unix_time <= 0 or unix_time > time.time() + 86400:  # Allow 1 day in the future for clock skew
                                continue
                                
                            # Format timestamp as ISO string
                            timestamp = datetime.fromtimestamp(unix_time, timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                            
                            # Skip empty URLs
                            if not url:
                                continue
                                
                            history_data.append({
                                'url': url,
                                'title': title or url,
                                'timestamp': timestamp,
                                'visit_time': unix_time,
                                'visit_count': visit_count
                            })
                        except Exception as entry_error:
                            print(f"Error processing Firefox history entry: {entry_error}")
                            continue
                else:
                    # Regular query for short-term checks
                    query = """
                    SELECT p.url, p.title, h.visit_date
                    FROM moz_places p JOIN moz_historyvisits h ON p.id = h.place_id
                    WHERE h.visit_date > ?
                    ORDER BY h.visit_date DESC
                    LIMIT ?
                    """
                    
                    # Firefox stores time as microseconds since Jan 1, 1970 UTC
                    firefox_cutoff = cutoff_time * 1000000
                    
                    cursor.execute(query, (firefox_cutoff, limit))
                    
                    for url, title, visit_time in cursor.fetchall():
                        try:
                            # Convert Firefox timestamp to Unix timestamp
                            unix_time = visit_time // 1000000
                            
                            # Skip invalid timestamps
                            if unix_time <= 0 or unix_time > time.time() + 86400:  # Allow 1 day in the future for clock skew
                                continue
                                
                            # Format timestamp as ISO string
                            timestamp = datetime.fromtimestamp(unix_time, timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                            
                            # Skip empty URLs
                            if not url:
                                continue
                                
                            history_data.append({
                                'url': url,
                                'title': title or url,
                                'timestamp': timestamp,
                                'visit_time': unix_time
                            })
                        except Exception as entry_error:
                            print(f"Error processing Firefox history entry: {entry_error}")
                            continue
                
                print(f"Found {len(history_data)} Firefox history entries from {os.path.basename(os.path.dirname(history_file))}")
                conn.close()
            except sqlite3.Error as sql_error:
                print(f"SQLite error when reading Firefox history: {sql_error}")
                return history_data
        except Exception as e:
            print(f"Error extracting Firefox history: {e}")
        finally:
            # Clean up the temporary file
            try:
                if os.path.exists(temp_history):
                    os.remove(temp_history)
            except Exception as cleanup_error:
                print(f"Error cleaning up temporary Firefox history file: {cleanup_error}")
                pass
                
        return history_data
        
    def get_safari_history(self, history_file, cutoff_time):
        """Extract history from Safari
        
        This method extracts recent browsing history from a Safari history database file.
        
        Args:
            history_file (str): Path to the history database file
            cutoff_time (int): Unix timestamp for the cutoff time
            
        Returns:
            list: A list of dictionaries containing URL, title, and visit time
        """
        history_data = []
        
        # Validate inputs
        if not history_file or not os.path.exists(history_file):
            print(f"Safari history file does not exist: {history_file}")
            return history_data
            
        # Ensure cutoff_time is valid
        try:
            cutoff_time = int(cutoff_time)
        except (TypeError, ValueError):
            print(f"Invalid cutoff time: {cutoff_time}, using current time - 600 seconds")
            cutoff_time = int(time.time()) - 600
            
        # Always use long-term check mode to ensure we capture all history since timer started
        is_long_term_check = True
        
        # Create a copy of the history file to avoid database lock issues
        temp_dir = tempfile.gettempdir()
        temp_history = os.path.join(temp_dir, f'temp_history_{random.randint(1000, 9999)}.db')
        
        try:
            # Copy the history file to a temporary location
            try:
                shutil.copy2(history_file, temp_history)
                print(f"Successfully copied Safari history file: {history_file}")
            except (shutil.Error, IOError) as e:
                print(f"Error copying Safari history file {history_file}: {e}")
                return history_data
            
            # Connect to the database
            try:
                conn = sqlite3.connect(temp_history)
                cursor = conn.cursor()
                
                # Query for recent history
                # For long-term checks (first check after app starts), use a larger limit
                # to ensure we capture more history entries
                limit = 5000 if is_long_term_check else 1000
                
                # For long-term checks, also include visit count to prioritize frequently visited URLs
                # Note: Safari schema might be different, so we need to adapt the query
                try:
                    # First, check if the visit_count column exists in the history_items table
                    cursor.execute("PRAGMA table_info(history_items)")
                    columns = [column[1] for column in cursor.fetchall()]
                    has_visit_count = 'visit_count' in columns
                    
                    if is_long_term_check and has_visit_count:
                        query = """
                        SELECT i.url, v.title, v.visit_time, i.visit_count
                        FROM history_items i JOIN history_visits v ON i.id = v.history_item
                        WHERE v.visit_time > ?
                        ORDER BY v.visit_time DESC, i.visit_count DESC
                        LIMIT ?
                        """
                        
                        # Safari stores time as seconds since Jan 1, 2001 UTC
                        # Convert from Unix timestamp to Safari timestamp
                        safari_cutoff = cutoff_time - 978307200
                        
                        cursor.execute(query, (safari_cutoff, limit))
                        
                        print(f"Executing Safari history query with extended limit ({limit}) for long-term check")
                        
                        for url, title, visit_time, visit_count in cursor.fetchall():
                            try:
                                # Convert Safari timestamp to Unix timestamp
                                unix_time = visit_time + 978307200
                                
                                # Skip invalid timestamps
                                if unix_time <= 0 or unix_time > time.time() + 86400:  # Allow 1 day in the future for clock skew
                                    continue
                                    
                                # Format timestamp as ISO string
                                timestamp = datetime.fromtimestamp(unix_time, timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                                
                                # Skip empty URLs
                                if not url:
                                    continue
                                    
                                history_data.append({
                                    'url': url,
                                    'title': title or url,
                                    'timestamp': timestamp,
                                    'visit_time': unix_time,
                                    'visit_count': visit_count
                                })
                            except Exception as entry_error:
                                print(f"Error processing Safari history entry: {entry_error}")
                                continue
                    else:
                        # Regular query for short-term checks or if visit_count is not available
                        query = """
                        SELECT i.url, v.title, v.visit_time
                        FROM history_items i JOIN history_visits v ON i.id = v.history_item
                        WHERE v.visit_time > ?
                        ORDER BY v.visit_time DESC
                        LIMIT ?
                        """
                        
                        # Safari stores time as seconds since Jan 1, 2001 UTC
                        # Convert from Unix timestamp to Safari timestamp
                        safari_cutoff = cutoff_time - 978307200
                        
                        cursor.execute(query, (safari_cutoff, limit))
                        
                        for url, title, visit_time in cursor.fetchall():
                            try:
                                # Convert Safari timestamp to Unix timestamp
                                unix_time = visit_time + 978307200
                                
                                # Skip invalid timestamps
                                if unix_time <= 0 or unix_time > time.time() + 86400:  # Allow 1 day in the future for clock skew
                                    continue
                                    
                                # Format timestamp as ISO string
                                timestamp = datetime.fromtimestamp(unix_time, timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                                
                                # Skip empty URLs
                                if not url:
                                    continue
                                    
                                history_data.append({
                                    'url': url,
                                    'title': title or url,
                                    'timestamp': timestamp,
                                    'visit_time': unix_time
                                })
                            except Exception as entry_error:
                                print(f"Error processing Safari history entry: {entry_error}")
                                continue
                except sqlite3.Error as schema_error:
                    print(f"Error checking Safari schema: {schema_error}")
                    # Fall back to basic query
                    query = """
                    SELECT i.url, v.title, v.visit_time
                    FROM history_items i JOIN history_visits v ON i.id = v.history_item
                    WHERE v.visit_time > ?
                    ORDER BY v.visit_time DESC
                    LIMIT ?
                    """
                    
                    safari_cutoff = cutoff_time - 978307200
                    cursor.execute(query, (safari_cutoff, limit))
                    
                    for url, title, visit_time in cursor.fetchall():
                        try:
                            unix_time = visit_time + 978307200
                            if unix_time <= 0 or unix_time > time.time() + 86400:
                                continue
                            timestamp = datetime.fromtimestamp(unix_time, timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                            if not url:
                                continue
                            history_data.append({
                                'url': url,
                                'title': title or url,
                                'timestamp': timestamp,
                                'visit_time': unix_time
                            })
                        except Exception as entry_error:
                            print(f"Error processing Safari history entry: {entry_error}")
                            continue
                
                print(f"Found {len(history_data)} Safari history entries")
                conn.close()
            except sqlite3.Error as sql_error:
                print(f"SQLite error when reading Safari history: {sql_error}")
                return history_data
        except Exception as e:
            print(f"Error extracting Safari history: {e}")
        finally:
            # Clean up the temporary file
            try:
                if os.path.exists(temp_history):
                    os.remove(temp_history)
            except Exception as cleanup_error:
                print(f"Error cleaning up temporary Safari history file: {cleanup_error}")
                pass
                
        return history_data
        
    def check_browser_links(self):
        """Check browser links and update link usage data
        
        This method checks browser history for all supported browsers and updates
        the link usage data with the time spent on each link.
        
        On the first check after the app starts (when last_link_check_time is None),
        it uses the timer start time as the cutoff to only capture browser history
        from when the timer is running. For subsequent checks, it uses the
        regular session update interval (10 minutes) to capture only recent history.
        
        The method handles various edge cases and error conditions, such as missing
        or corrupt history files, database lock issues, and invalid timestamps.
        
        Returns:
            None
        """
        if not self.start_time:
            return
            
        current_time = time.time()
        
        # If this is the first check, initialize last_link_check_time
        first_check = self.last_link_check_time is None
        if first_check:
            self.last_link_check_time = current_time
            
        # Calculate time elapsed since last check
        time_elapsed = current_time - self.last_link_check_time
        self.last_link_check_time = current_time
        
        # Get current timestamp in ISO format
        current_timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        
        # Calculate cutoff time
        # For the first check, use the timer start time to only capture history since timer started
        # For subsequent checks, use the last check time minus the session update interval
        if first_check:
            # Use timer start time for the first check to only capture history since timer started
            cutoff_time = int(self.start_time)
            print(f"First browser history check - using timer start time to capture history only since timer started")
        else:
            # Use regular session update interval for subsequent checks
            cutoff_time = int(current_time) - self.session_update_interval
        
        try:
            # Get browser paths
            browser_paths = self.get_browser_paths()
            
            # Track the total number of history entries found
            total_history_entries = 0
            
            # Process each browser type
            for browser_type in self.supported_browsers:
                history_files = browser_paths.get(browser_type, [])
                
                for history_file in history_files:
                    try:
                        # Get history data based on browser type
                        if browser_type in ['chrome', 'brave', 'edge']:
                            history_data = self.get_chrome_history(history_file, cutoff_time)
                        elif browser_type == 'firefox':
                            history_data = self.get_firefox_history(history_file, cutoff_time)
                        elif browser_type == 'safari':
                            history_data = self.get_safari_history(history_file, cutoff_time)
                        else:
                            continue
                        
                        # Update total history entries count
                        total_history_entries += len(history_data)
                        
                        # Process history data
                        for entry in history_data:
                            url = entry['url']
                            title = entry['title']
                            
                            # Skip about: and chrome:// URLs and other browser-specific URLs
                            if url.startswith(('about:', 'chrome://', 'edge://', 'brave://', 'firefox://', 'safari://', 'file://', 'data:')):
                                continue
                                
                            # Skip empty URLs or titles
                            if not url or not title:
                                continue
                                
                            # Normalize URL (remove trailing slashes, etc.)
                            url = url.rstrip('/')
                            
                            # Update link usage data
                            if url in self.links_usage:
                                # Update existing link
                                # Distribute time based on number of entries, but ensure at least 1 second per entry
                                time_per_entry = max(1, time_elapsed / max(1, total_history_entries))
                                self.links_usage[url]['timeSpent'] += time_per_entry
                                self.links_usage[url]['lastSeen'] = current_timestamp
                            else:
                                # Add new link
                                time_per_entry = max(1, time_elapsed / max(1, total_history_entries))
                                self.links_usage[url] = {
                                    'url': url,
                                    'title': title,
                                    'timeSpent': time_per_entry,
                                    'lastSeen': current_timestamp
                                }
                    except Exception as e:
                        # Log the error but continue processing other history files
                        print(f"Error processing history file {history_file}: {e}")
                        continue
        except Exception as e:
            print(f"Error checking browser links: {e}")
            # Continue execution even if there's an error
            
    def start_link_tracking(self):
        """Start the link tracking thread
        
        This method starts a periodic thread to check browser links and update
        the link usage data. The thread runs every self.link_check_interval seconds.
        """
        # Don't start if already running
        if self.link_timer:
            return
            
        def link_check():
            """Inner function to check browser links periodically"""
            # Stop if timer is no longer running
            if not self.start_time:
                return
                
            try:
                # Check browser links
                self.check_browser_links()
            except Exception as e:
                # Log error but continue execution
                print(f"Error in link check thread: {e}")
            
            # Schedule the next check if timer is still running
            if self.start_time:
                self.link_timer = threading.Timer(self.link_check_interval, link_check)
                self.link_timer.daemon = True
                self.link_timer.start()
        
        # Initialize link tracking
        self.last_link_check_time = time.time()
        
        # Start the link check timer
        self.link_timer = threading.Timer(self.link_check_interval, link_check)
        self.link_timer.daemon = True
        self.link_timer.start()
        
        print(f"Link tracking started with interval of {self.link_check_interval} seconds")
    
    def stop_link_tracking(self):
        """Stop the link tracking thread
        
        This method stops the periodic thread that checks browser links.
        """
        if self.link_timer:
            self.link_timer.cancel()
            self.link_timer = None
            print("Link tracking stopped")
            
    def prepare_links_for_session(self):
        """Prepare link data for session updates
        
        This method converts the link usage data from the links_usage
        dictionary to the format required by the API.
        
        It includes several robustness features:
        - Checks for empty links_usage and attempts to force a browser history check if needed
        - Tracks metrics for debugging (total links, valid links, skipped links, error links)
        - Prioritizes links by timeSpent and visit_count (when available)
        - Limits the number of links to prevent oversized payloads
        - Provides detailed logging for troubleshooting
        
        If no valid links are found, it returns an empty list and logs a warning.
        
        Returns:
            list: A list of link usage data in the format required by the API
        """
        links_data = []
        
        try:
            # Get current timestamp in ISO format
            current_timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            
            # Check if links_usage is empty
            if not self.links_usage:
                print("Warning: links_usage is empty. No browser history data collected.")
                # If this is the first check after app startup, try to collect browser history now
                if self.last_link_check_time is not None and time.time() - self.last_link_check_time < 60:
                    print("This appears to be soon after startup. Forcing a browser history check with 24-hour window...")
                    # Force a browser history check with a 24-hour window
                    self.last_link_check_time = None
                    self.check_browser_links()
            
            # Track metrics for debugging
            total_links = len(self.links_usage)
            valid_links = 0
            skipped_links = 0
            error_links = 0
            
            # Convert links_usage dictionary to list of link usage data
            for url, link_info in self.links_usage.items():
                try:
                    # Skip invalid entries
                    if not url or not isinstance(link_info, dict):
                        skipped_links += 1
                        continue
                        
                    # Ensure required fields exist
                    if 'title' not in link_info or 'timeSpent' not in link_info:
                        skipped_links += 1
                        continue
                        
                    # Only include links with significant usage (more than 1 second)
                    if link_info['timeSpent'] > 1:
                        # Ensure title is a string
                        title = str(link_info['title']) if link_info['title'] else url
                        
                        # Limit title and URL length to prevent oversized payloads
                        title = title[:255]  # Limit title to 255 characters
                        url_to_send = url[:2048]  # Limit URL to 2048 characters
                        
                        # Add visit_count if available (for prioritization)
                        link_data = {
                            'url': url_to_send,
                            'title': title,
                            'timeSpent': int(link_info['timeSpent']),  # Convert to integer
                            'timestamp': link_info['lastSeen'] if 'lastSeen' in link_info else current_timestamp
                        }
                        
                        # Add visit_count if available
                        if 'visit_count' in link_info:
                            link_data['visit_count'] = link_info['visit_count']
                        
                        links_data.append(link_data)
                        valid_links += 1
                    else:
                        skipped_links += 1
                except Exception as e:
                    try:
                        print(f"Error processing link: {str(e)}")
                    except Exception as print_err:
                        print(f"Print error: {str(print_err)}")
                    error_links += 1
                    continue
            
            # Log metrics - safely handle potential encoding issues
            try:
                print(f"Links processing metrics: Total={total_links}, Valid={valid_links}, Skipped={skipped_links}, Errors={error_links}")
            except Exception as e:
                print(f"Print error in links metrics: {str(e)}")
            
            # Sort by timeSpent in descending order
            links_data.sort(key=lambda x: x['timeSpent'], reverse=True)
            
            # If we have visit_count, use it as a secondary sort key
            if any('visit_count' in link for link in links_data):
                links_data.sort(key=lambda x: (x['timeSpent'], x.get('visit_count', 0)), reverse=True)
            
            # Limit the number of links to prevent oversized payloads
            max_links = 100  # Limit to 100 links per session update
            if len(links_data) > max_links:
                print(f"Warning: Limiting links from {len(links_data)} to {max_links} to prevent oversized payloads")
                links_data = links_data[:max_links]
            
            # If we still have no links, log a warning
            if not links_data:
                print("Warning: No valid links found for session update. Check browser history access.")
                
        except Exception as e:
            print(f"Error preparing links for session: {e}")
            # Return an empty list if there's an error
            return []
            
        return links_data
    
    def get_daily_stats(self):
        """Get daily stats for the current employee"""
        if not self.auth_token:
            return {"success": False, "message": "Not authenticated"}
        
        try:
            # Get employee ID from stored user data
            employee_id = self.user_data.get('employeeId')
            if not employee_id:
                return {"success": False, "message": "Employee ID not found"}
                
            response = requests.get(
                f'{URLS["DAILY_STATS"]}/{employee_id}?timezone={local_tz}',
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            )
            data = response.json()
            
            if data.get('success'):
                return {"success": True, "data": data['data']}
            else:
                return {"success": False, "message": data.get('message', 'Failed to get daily stats')}
        except Exception as e:
            print(f"Daily stats error: {e}")
            window.evaluate_js('window.toastFromPython("Failed to get daily stats!", "error")')
            return {"success": False, "message": f"An error occurred: {str(e)}"}
    
    def get_weekly_stats(self):
        """Get weekly stats for the current employee"""
        if not self.auth_token:
            return {"success": False, "message": "Not authenticated"}
        
        try:
            # Get employee ID from stored user data
            employee_id = self.user_data.get('employeeId')
            if not employee_id:
                return {"success": False, "message": "Employee ID not found"}
                
            response = requests.get(
                f'{URLS["WEEKLY_STATS"]}/{employee_id}?timezone={local_tz}',
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            )
            data = response.json()
            
            if data.get('success'):
                return {"success": True, "data": data['data']}
            else:
                return {"success": False, "message": data.get('message', 'Failed to get weekly stats')}
        except Exception as e:
            print(f"Weekly stats error: {e}")
            return {"success": False, "message": f"An error occurred: {str(e)}"}
    
    def get_time_entries(self):
        with sqlite3.connect(db_file) as conn:
            c = conn.cursor()
            c.execute('SELECT project_name, timestamp, duration FROM time_entries ORDER BY id DESC LIMIT 10')
            return [{'project': row[0], 'timestamp': row[1], 'duration': row[2]} for row in c.fetchall()]
            
    def compare_versions(self, version1, version2):
        """Compare two version strings and return True if version2 is newer than version1"""
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        # Pad with zeros if versions have different lengths
        while len(v1_parts) < len(v2_parts):
            v1_parts.append(0)
        while len(v2_parts) < len(v1_parts):
            v2_parts.append(0)
            
        # Compare each part
        for i in range(len(v1_parts)):
            if v2_parts[i] > v1_parts[i]:
                return True
            elif v2_parts[i] < v1_parts[i]:
                return False
                
        # If we get here, versions are equal
        return False
        
    def check_for_updates(self):
        """Check for updates by querying the GitHub API for the latest release"""
        try:
            # Get the latest release from GitHub
            response = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest")
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"Failed to check for updates. Status code: {response.status_code}"
                }
                
            release_data = response.json()
            latest_version = release_data.get('tag_name', '').lstrip('v')
            
            # If no version found, return error
            if not latest_version:
                return {
                    "success": False,
                    "message": "Could not determine latest version"
                }
                
            # Compare versions
            update_available = self.compare_versions(APP_VERSION, latest_version)
            
            return {
                "success": True,
                "update_available": update_available,
                "current_version": APP_VERSION,
                "latest_version": latest_version,
                "release_notes": release_data.get('body', ''),
                "download_url": release_data.get('assets', [{}])[0].get('browser_download_url', '') if release_data.get('assets') else ''
            }
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return {
                "success": False,
                "message": f"An error occurred while checking for updates: {str(e)}"
            }
            
    def download_update(self, download_url):
        """Download the update from the provided URL"""
        try:
            # Create updates directory if it doesn't exist
            updates_dir = os.path.join(DATA_DIR, 'updates')
            os.makedirs(updates_dir, exist_ok=True)
            
            # Download the file
            response = requests.get(download_url, stream=True)
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"Failed to download update. Status code: {response.status_code}"
                }
                
            # Get filename from URL
            filename = os.path.basename(download_url)
            file_path = os.path.join(updates_dir, filename)
            
            # Save the file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            return {
                "success": True,
                "file_path": file_path
            }
        except Exception as e:
            print(f"Error downloading update: {e}")
            return {
                "success": False,
                "message": f"An error occurred while downloading the update: {str(e)}"
            }
            
    def install_update(self, file_path):
        """Install the update and restart the application"""
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "message": "Update file not found"
                }
                
            # Get file extension
            _, ext = os.path.splitext(file_path)
            
            # Handle different file types
            if ext.lower() == '.exe':
                # For Windows executable installers
                # Start the installer and exit current app
                subprocess.Popen([file_path, '/SILENT', '/CLOSEAPPLICATIONS'])
                # Schedule app exit
                threading.Timer(1.0, lambda: os._exit(0)).start()
                return {"success": True, "message": "Installing update..."}
                
            elif ext.lower() == '.msi':
                # For MSI installers
                subprocess.Popen(['msiexec', '/i', file_path, '/quiet', '/norestart'])
                threading.Timer(1.0, lambda: os._exit(0)).start()
                return {"success": True, "message": "Installing update..."}
                
            elif ext.lower() in ['.zip', '.7z']:
                # For zip archives, extract and replace current executable
                # This is a simplified example - actual implementation would depend on your app structure
                # You might need to extract files, copy them to the right location, etc.
                return {
                    "success": False,
                    "message": "Archive installation not implemented"
                }
                
            else:
                return {
                    "success": False,
                    "message": f"Unsupported update file type: {ext}"
                }
                
        except Exception as e:
            print(f"Error installing update: {e}")
            return {
                "success": False,
                "message": f"An error occurred while installing the update: {str(e)}"
            }
            
    def is_timer_running(self):
        """Check if the timer is currently running"""
        return self.start_time is not None
        
    def handle_close_event(self):
        """Handle window close event, showing confirmation dialog if timer is running"""
        if not self.is_timer_running():
            # Timer is not running, allow window to close
            return True
            
        # Timer is running, show confirmation dialog
        result = self.window.create_confirmation_dialog(
            "Timer Running",
            "Your timer is currently running. Are you sure you want to close the app?"
        )
        
        if result:
            # User confirmed, stop the timer and update the session
            try:
                self.stop_timer()
                print("Timer stopped due to app close")
                return True
            except Exception as e:
                print(f"Error stopping timer on app close: {e}")
                # Still allow the app to close even if there was an error stopping the timer
                return True
        else:
            # User cancelled, prevent window from closing
            return False

if __name__ == '__main__':
    init_db()
    api = Api()

    # Determine if we're in development or production mode
    #DEBUG = True
    DEBUG = URLS["DEBUG"]
    if len(sys.argv) > 1 and sys.argv[1] == '--dev':
        DEBUG = True

    # Handle PyInstaller bundled resources
    # When running as a PyInstaller executable, resources are in a temporary directory
    # accessible through sys._MEIPASS
    base_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    
    # Get the appropriate URL
    if DEBUG:
        #url = "http://localhost:5173"
        url = os.path.join(base_dir, "dist", "index.html")
        debug = True
        print("Running in DEVELOPMENT mode with DevTools enabled")
    else:
        url = os.path.join(base_dir, "dist", "index.html")
        debug = False
        print("Running in PRODUCTION mode")

    # Get primary monitor size
    monitor = screeninfo.get_monitors()[0]
    screen_width = monitor.width
    screen_height = monitor.height

    # Set window size relative to screen size
    win_width = min(400, screen_width + 50)
    win_height = min(630, screen_height + 100)

    # Create the window
    window = webview.create_window(
        "RI Tracker",
        url,
        js_api=api,
        width=win_width,
        height=win_height,
        min_size=(300, 400),
        resizable=False,
        confirm_close=False,  # We'll handle confirmation ourselves
    )
    
    # Store window reference in the API instance
    api.window = window
    
    # Set up the on_closing event handler
    window.events.closing += api.handle_close_event

    # Start the application
    #webview.start(debug=debug)  # Optional: use 'cef' or 'qt' for better styling support
    webview.start(debug=debug)

