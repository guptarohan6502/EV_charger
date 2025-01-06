import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

def test_rfid():
    reader = SimpleMFRC522()
    try:
        print("Scan your RFID tag...")
        id, text = reader.read()
        print(f"RFID ID: {id}")
        print(f"RFID Text: {text}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    test_rfid()

