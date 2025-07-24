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
from datetime import datetime, timezone
from config import URLS


APP_NAME = "RI_Tracker"
APP_VERSION = "1.0.7"  # Current version of the application
GITHUB_REPO = "younusFoysal/RI-Tracker-Lite"  # Replace with your actual GitHub repository
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
        
        # Activity tracking variables
        self.last_activity_time = None
        self.is_idle = False
        self.idle_threshold = 60  # seconds of inactivity before considered idle
        self.keyboard_events = 0
        self.mouse_events = 0
        self.activity_timer = None
        self.activity_check_interval = 1  # seconds between activity checks
        self.last_active_check_time = None
        
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
                f'{URLS['PROFILE']}/{employee_id}',
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

    def create_session(self):
        """Create a new session via API"""
        if not self.auth_token:
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
                return {"success": False, "message": "Employee ID or Company ID not found"}
            
            # Create session data
            start_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

            session_data = {
                "employeeId": employee_id,
                "companyId": company_id,
                "startTime": start_time,
                "notes": "Session from RI Tracker Lite APP v1.",
                "timezone": "America/New_York"
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
                return {"success": False, "message": data.get('message', 'Failed to create session')}
        except Exception as e:
            print(f"Create session error: {e}")
            return {"success": False, "message": f"An error occurred: {str(e)}"}
    
    def update_session(self, active_time, idle_time=0, keyboard_rate=0, mouse_rate=0, is_final_update=False):
        """Update an existing session via API
        
        Args:
            active_time: Time spent actively working (in seconds)
            idle_time: Time spent idle (in seconds)
            keyboard_rate: Keyboard activity rate (events per minute)
            mouse_rate: Mouse activity rate (events per minute)
            is_final_update: Whether this is the final update (when timer is stopped)
        """
        if not self.auth_token or not self.session_id:
            return {"success": False, "message": "Not authenticated or no active session"}
        
        try:
            # Create session update data
            end_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

            update_data = {
                "endTime": end_time,
                "activeTime": active_time,
                "idleTime": idle_time,
                "keyboardActivityRate": keyboard_rate,
                "mouseActivityRate": mouse_rate,
                "timezone": "America/New_York"
            }
            
            # Send request to update session
            response = requests.patch(
                f'{URLS["SESSIONS"]}/{self.session_id}',
                json=update_data,
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            )
            
            data = response.json()
            
            if data.get('success'):
                # Only reset session_id if this is the final update
                if is_final_update:
                    self.session_id = None
                return {"success": True, "data": data['data']}
            else:
                return {"success": False, "message": data.get('message', 'Failed to update session')}
        except Exception as e:
            print(f"Update session error: {e}")
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
                is_final_update=False
            )
            
            # Schedule the next update if timer is still running
            if self.start_time:
                self.session_update_timer = threading.Timer(self.session_update_interval, update_session_periodically)
                self.session_update_timer.daemon = True
                self.session_update_timer.start()
        
        # Start the session update timer
        self.session_update_timer = threading.Timer(self.session_update_interval, update_session_periodically)
        self.session_update_timer.daemon = True
        self.session_update_timer.start()
        
    def stop_session_updates(self):
        """Stop periodic session updates"""
        if self.session_update_timer:
            self.session_update_timer.cancel()
            self.session_update_timer = None
    
    def start_timer(self, project_name):
        """Start the timer and create a new session"""
        current_time = time.time()
        self.start_time = current_time
        self.current_project = project_name
        
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
        
        # Start activity tracking
        self.start_activity_tracking()
        
        # Start stats updates
        stats = self.start_stats_updates()
        
        # Create a new session
        result = self.create_session()
        
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
                is_final_update=True
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
        """Start the activity tracking thread"""
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
        
        # Start the activity check timer
        self.activity_timer = threading.Timer(self.activity_check_interval, activity_check)
        self.activity_timer.daemon = True
        self.activity_timer.start()
    
    def stop_activity_tracking(self):
        """Stop the activity tracking thread"""
        if self.activity_timer:
            self.activity_timer.cancel()
            self.activity_timer = None
    
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
                f'{URLS["DAILY_STATS"]}/{employee_id}',
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
                f'{URLS["WEEKLY_STATS"]}/{employee_id}',
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

if __name__ == '__main__':
    init_db()
    api = Api()

    # Determine if we're in development or production mode
    #DEBUG = True
    DEBUG = URLS["DEBUG"]
    if len(sys.argv) > 1 and sys.argv[1] == '--dev':
        DEBUG = True

    # Get the appropriate URL
    if DEBUG:
        #url = "http://localhost:5173"
        url = "dist/index.html"
        debug = True
        print("Running in DEVELOPMENT mode with DevTools enabled")
    else:
        url = "dist/index.html"
        debug = False
        print("Running in PRODUCTION mode")

    # Create the window
    window = webview.create_window(
        "RI Tracker",
        url,
        js_api=api,
        width=400,
        height=630,
        resizable=False
    )

    # Start the application
    #webview.start(debug=debug)  # Optional: use 'cef' or 'qt' for better styling support
    webview.start(debug=debug)

