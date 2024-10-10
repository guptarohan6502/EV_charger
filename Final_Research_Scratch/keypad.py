
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
        self.root = tk.Frame(master)
        
        # Create an entry widget to display input
        self.entry = tk.Entry(self.root, width=20, font=("Helvetica", 16))
        self.entry.pack(pady=20)
    
        # Create a label for instructions
        label = tk.Label(self.root, text="Enter input via keypad", font=("Helvetica", 16))
        label.pack(pady=10)
    
        # Start the update loop
        #self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        #self.root.mainloop()
        
        buttons = [
            ["1", "2", "3", "A"],
            ["4", "5", "6", "B"],
            ["7", "8", "9", "C"],
            ["*", "0", "#", "D"]
        ]

        for row in buttons:
            button_row = tk.Frame(self.root)
            button_row.pack()
            for char in row:
                btn = tk.Button(button_row, text=char, font=("Helvetica", 16), command=lambda c=char: self.handle_buttonkey(c))
                btn.pack(side=tk.LEFT)

        self.root.pack()
       
        self.update()

    def handle_buttonkey(self, char):
        current_text = self.entry.get()
        if char == '#':
            print(f"Submitted Input: {current_text}")
            self.on_submit(current_text)
            self.entry.delete(0, tk.END)
            self.root.pack_forget()  # Hide the keypad
        elif char == 'C':
            self.entry.delete(0, tk.END)
        else:
            self.entry.insert(tk.END, char)
    
    def readLine(self, line, characters):
        global key_pressed
        GPIO.output(line, GPIO.HIGH)
    
        if GPIO.input(C1) == 1 and not key_pressed:
            key_pressed = True
            self.handle_keypress(characters[0])
        elif GPIO.input(C2) == 1 and not key_pressed:
            key_pressed = True
            self.handle_keypress(characters[1])
        elif GPIO.input(C3) == 1 and not key_pressed:
            key_pressed = True
            self.handle_keypress(characters[2])
        elif GPIO.input(C4) == 1 and not key_pressed:
            key_pressed = True
            self.handle_keypress(characters[3])
    
        GPIO.output(line, GPIO.LOW)
    
    def handle_keypress(self, char):
        """Handle the keypress events for displaying and controlling the input"""
        current_text = self.entry.get()
    
        if char == '#':
            print(f"Submitted Input: {current_text}")
            self.on_submit(current_text)
            self.entry.delete(0, tk.END)
            self.root.pack_forget() 
        elif char == 'C':
            self.entry.delete(0, tk.END)
        else:
            self.entry.insert(tk.END, char)
    
    def check_keypad(self):
        """Check keypad for input"""
        global key_pressed
        self.readLine(L1, ["1", "2", "3", "A"])
        self.readLine(L2, ["4", "5", "6", "B"])
        self.readLine(L3, ["7", "8", "9", "C"])
        self.readLine(L4, ["*", "0", "#", "D"])
    
        # Delay to avoid continuous keypress detection
        time.sleep(0.08)
        key_pressed = False  # Reset key press state
    
        
    def show(self):
        self.root.pack()  # Show the keypad frame

    def hide(self):
		GPIO.cleanup()
        self.root.pack_forget()  # Hide the keypad frame

if __name__ == "__main__":
    def on_submit(input_text):
        print(f"Input received: {input_text}")
    
    KeypadUI(on_submit)
