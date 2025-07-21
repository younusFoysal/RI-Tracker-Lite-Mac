
import webview
import sqlite3
import time
import sys
import requests
import json
from datetime import datetime

db_file = 'tracker.db'

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

    def login(self, email, password):
        """Login to the remote API and store the token"""
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
                self.save_auth_data(token, user_data)
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

    def start_timer(self, project_name):
        self.start_time = time.time()
        self.current_project = project_name

    def stop_timer(self):
        if self.start_time:
            duration = int(time.time() - self.start_time)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with sqlite3.connect(db_file) as conn:
                conn.execute(
                    'INSERT INTO time_entries (project_name, timestamp, duration) VALUES (?, ?, ?)',
                    (self.current_project, timestamp, duration)
                )
            self.start_time = None
            self.current_project = None

    def get_time_entries(self):
        with sqlite3.connect(db_file) as conn:
            c = conn.cursor()
            c.execute('SELECT project_name, timestamp, duration FROM time_entries ORDER BY id DESC LIMIT 10')
            return [{'project': row[0], 'timestamp': row[1], 'duration': row[2]} for row in c.fetchall()]

if __name__ == '__main__':
    init_db()
    api = Api()

    # Determine if we're in development or production mode
    DEBUG = False
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

