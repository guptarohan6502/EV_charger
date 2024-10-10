
import RPi.GPIO as GPIO
import time
import tkinter as tk

# Define pins for rows and columns
L1 = 5
L2 = 6
L3 = 13
L4 = 19

C1 = 12
C2 = 16
C3 = 20
C4 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)

GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

key_pressed = False  # Track keypress state

class KeypadUI:
    def __init__(self, master, on_submit):
        self.master = master
        self.on_submit = on_submit
        self.keypad_frame = tk.Frame(master)
        self.create_keypad()

    def create_keypad(self):
        self.entry = tk.Entry(self.keypad_frame, width=20, font=("Helvetica", 16))
        self.entry.pack(pady=20)

        label = tk.Label(self.keypad_frame, text="Enter input via keypad", font=("Helvetica", 16))
        label.pack(pady=10)

        # Create keypad buttons layout
        buttons = [
            ["1", "2", "3", "A"],
            ["4", "5", "6", "B"],
            ["7", "8", "9", "C"],
            ["*", "0", "#", "D"]
        ]

        for row in buttons:
            button_row = tk.Frame(self.keypad_frame)
            button_row.pack()
            for char in row:
                btn = tk.Button(button_row, text=char, font=("Helvetica", 16), command=lambda c=char: self.handle_keypress(c))
                btn.pack(side=tk.LEFT)

        self.keypad_frame.pack()

    def handle_keypress(self, char):
        current_text = self.entry.get()
        if char == '#':
            print(f"Submitted Input: {current_text}")
            self.on_submit(current_text)
            self.entry.delete(0, tk.END)
            self.keypad_frame.pack_forget()  # Hide the keypad
        elif char == 'C':
            self.entry.delete(0, tk.END)
        else:
            self.entry.insert(tk.END, char)

    def show(self):
        self.keypad_frame.pack()  # Show the keypad frame

    def hide(self):
        self.keypad_frame.pack_forget()  # Hide the keypad frame

if __name__ == "__main__":
    GPIO.cleanup()
