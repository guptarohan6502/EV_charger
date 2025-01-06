
import threading
import time
from collections import deque

def disconnect_from_arduino(arduino_socks):
    """
    Sends a 'DISCONNECT' command to the Arduino via the established socket connection.
    """
    try:
        if arduino_socks:
            arduino_socks.send(b"DISCONNECT\n")
            print("ARscript: Sent DISCONNECT to Arduino.")
        else:
            print("Error: Arduino socket connection not available.")
    except Exception as e:
        print(f"Error in disconnect_from_arduino: {e}")

def read_central_connection(arduino_socket_q):
    """
    Reads lines from the arduino_socket_q until it finds one containing
    'Connected to central:'. Extracts and returns the BLE address.
    """
    while True:
        if arduino_socket_q:
            # Log the queue contents for debugging
            print(f"ARscript: Queue contents before dequeuing: {list(arduino_socket_q)}")

            # Get the next line
            line = arduino_socket_q.popleft().strip()
            print(f"ARscript: Processing line: {line}")

            # Check if the line contains the expected message
            if "Connected to central:" in line:
                try:
                    # Extract the BLE address
                    address = line.split("Connected to central:")[1].strip()
                    print(f"ARscript: Found central address: {address}")
                    return address
                except IndexError:
                    print("ARscript: Error parsing 'Connected to central:' line.")
                    return None
        else:
            # No data in the queue, wait briefly
            time.sleep(0.01)

    print("ARscript: Timed out waiting for 'Connected to central:' line.")
    return None

def app_communication(arduino_socket_q, arduino_socks, stop_event=None, timeout=30):
    """
    Handles communication between the application and Arduino over sockets.
    """
    print("AR:Inside app comms func")
    pin_code = None
    amount = None
    start_time = time.time()

    try:
        # Wait for "Start" from Arduino
        while time.time() - start_time < timeout:
            if stop_event and stop_event.is_set():
                print("AR: Communication stopped by external event.")
                return

            if arduino_socket_q:
                line = arduino_socket_q.popleft().strip()
                line = line.split("APP:")[1].strip()
                print(f"AR: Received line: {line}")

                if line == "Start":
                    print("AR: Received 'Start' from Arduino.")
                    if arduino_socks:
                        arduino_socks.send(b"ANDROID: Please Enter Amount\n")
                    else:
                        print("Error: Arduino socket not available.")
                    break
            else:
                time.sleep(0.1)
        else:
            print("AR: Timed out waiting for 'Start'.")
            return
        
        
        # Wait for Amount
        start_time = time.time()
        while time.time() - start_time < timeout:
            if arduino_socket_q:
                line = arduino_socket_q.popleft().strip()
                line = line.split("APP:")[1].strip()

                print(f"AR: Received line: {line}")

                if line.isdigit():
                    amount = line
                    print(f"AR: Amount received: {amount}")
                    if arduino_socks:
                        arduino_socks.send(b"ANDROID: Please Enter PIN\n")
                    break
            else:
                time.sleep(0.1)
        else:
            print("AR: Timed out waiting for Amount.")
            return

        # Wait for PIN
        start_time = time.time()
        while time.time() - start_time < timeout:
            if arduino_socket_q:
                line = arduino_socket_q.popleft().strip()
                line = line.split("APP:")[1].strip()

                print(f"AR: Received line: {line}")

                if line.isdigit():
                    pin_code = line
                    print(f"AR: PIN received: {pin_code}")
                    break
            else:
                time.sleep(0.1)
        else:
            print("AR: Timed out waiting for PIN.")
            return pin_code, amount

        print(f"AR: Communication complete. PIN={pin_code}, Amount={amount}")
        return pin_code, amount

    except Exception as e:
        print(f"AR: Error in app_communication: {e}")
