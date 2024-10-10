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


def readLine(line, characters, entry):
    global key_pressed
    GPIO.output(line, GPIO.HIGH)

    if GPIO.input(C1) == 1 and not key_pressed:
        key_pressed = True
        handle_keypress(characters[0], entry)
    elif GPIO.input(C2) == 1 and not key_pressed:
        key_pressed = True
        handle_keypress(characters[1], entry)
    elif GPIO.input(C3) == 1 and not key_pressed:
        key_pressed = True
        handle_keypress(characters[2], entry)
    elif GPIO.input(C4) == 1 and not key_pressed:
        key_pressed = True
        handle_keypress(characters[3], entry)

    GPIO.output(line, GPIO.LOW)


def handle_keypress(char, entry):
    """Handle the keypress events for displaying and controlling the input"""
    current_text = entry.get()

    if char == '#':
        print(f"Submitted Input: {current_text}")
        entry.delete(0, tk.END)
        return current_text  # Return the entered input
    elif char == 'C':
        entry.delete(0, tk.END)
    else:
        entry.insert(tk.END, char)


def check_keypad(entry):
    """Check keypad for input"""
    global key_pressed
    readLine(L1, ["1", "2", "3", "A"], entry)
    readLine(L2, ["4", "5", "6", "B"], entry)
    readLine(L3, ["7", "8", "9", "C"], entry)
    readLine(L4, ["*", "0", "#", "D"], entry)

    # Delay to avoid continuous keypress detection
    time.sleep(0.08)
    key_pressed = False  # Reset key press state


def start_keypad(entry, display_callback):
    """Start the keypad interaction"""
    entry.pack_forget()  # Hide the entry widget temporarily

    # Create a keypad frame
    keypad_frame = tk.Frame()
    keypad_frame.pack(pady=20)

    # Create buttons for the keypad
    buttons = [
        ["1", "2", "3", "A"],
        ["4", "5", "6", "B"],
        ["7", "8", "9", "C"],
        ["*", "0", "#", "D"]
    ]

    for row in buttons:
        row_frame = tk.Frame(keypad_frame)
        row_frame.pack()
        for char in row:
            btn = tk.Button(row_frame, text=char, width=5, height=2,
                            command=lambda c=char: handle_keypress(c, entry) if c != '#' else display_callback(entry.get()))
            btn.pack(side=tk.LEFT)

    # Check keypad input
    def update():
        check_keypad(entry)
        keypad_frame.after(100, update)

    keypad_frame.after(100, update)
