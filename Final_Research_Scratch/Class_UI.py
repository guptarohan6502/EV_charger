import tkinter as tk

import time



from keypad import KeypadUI  # Import the KeypadUI class from keypad.py

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x400")
        self.root.title("Main Application")

        # Frame for the main screen
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True)

        # Enter Input button
        self.input_button = tk.Button(self.main_frame, text="Enter Input", font=("Helvetica", 16), command=self.show_keypad)
        self.input_button.pack(pady=20)

        
        # Label to display the input
        self.display_label = tk.Label(root, text="", font=("Helvetica", 16))
        self.display_label.pack(pady=20)
        
        
        
        
        self.keypad = KeypadUI(self.root, self.process_input)


    

    def show_keypad(self):
        self.main_frame.pack_forget()  # Hide the main frame
        self.keypad.show()  # Show the keypad

    def process_input(self, input_text):
        # Display the input received from the keypad
        self.display_label.config(text=f"Input: {input_text}")
        self.root.after(2000, self.reset_ui)  # Reset UI after 2 seconds

    def reset_ui(self):
        self.display_label.config(text="")  # Clear the display
        self.keypad.hide()  # Hide the keypad
        self.main_frame.pack(expand=True)  # Show the main frame again

        
   
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
