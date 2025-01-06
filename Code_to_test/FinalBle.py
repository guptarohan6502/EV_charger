import tkinter as tk
import serial
import threading
import time
import socket
from collections import deque
import RPi.GPIO as GPIO

# User-defined imports
import BR_comms
import Pzem
import keypad

# Global variables for serial connection and socket port
Ard_ser = None
wisun_ser = None

Ard_ser = serial.Serial('/dev/ttyACM1', 9600)
if Ard_ser.is_open:
    print("Arduino serial is connected.")

wisun_ser = serial.Serial('/dev/ttyACM0', 9600)
if wisun_ser.is_open:
    print("Wi-SUN serial is connected.")


def read_serial():
    global serial_q

    while True:
        msg = cli_socks.recv(1024)
        serial_q.append(msg.decode().strip())
        # print("Received:", msg.decode().strip())


# Create a class to store the result
class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, timeout=None):
        threading.Thread.join(self, timeout)
        return self._return


# Function to update the status label
def update_status(message):
    status_label.config(text=message)


def click_button(btn):
    btn.invoke()


def stop_charge_keypad():
    return check_keypad()  # Call check_keypad and return its result


# Function to handle Wi-SUN connection setup
def setup_wisun():
    global serial_q

    read_string = ""

    try:
        # Send Wi-SUN join commands
        wisun_ser.write(b"wisun get wisun\n")
        wisun_ser.write(b"wisun join_fan11\n")
        if serial_q:
            read_string = serial_q.pop()

        while ("IPv6 address" not in str(read_string)) and ("wisun.border_router = fd12:3456" not in str(read_string)):
            if serial_q:
                read_string = serial_q.pop()
            else:
                continue
            print("\r", f"waiting For wisun to setup", end='\r')

        if ("IPv6 address" in str(read_string) or "wisun.border_router" in str(read_string)):
            wisun_ser.write(b"wisun udp_server 5001\n")
            time.sleep(1)
            wisun_ser.write(b"wisun udp_client fd12:3456::1 5005\n")
            time.sleep(1)
            wisun_ser.write(b"wisun get wisun\n")
            time.sleep(1)
            wisun_ser.write(b"wisun socket_list\n")
            time.sleep(1)
            return True

        else:
            print("I am here")
            return False

    except Exception as e:
        print("Here at exception")
        update_status("Wi-SUN Setup Error: " + str(e))
        return False


# Function to handle the scanning process
def scan_for_bikes():
    try:
        update_status("Scanning...")

        start_time = time.time()

        while True:
            if time.time() - start_time > 5:
                update_status("Scanning failed")
                break

            if Ard_ser.in_waiting > 0:
                line = Ard_ser.readline().decode('utf-8').strip()
                if "Scanning for devices..." in line:
                    update_status("Scanning...")

                elif "bikes are available to connect:" in line:
                    num_bikes = int(line.split()[0])
                    bike_details = []
                    for _ in range(num_bikes):
                        bike_name = Ard_ser.readline().decode('utf-8').strip()
                        bike_details.append(bike_name)

                    display_bike_options(bike_details)
                    break
    except Exception as e:
        update_status("Error: " + str(e))


# Function to send the "SCAN" command
def send_scan_command():
    try:
        if Ard_ser and Ard_ser.is_open:
            Ard_ser.flush()
            Ard_ser.write(b"SCAN\n")
            threading.Thread(target=scan_for_bikes).start()
        else:
            update_status("Serial port not open.")
    except Exception as e:
        update_status("Error: " + str(e))


def but_startcharge():
    for widget in window.winfo_children():
        widget.destroy()
    try:
        power_sensor = Pzem.PZEM()
    except:
        btn = tk.Button(window, text="Power meter is not Working", width=20, command=but_startcharge())
        btn.pack(pady=10)

    btn = tk.Button(window, text="Enter Amount", width=20, command=but_startcharge())
    btn.pack(pady=10)
    # Keypad interfacing with raspberry pi
    print('Amount you want to charge for: Press the amount and press #')

    keypad_input = keypad.keypad_take_inp()
    
    print(f"Amount you want to charge for: {keypad_input}")
    GPIO.cleanup()
    
    btn = tk.Button(window, text=f"Amount to charge: {keypad_input}", width=20, command=but_startcharge())
    btn.pack(pady=10)

    user_idTag = "Bike 1"

    print(f"Amount: {keypad_input} and VehicleidTag: {user_idTag}")
    idtag_str = f"{{'Amount': {keypad_input}, 'VehicleidTag' : '{user_idTag}', 'Time': {time.time()}, 'Chargerid': 1}}"
    
    costperunit = 7
    unit_1 = 36  # ideally 36000000
    
    Rfid_valid = True
    if Rfid_valid:
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        print(f"Total unit you get = {keypad_input / costperunit}")
        btn = tk.Button(window, text=f"Total Units= {keypad_input / costperunit:0.2f}\n Charging...", width=20, command=but_startcharge())
        btn.pack(pady=10)
        
        time.sleep(1)
        
        netunit = keypad_input / costperunit
        netenergy = netunit * unit_1
        GPIO.setup(4, GPIO.OUT)

        try:
            print("Checking readiness")
            if power_sensor.isReady():
                print(f"Charging started")
                GPIO.output(4, GPIO.HIGH)
                time.sleep(0.1)
                power = power_sensor.readPower()
                while power <= 0:
                    power = power_sensor.readPower()

                start = time.time()
                energy_cons = 0
                energy_cons = (power * (time.time() - start))
                print(f"power={power}")
                print('\n')
                while energy_cons < netenergy:
                    print("\r", f"units_cons = {energy_cons / unit_1}", end='\r')
                    energy_cons = (power * (time.time() - start))

                print(time.time() - start)
                print("Done")
                GPIO.output(4, GPIO.LOW)

        finally:
            power_sensor.close()
        
        but = tk.Button(window, text="Charging Done", width=20)
        but.pack(pady=10)
        
        setup_scan_screen()
    
    g = {
        "amount": keypad_input,
        "VehicleidTag": user_idTag
    }


# Function to display bike options
def display_bike_options(bike_details):
    for widget in window.winfo_children():
        widget.destroy()

    for bike in bike_details:
        btn = tk.Button(window, text=bike, width=20, command=but_startcharge())
        btn.pack(pady=10)

    back_btn = tk.Button(window, text="Back", command=setup_scan_screen)
    back_btn.pack(pady=20)

    # Wait for keypad use input for 10 secs else continue
    btn_thread = ThreadWithReturnValue(target=keypad.keypad_take_inp)
    btn_thread.start()
    keypad_input = btn_thread.join(timeout=1 / 6)
    if keypad_input:
        keypad_input = keypad.keyboard_input(click_button(btn))
    else:
        keypad.keyboard_input(click_button(back_btn))


# Function to set up the initial scan screen
def setup_scan_screen():
    for widget in window.winfo_children():
        widget.destroy()

    scan_button = tk.Button(window, text="Scan for Bikes", command=send_scan_command, width=20)
    scan_button.pack(pady=20)

    global status_label
    status_label = tk.Label(window, text="")
    status_label.pack(pady=20)

    keypad.keyboard_input(click_button(scan_button))


# Function to start the Wi-SUN connection process and then show the scan screen
def start_connection():
    global connect_button
    update_status("Connecting to Wi-SUN...")
      
    set_wisun_thread = ThreadWithReturnValue(target=setup_wisun)
    set_wisun_thread.start()
    wisun_setup = set_wisun_thread.join(timeout=600)  # 10 minutes to setup wisun else BR not setup
    
    if wisun_setup:
        print("Wisun Connection Successful")
        setup_scan_screen()
    else:
        print("Wisun Not connected")
        update_status("Failed to connect to Wi-SUN.")
        time.sleep(1)
        for widget in window.winfo_children():
            widget.destroy()
        connect_button.pack(pady=20)


# Create the main window
window = tk.Tk()
window.title("EV Charger")

monitor_BR_thread = threading.Thread(target=BR_comms.monitor_BR, args=(wisun_ser,))
monitor_BR_thread.start()

time.sleep(1)
serial_q = deque()

# Create a socket object
cli_socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cli_socks.connect((socket.gethostname(), 6000))  # Bind to the port
print("Connected to local server.")

read_thread = threading.Thread(target=read_serial)
read_thread.start()
time.sleep(1)

# Set up a button to initiate the Wi-SUN connection
connect_button = tk.Button(window, text="Connect to Wi-SUN", command=start_connection, width=20)
connect_button.pack(pady=20)

# Add a label for status updates
status_label = tk.Label(window, text="")
status_label.pack(pady=20)


# Start the Tkinter event loop
window.mainloop()
#keypad.keyboard_input(click_button(connect_button))
