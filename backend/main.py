
import webview
import sqlite3
import time
import sys
from datetime import datetime

db_file = 'tracker.db'
DEBUG = True  # Set to False for production

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

class Api:
    def __init__(self):
        self.start_time = None
        self.current_project = None

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
    if len(sys.argv) > 1 and sys.argv[1] == '--dev':
        #global DEBUG
        DEBUG = True

    # Get the appropriate URL
    if DEBUG:
        url = "http://localhost:5173"
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
    webview.start(debug=debug)  # Optional: use 'cef' or 'qt' for better styling support

