
# run.py

import threading
import time
import send_to_BR  # Import the BR communication script
import send_to_AR
import EV_ui  # Import the UI script
import tkinter as tk  # Add tkinter import here for root window creation

# Create a class to store the result of threads
class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, timeout=None):
        threading.Thread.join(self, timeout)
        return self._return

# Define ports
port = 6010
arduino_port = port + 1
wisun_port = port

# Start the BR communication thread
sendBR_thread = threading.Thread(target=send_to_BR.sendBR, args=(port,))
sendBR_thread.start()

sendAR_thread = threading.Thread(target=send_to_AR.sendAR, args=(arduino_port,))
sendAR_thread.start()

# Adding a small delay to ensure BR communication is established before starting the UI
time.sleep(2)

# Initialize the Tkinter root window and start the EV UI thread
def start_ui():
    root = tk.Tk()  # Create the root window here
    app = EV_ui.MainApp(root,wisun_port,arduino_port)  # Pass the root window to the MainApp
    root.mainloop()  # Start the Tkinter main loop

EV_UI_thread = threading.Thread(target=start_ui)
EV_UI_thread.start()

# Optionally, you can join threads if you want the main program to wait for them.
# sendBR_thread.join()
# EV_UI_thread.join()
