import tkinter as tk
import threading
import subprocess
import sys
import os
import time

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x400")
        self.root.title("Main Application")

        # Frame for the main screen
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True)

        # Enter Input button
        self.input_button = tk.Button(self.main_frame, text="Enter Input", font=("Helvetica", 16), command=self.open_keypad)
        self.input_button.pack(pady=20)

        # Label to display the input
        self.display_label = tk.Label(root, text="", font=("Helvetica", 16))

    def open_keypad(self):
        # Hide the main frame
        self.main_frame.pack_forget()
        # Start keypad in a separate thread
        threading.Thread(target=self.launch_keypad, daemon=True).start()

    def launch_keypad(self):
        # Determine the path to keypad.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        keypad_path = os.path.join(script_dir, 'keypad2.py')

        # Launch keypad.py as a subprocess and capture its output
        process = subprocess.Popen([sys.executable, keypad_path],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)

        stdout, stderr = process.communicate()

        if stderr:
            print(f"Error from keypad.py: {stderr}")

        # Extract the submitted input from stdout
        for line in stdout.splitlines():
            if line.startswith("Submitted Input:"):
                input_text = line.split("Submitted Input:")[1].strip()
                # Update the UI in the main thread
                self.root.after(0, lambda: self.show_input(input_text))
                break
        else:
            # If no input was submitted, show the main frame again
            self.root.after(0, self.show_main_frame)

    def show_input(self, input_text):
        # Display the input
        self.display_label.config(text=f"Input: {input_text}")
        self.display_label.pack(pady=20)
        # After 2 seconds, clear the input and show the main frame
        self.root.after(2000, lambda: self.reset_ui())

    def reset_ui(self):
        # Hide the display label
        self.display_label.pack_forget()
        # Show the main frame again
        self.show_main_frame()

    def show_main_frame(self):
        self.main_frame.pack(expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
