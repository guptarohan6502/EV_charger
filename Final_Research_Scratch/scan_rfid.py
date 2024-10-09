
import warnings
import threading
import time
import tkinter as tk
from tkinter import messagebox
from collections import deque
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

warnings.filterwarnings("ignore")

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Global variables
serial_q = deque()
rfid_number = None
scan_thread = None
timeout_timer = None

# Initialize RFID reader
reader = SimpleMFRC522()

# def setup_ui():
    # """
    # Initialize the main Tkinter window and display the initial screen.
    # """
    # global root
    # root = tk.Tk()
    # root.title("RFID Scanner")
    # root.geometry("600x400")
    # show_initial_screen()
    # root.mainloop()

def show_initial_screen(root):
    """
    Display the initial screen with a button to start RFID scanning.
    """
    
    clear_window(root)
    
    title_label = tk.Label(root, text="Welcome to RFID Scanner", font=("Helvetica", 24))
    title_label.pack(pady=50)
    
    scan_button = tk.Button(root, text="Scan RFID", font=("Helvetica", 18), command=show_scan_screen(root))
    scan_button.pack(pady=20)

def show_scan_screen(root):
    """
    Display the scan screen with instructions and start the RFID scanning process.
    """
    
    clear_window(root)
    
    instruction_label = tk.Label(root, text="Please scan your RFID near the scanner.", font=("Helvetica", 16))
    instruction_label.pack(pady=20)
    
    # Simple ASCII diagram
    diagram = """
      +---------------------+
      |       [ RFID ]      |
      |      Scanner        |
      +---------------------+
             ||
             ||
             \/
    Bring your RFID card near the scanner.
    """
    diagram_label = tk.Label(root, text=diagram, font=("Courier", 12), justify="left")
    diagram_label.pack(pady=10)
    
    cancel_button = tk.Button(root, text="Cancel", font=("Helvetica", 14), command=show_initial_screen(root))
    cancel_button.pack(pady=20)
    
    # Start RFID scanning in a separate thread
    start_rfid_scan(root)

def start_rfid_scan(root):
    """
    Start the RFID scanning thread and set a 30-second timeout.
    """
    global scan_thread, timeout_timer
    scan_thread = threading.Thread(target=scan_rfid,args=(root,), daemon=True)
    scan_thread.start()
    
    # Start a timer for 30 seconds
    timeout_timer = threading.Timer(30.0, on_timeout(root))
    timeout_timer.start()

def scan_rfid(root):
    """
    Function to handle RFID scanning. Runs in a separate thread.
    """
    global rfid_number
    try:
        print("Charger: Waiting for RFID scan...")
        id, text = reader.read()
        rfid_number = text.strip()
        print(f"Charger: RFID Scanned: {rfid_number}")
        # Stop the timeout timer
        timeout_timer.cancel()
        # Update the UI with the scanned RFID
        #root.after(0, show_result, rfid_number)
    except Exception as e:
        print(f"Charger: Error during RFID scan: {e}")
        root.after(0, show_error, "Error during RFID scan.")

def on_timeout(root):
    """
    Handle the timeout scenario when no RFID is scanned within 30 seconds.
    """
    print("Charger: RFID scan timed out.")
    root.after(0, show_timeout)

# def show_result(root,rfid):
    # """
    # Display the scanned RFID number on the UI.
    # """
    # clear_window(root)
    
    # result_label = tk.Label(root, text=f"RFID Scanned Successfully!\nRFID Number: {rfid}", font=("Helvetica", 16))
    # result_label.pack(pady=100)
    
    # ok_button = tk.Button(root, text="OK", font=("Helvetica", 14), command=show_initial_screen(root))
    # ok_button.pack(pady=20)

def show_timeout(root):
    """
    Inform the user that the RFID scan timed out and return to the initial screen.
    """
    clear_window(root)
    
    timeout_label = tk.Label(root, text="RFID scan timed out.\nPlease try again.", font=("Helvetica", 16))
    timeout_label.pack(pady=100)
    
    retry_button = tk.Button(root, text="Retry", font=("Helvetica", 14), command=show_initial_screen(root))
    retry_button.pack(pady=20)

def show_error(message):
    """
    Display an error message on the UI.
    """
    clear_window()
    
    error_label = tk.Label(root, text=message, font=("Helvetica", 16), fg="red")
    error_label.pack(pady=100)
    
    retry_button = tk.Button(root, text="Retry", font=("Helvetica", 14), command=show_initial_screen(root))
    retry_button.pack(pady=20)

def clear_window(root):
    """
    Clear all widgets from the main window.
    """
    for widget in root.winfo_children():
        widget.destroy()

def on_closing():
    """
    Handle the closing of the Tkinter window gracefully.
    """
    try:
        GPIO.cleanup()
    except:
        pass
    root.destroy()

if __name__ == "__main__":
    try:
        setup_ui()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Program terminated by user.")
