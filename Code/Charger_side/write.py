import serial
import select

# Create a serial connection
ser = serial.Serial('/dev/ttyACM0', 9600)  # Update baud rate if necessary
while True:
    user_input = input("Enter message to send: ")
    if len(user_input) > 0:
        ser.write((user_input+"\n").encode())
