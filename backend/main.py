import os
import webview
import sqlite3
import time
import sys
import requests
import json
from datetime import datetime, timezone



APP_NAME = "RI_Tracker"
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
                'https://remotintegrity-auth.vercel.app/api/v1/auth/login/employee',
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
                f'https://crm-amber-six.vercel.app/api/v1/employee/{employee_id}',
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
            #start_time = datetime.utcnow().isoformat() + 'Z'  # UTC time in ISO format
            #start_time = datetime.now(timezone.utc).isoformat()
            start_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

            #start_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

            # Optional: Ensure it ends with 'Z' if you want ISO 8601 compatibility
            # if not start_time.endswith('Z'):
            #     start_time = start_time.replace('+00:00', 'Z')


            session_data = {
                "employeeId": employee_id,
                "companyId": company_id,
                "startTime": start_time,
                "notes": "Session from RI Tracker APP v1.",
                "timezone": "America/New_York"
            }
            
            # Send request to create session
            response = requests.post(
                'https://tracker-beta-kohl.vercel.app/api/v1/sessions/',
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
    
    def update_session(self, active_time, idle_time=0, keyboard_rate=0, mouse_rate=0):
        """Update an existing session via API"""
        if not self.auth_token or not self.session_id:
            return {"success": False, "message": "Not authenticated or no active session"}
        
        try:
            # Create session update data
            #end_time = datetime.utcnow().isoformat() + 'Z'  # UTC time in ISO format
            #end_time = datetime.now(timezone.utc).isoformat()
            end_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            #end_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

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
                f'https://tracker-beta-kohl.vercel.app/api/v1/sessions/{self.session_id}',
                json=update_data,
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            )
            
            data = response.json()
            
            if data.get('success'):
                self.session_id = None
                return {"success": True, "data": data['data']}
            else:
                return {"success": False, "message": data.get('message', 'Failed to update session')}
        except Exception as e:
            print(f"Update session error: {e}")
            return {"success": False, "message": f"An error occurred: {str(e)}"}
    
    def start_timer(self, project_name):
        """Start the timer and create a new session"""
        self.start_time = time.time()
        self.current_project = project_name
        self.active_time = 0
        self.idle_time = 0
        
        # Create a new session
        result = self.create_session()
        return result

    def stop_timer(self):
        """Stop the timer and update the session"""
        if self.start_time:
            # Calculate duration
            duration = int(time.time() - self.start_time)
            self.active_time = duration
            
            # Store in local database
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with sqlite3.connect(db_file) as conn:
                conn.execute(
                    'INSERT INTO time_entries (project_name, timestamp, duration) VALUES (?, ?, ?)',
                    (self.current_project, timestamp, duration)
                )
            
            # Update the session
            result = self.update_session(active_time=duration)
            
            # Reset timer state
            self.start_time = None
            self.current_project = None
            
            return result
        
        return {"success": False, "message": "Timer not running"}

    def get_time_entries(self):
        with sqlite3.connect(db_file) as conn:
            c = conn.cursor()
            c.execute('SELECT project_name, timestamp, duration FROM time_entries ORDER BY id DESC LIMIT 10')
            return [{'project': row[0], 'timestamp': row[1], 'duration': row[2]} for row in c.fetchall()]

if __name__ == '__main__':
    init_db()
    api = Api()

    # Determine if we're in development or production mode
    DEBUG = True
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
        height=670,
        resizable=False
    )

    # Start the application
    #webview.start(debug=debug)  # Optional: use 'cef' or 'qt' for better styling support
    webview.start(debug=debug)

