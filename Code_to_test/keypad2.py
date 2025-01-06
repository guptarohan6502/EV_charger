
import RPi.GPIO as GPIO
import time

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

# Track when a key is pressed and released
key_pressed = False

def readLine(line, characters):
    GPIO.output(line, GPIO.HIGH)

    # Check each column for a press, but register only if no key was pressed before
    if GPIO.input(C1) == 1 and not key_pressed:
        print(characters[0])
    elif GPIO.input(C2) == 1 and not key_pressed:
        print(characters[1])
    elif GPIO.input(C3) == 1 and not key_pressed:
        print(characters[2])
    elif GPIO.input(C4) == 1 and not key_pressed:
        print(characters[3])

    GPIO.output(line, GPIO.LOW)

try:
    while True:
        # Scan each line (row) of the keypad
        readLine(L1, ["1", "2", "3", "A"])
        readLine(L2, ["4", "5", "6", "B"])
        readLine(L3, ["7", "8", "9", "C"])
        readLine(L4, ["*", "0", "#", "D"])

  

        # Adjust the delay for stable reading
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nApplication stopped!")
    GPIO.cleanup()
