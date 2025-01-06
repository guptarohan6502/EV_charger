
import threading
import time
import serial
import serial.tools.list_ports
import fnmatch  # For filtering port names
import send_to_BR  # Import the BR communication script
import send_to_AR  # Import the AR communication script
import EV_BLE  # Import the UI script
import tkinter as tk  # Add tkinter import here for root window creation

# Create a class to store the result of threads
class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, timeout=None):
        threading.Thread.join(self, timeout)
        return self._return

def is_arduino(port):
    """
    Function to check if the connected device is an Arduino.
    Sends a query and waits for a specific response.
    """
    try:
        ser = serial.Serial(port, 9600, timeout=1)  # Open serial port
        time.sleep(2)  # Give some time for the connection to establish

        if not ser.is_open:
            print(f"Port {port} is not open.")
            return False

        ser.reset_input_buffer()
        ser.reset_output_buffer()

        print(f"Checking Arduino on port {port}...")

        # Send the identification command
        ser.write(b'CHECK_ARDUINO\n')
        time.sleep(1)

        if ser.in_waiting > 0:  # Check if there's data available
            response = ser.readline().decode().strip()  # Read response
            if response == "ARDUINO_OK":
                print("Arduino detected!")
                ser.close()  # Close the port after checking
                print("Done")
                return True
            else:
                ser.close()
                print(f"Unexpected response: {response}")
        else:
            ser.close()
            print(f"No response from device on port {port}.")

    
        return False

    except (serial.SerialException, Exception) as e:
        print(f"Error checking port {port}: {e}")
        return False

def find_ports():
    """
    Function to find the Arduino and Wi-SUN device by scanning available serial ports.
    Filters to only check /dev/ttyACMx ports.
    """
    ports = serial.tools.list_ports.comports()
    arduino_port = None
    wisun_port = None

    print(f"Available ports: {ports}")

    # Filter only /dev/ttyACMx ports
    acm_ports = [port for port in ports if fnmatch.fnmatch(port.device, '/dev/ttyACM*')]

    if not acm_ports:
        print("No /dev/ttyACMx ports found.")
        return None, None
    print(f"Available ACM ports: {acm_ports}")	
    for port in acm_ports:
        if is_arduino(port.device):
            arduino_ser_port = port.device  # Save the Arduino port
        else:
            wisun_ser_port = port.device
            
      

    return arduino_ser_port, wisun_ser_port


# Initialize the Tkinter root window and start the EV UI thread
def start_ui():
    try:
        root = tk.Tk()  # Create the root window here
        app = EV_BLE.MainApp(root, wisun_port, arduino_port)  # Pass the root window to the MainApp
        root.mainloop()  # Start the Tkinter main loop
    except Exception as e:
      print(f"Waiting for GUI to become available: {e}")
      time.sleep(0.2) # Small delay, not needed but recommended
      
      
if __name__ == '__main__':
    time.sleep(5)
    # Detect the Arduino and Wi-SUN ports
    arduino_ser_port, wisun_ser_port = find_ports()

    if arduino_ser_port is None:
        print("Error: Could not detect both Arduino and Wi-SUN devices.")
        exit(1)

    print(f"Detected Arduino on port: {arduino_ser_port}")
    #print(f"Detected Wi-SUN on port: {wisun_ser_port}")

    # Define ports
    port = 7010
    arduino_port = port + 1
    wisun_port = port

    # Start the BR communication thread for Wi-SUN
    sendBR_thread = threading.Thread(target=send_to_BR.sendBR, args=(wisun_ser_port, wisun_port,))
    sendBR_thread.start()

    # Start the AR communication thread for Arduino
    sendAR_thread = threading.Thread(target=send_to_AR.sendAR, args=(arduino_ser_port, arduino_port,))
    sendAR_thread.start()

    # Adding a small delay to ensure BR communication is established before starting the UI
    time.sleep(2)



    EV_BLE_thread = threading.Thread(target=start_ui)
    EV_BLE_thread.start()

