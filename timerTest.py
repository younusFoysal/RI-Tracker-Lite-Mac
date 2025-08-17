import sys
import time
import threading
from Cocoa import (
    NSStatusBar,
    NSMenu,
    NSMenuItem,
    NSApplication,
    NSObject,
    NSVariableStatusItemLength,
)
from PyObjCTools.AppHelper import runEventLoop
import webview  # pywebview

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        print("✅ applicationDidFinishLaunching fired")

        # Timer state
        self.running = False
        self.seconds = 0

        # Create status bar item
        self.statusItem = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        self.statusItem.button().setTitle_("⏱00:00")

        # Create dropdown menu
        menu = NSMenu.alloc().init()
        open_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Open App", "openApp:", "")
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Quit", "quitApp:", "")
        menu.addItem_(open_item)
        menu.addItem_(quit_item)
        self.statusItem.setMenu_(menu)

    def startTimer(self):
        if not getattr(self, "running", False):
            self.running = True
            threading.Thread(target=self.update_timer, daemon=True).start()

    def stopTimer(self):
        self.running = False

    def update_timer(self):
        while self.running:
            time.sleep(1)
            self.seconds += 1
            mins = (self.seconds % 3600) // 60
            secs = self.seconds % 60
            title = f"⏱{mins:02}:{secs:02}"
            self.statusItem.button().setTitle_(title)

    def openApp_(self, sender):
        if webview.windows:
            webview.windows[0].show()

    def quitApp_(self, sender):
        sys.exit(0)


def start_app():
    # Launch pywebview in a thread
    def launch_window():
        webview.create_window("Timer App", "http://localhost:3000")  # your React frontend
    threading.Thread(target=launch_window, daemon=True).start()

    # Cocoa app loop
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)

    # Start the timer AFTER delegate is created
    delegate.startTimer()

    runEventLoop()


if __name__ == "__main__":
    start_app()
