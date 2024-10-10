import tkinter as tk
from keypad import start_keypad

def show_input(entry_text):
    """Show the submitted input for 2 seconds"""
    result_label.config(text=f"Entered Input: {entry_text}")
    root.after(2000, lambda: result_label.config(text=""))  # Clear the label after 2 seconds

def enter_input():
    """Function to initiate the keypad input"""
    start_keypad(entry, show_input)  # Call keypad function and pass the callback

# Create the main Tkinter UI
root = tk.Tk()
root.geometry("600x400")
root.title("Main Window")


# Create a button to enter input
enter_button = tk.Button(root, text="Enter Input", command=enter_input, font=("Helvetica", 16))
enter_button.pack(pady=10)

# Create a label to display the result
result_label = tk.Label(root, text="", font=("Helvetica", 16))
result_label.pack(pady=10)

root.mainloop()
