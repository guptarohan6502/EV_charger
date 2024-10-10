
# EV_ui.py

import tkinter as tk
import socket
import threading
from collections import deque
from keypad import Keypad
from wisun_set_script import setup_wisun  # Import Wi-SUN setup function


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


class MainApp:
    def __init__(self, root, wisun_port, arduino_port):
        self.root = root
        self.root.geometry("600x400")
        self.root.title("EV Charger Wi-SUN Connection")

        self.wisun_port = wisun_port
        self.arduino_port = arduino_port

        # Create a socket object
        self.cli_socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cli_socks.connect((socket.gethostname(), self.wisun_port))  # Bind to the port
        print("EVscript: Connected to local server.")

        self.wisun_socket_q = deque()
        read_thread = threading.Thread(target=self.read_socket)
        read_thread.start()

        # Initially start with an empty frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True)

        # Create the initial frame
        self.show_initial_frame("Press '#' on the keypad to Connect")

        # Start keypad input monitoring
        self.keypad = Keypad(self.process_keypad_input)
        self.start_keypad_listener()

    def read_socket(self):
        while True:
            msg = self.cli_socks.recv(1024)
            if msg:
                self.wisun_socket_q.append(msg.decode().strip())

    def start_keypad_listener(self):
        """Run the keypad check loop in a separate thread."""
        keypad_thread = threading.Thread(target=self.keypad.check_keypad)
        keypad_thread.daemon = True  # Ensure it stops when the program exits
        keypad_thread.start()

    def process_keypad_input(self, char):
        """Handle the '#' input from the keypad to start Wi-SUN connection."""
        if char == '#':
            self.connect_to_wisun()

    def update_status(self, message):
        """Update the status label with the current message."""
        self.status_label.config(text=message)
        self.root.update()

    def connect_to_wisun(self):
        """Trigger the Wi-SUN connection setup."""
        self.show_loading_frame("Connecting to Wi-SUN...")

        # Run the Wi-SUN setup in a separate thread to avoid blocking the UI
        wisun_thread = threading.Thread(target=self.setup_wisun_and_update)
        wisun_thread.start()
        
    def show_initial_frame(self,msg):
        """Show the initial frame with 'Connect to Wi-SUN' button and status label."""
        self.clear_frame()

        self.initial_frame = tk.Frame(self.root)
        self.initial_frame.pack(expand=True)

        # Enter Input button to start Wi-SUN connection
        self.wisun_button = tk.Button(self.initial_frame, text="Connect to Wi-SUN", font=("Helvetica", 16))
        self.wisun_button.pack(pady=20)

        # Status label to prompt user to press '#'
        self.status_label = tk.Label(self.initial_frame, text= msg, font=("Helvetica", 10))
        self.status_label.pack(pady=20)

    def show_loading_frame(self, message):
        """Show a loading frame while Wi-SUN is being set up."""
        self.clear_frame()
        self.loading_frame = tk.Frame(self.root)
        self.loading_frame.pack(expand=True)

        self.loading_label = tk.Label(self.loading_frame, text=message, font=("Helvetica", 16))
        self.loading_label.pack(pady=100)

    def show_scanning_frame(self):
        """Show the frame for starting scanning after Wi-SUN setup."""
        self.clear_frame()
        self.scan_frame = tk.Frame(self.root)
        self.scan_frame.pack(expand=True)

        # Start Scanning button
        self.scan_button = tk.Button(self.scan_frame, text="Start Scanning", font=("Helvetica", 16))
        self.scan_button.pack(pady=20)

        # Status label to prompt user to press '#'
        self.scan_label = tk.Label(self.scan_frame, text="Press '#' on the keypad to start scanning", font=("Helvetica", 10))
        self.scan_label.pack(pady=20)
	
        
    def setup_wisun_and_update(self):
        """Setup Wi-SUN and update the UI based on success or failure."""
        #connected = setup_wisun(cli_socks=self.cli_socks, socket_q=self.wisun_socket_q)  # Call the setup function from wisun_set_script.py
        
        set_wisun_thread = ThreadWithReturnValue(target=setup_wisun, args = (self.cli_socks, self.wisun_socket_q,))
        set_wisun_thread.start()
        connected = set_wisun_thread.join(timeout=600)  # 10 minutes to setup Wi-SUN else BR not setup

        
        
        if connected:
            self.show_scanning_frame()  # Show the scanning frame when setup is successful
        else:
            self.show_initial_frame("Failed to connect Wisun \n Press '#' on the keypad to Connect")

    def clear_frame(self):
        """Clear all widgets from the main window."""
        for widget in self.root.winfo_children():
            widget.destroy()
