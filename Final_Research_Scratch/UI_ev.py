import warnings
import threading
import socket
import time
import tkinter as tk
from collections import deque

warnings.filterwarnings("ignore")

import Charger_script

Emergency_vehicle_discovered = False

def Emergency_status():
    global Emergency_vehicle_discovered
    time.sleep(10)
    
    Emergency_vehicle_discovered = False
    return 1

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

def read_Ard_serial():
    global Ard_serial_q
    global Ard_socks
    global cli_socks
    
    global Emergency_vehicle_discovered
    
    while True:
        msg = Ard_socks.recv(1024).decode().strip()

        # Condition 1: Check if it is an emergency message
        if "Emergency:" in msg:
            #print("EVscript: Emergency vehicle discvered")
            if Emergency_vehicle_discovered == False:
                print("EVscript: Emergency vehicle discvered")
                cli_socks.send(("wisun socket_write 4 \"" + str((str(msg) + str(" Near Node 1")) + "\"\n")).encode())
                Emergency_vehicle_status_thread = threading.Thread(target=Emergency_status)
                Emergency_vehicle_discovered = True
                Emergency_vehicle_status_thread.start()

        # Condition 2: Check if it is an EV_Bike message
        elif "EV_Bike:" in msg:
            clean_msg = msg.replace("EV_Bike: ", "")
            Ard_serial_q.append(clean_msg)
            print(clean_msg)

        # Condition 3: If anything else, just ignore it
        else:
            pass

def read_socket():
    global socket_q
    global cli_socks

    while True:
        msg = cli_socks.recv(1024)
        if msg:
            socket_q.append(msg.decode().strip())

# Function to update the status label
def update_status(message):
    global status_label
    status_label.config(text=message)

# Function to handle Wi-SUN connection setup
def setup_wisun():
    global socket_q
    global cli_socks

    read_string = ""

    try:
        # Send Wi-SUN join commands through the socket
        time.sleep(0.25)
        cli_socks.send(b"wisun get wisun\n")
        time.sleep(0.25)
        cli_socks.send(b"wisun join_fan11\n")
        time.sleep(0.5)
        print("EVscript: done")
        if socket_q:
            read_string = socket_q.pop()

        while "IPv6 address" not in str(read_string) and "wisun.border_router = fd12:3456" not in str(read_string):
            if socket_q:
                read_string = socket_q.pop()
            else:
                continue
            print("\r", "waiting For wisun to setup", end='\r')

        if "IPv6 address" in str(read_string) or "wisun.border_router" in str(read_string):
            cli_socks.send(b"wisun udp_server 5001\n")
            time.sleep(1)
            cli_socks.send(b"wisun udp_client fd12:3456::1 5005\n")
            time.sleep(1)
            cli_socks.send(b"wisun get wisun\n")
            time.sleep(1)
            cli_socks.send(b"wisun socket_list\n")
            time.sleep(1)
            return True
        else:
            print("I am here")
            return False

    except Exception as e:
        print("Here at exception")
        print(e)
        update_status("Wi-SUN Setup Error")
        return False

def get_amount(bike):
    global window, status_label

    # Clear existing widgets in the window (but keep the status_label intact)
    for widget in window.winfo_children():
        if widget != status_label:  # Preserve the status label for updating later
            widget.destroy()

    amount_label = tk.Label(window, text="Enter amount (in integer):")
    amount_label.pack(pady=10)

    amount_entry = tk.Entry(window)
    amount_entry.pack(pady=5)

    error_label = tk.Label(window, text="", fg="red")
    error_label.pack()

    def submit_amount():
        try:
            amount = int(amount_entry.get())
            if amount < 0:  # Optional: Check for non-negative amount
                raise ValueError("Amount must be a positive integer.")
            # Proceed to charging with the valid amount
            but_startcharge(amount, bike)  # Call but_startcharge with the amount
        except ValueError:
            error_label.config(text="Invalid input. Please enter a positive integer.")

    submit_button = tk.Button(window, text="Submit", command=submit_amount)
    submit_button.pack(pady=10)

    window.update()  # Update the UI to show the amount entry screen

def check_rfid_valid(idtag_str):
    global start_time
    print(f"EVscript: Input give Validation started")
    print(f"EVscript: data being sent")
    global socket_q
    global cli_socks
    
    read_string = ""
    cli_socks.send(("wisun socket_write 4 \"" + idtag_str + "\"\n").encode())
    print("EVscript: wisun socket_write 4 \"" + idtag_str + "\"\n")
    
    if socket_q:
        read_string = socket_q.popleft().strip()
        print(f"read_string:{read_string}")
    
    while "valid" not in str(read_string):
        if socket_q:
            read_string = socket_q.popleft().strip()
            print(f"read_string:{read_string}")
        else:
            continue
        print("\r", f"Charger: waiting For Id validation", end='\r')
    print(f"Charger: Validation done")

    if "valid_yes" in str(read_string):
        return True
    elif "valid_not" in str(read_string):
        return False
    elif "valid_insuff" in str(read_string):
        return "Low balance"
    elif "valid_error" in str(read_string):
        return "Onem2m Not responding at the Moment"


# Charging function to simulate charging for 10 seconds
def charging(amount):
    global window
    
    
    """
    Error Codes:
    1. Charging Completed Successfully
    2. Power meter not working
    3. Insufficient Balance
    4. Invalid ID
    5. Any other error
    """ 
    
    print(f"Amount: {amount}")
    idtag_str = f"{{'Amount': {amount}, 'VehicleidTag': '12345678', 'Time': {time.time()}, 'Chargerid': 'EV-L001-03'}}"
    try:
        RFID_thread = ThreadWithReturnValue(target = check_rfid_valid, args=(idtag_str,))
        RFID_thread.start()
        Rfid_valid = RFID_thread.join(timeout = 60) # 1 minute to verify RFID
            
        print(Rfid_valid)
        time.sleep(2)
        charge_status = Charger_script.Charger(Rfid_valid,amount)
        print(charge_status)
        return charge_status
    except Exception as e:
        print(f"Error in charging: {e}")
        return 0  # Charging failed


def but_startcharge(amount,bike):
    global Ard_serial_q, Ard_socks, window, status_label
    global bike_details

    print(f"EVscript: Amount to charge for is: {amount}")
    if amount is None:
        update_status("EVscript: Error: Invalid amount. Please try again.")
        return

    # Update the UI to show charging screen
    for widget in window.winfo_children():
        widget.destroy()

    status_label = tk.Label(window, text="Charging in progress...")
    status_label.pack(pady=20)
    window.update()

    # Perform the background steps
    try:
        # Find the index of the bike in the bike details list (1-based indexing)
        index = bike_details.index(bike) + 1 if bike and bike_details else 0  # Add proper handling

        # Write the Arduino indexing to the Arduino socket
        Ard_socks.send(str(index).encode())

        time.sleep(2)
        update_status("Charging in progress..")
        window.update()

        # Read two lines from the Arduino serial queue (peripheral name and address)
        if len(Ard_serial_q) >= 2:
            peripheral_name = Ard_serial_q.popleft().strip()
            peripheral_address = Ard_serial_q.popleft().strip()

            # Print peripheral details for reference
            print(f"EV_script: Peripheral Name: {peripheral_name}")
            print(f"EV_script: Peripheral Address: {peripheral_address}")

            # Call the charging function
            charging_status = charging(amount)

            # Handle the post-charging process
            if charging_status == 1:
                Ard_socks.send(b"DISCONNECT\n")
                update_status("Charging completed")
            else:
                Ard_socks.send(b"DISCONNECT\n")
                update_status("Error: Charging failed")

            # After showing the status, return to the scan screen
            window.after(2000, setup_scan_screen)
        else:
            Ard_socks.send(str("DISCONNECT").encode())  # In case Arduino Bluetooth is connected
            print("EV_script: Error: Not enough data in the queue to read peripheral details.")
            update_status("Error: Could not retrieve peripheral details.")
            window.after(2000, setup_scan_screen)

    except Exception as e:
        Ard_socks.send(str("DISCONNECT").encode())  # In case Arduino Bluetooth is connected
        print(f"EV_script: Error in but_startcharge: {e}")
        update_status(f"Error: {e}")
        window.after(2000, setup_scan_screen)





# Function to display bike options
def display_bike_options():
    global window, status_label
    global bike_details
    

    print("evbIKE: FINALLY")

    # Clear previous widgets except the status label
    for widget in window.winfo_children():
        if widget != status_label:
            widget.destroy()

    # Display bike buttons
    for bike in bike_details:
        btn = tk.Button(window, text=bike, width=20, command=lambda b=bike: get_amount(b))
        btn.pack(pady=10)

    # Back button to return to the previous screen
    back_btn = tk.Button(window, text="Back", command=setup_scan_screen)
    back_btn.pack(pady=20)


# Function to handle the scanning process
def scan_for_bikes():
    global Ard_serial_q
    global bike, bike_details
    try:
        update_status("Scanning...")

        start_time = time.time()

        while True:
            if time.time() - start_time > 5:
                update_status("Scanning failed")
                break

            if Ard_serial_q:
                line = Ard_serial_q.popleft().strip()
                print("line: " + line)

                if "Scanning for devices..." in line:
                    update_status("Scanning...")

                elif "Bikes are available to connect:" in line:
                    time.sleep(1)
                    if Ard_serial_q:
                        line = Ard_serial_q.popleft().strip()
                        print("line: " + line)
                        num_bikes = int(line.split()[0])
                        print("EV_Script: Number of bikes: ", num_bikes)
                        bike_details = []

                        for _ in range(num_bikes):
                            if Ard_serial_q:
                                bike_name = Ard_serial_q.popleft().strip()
                                bike_details.append(bike_name)

                        display_bike_options()
                        break
    except Exception as e:
        update_status("Error: ")
        print(e)




# Function to send the "SCAN" command
def send_scan_command():
    global Ard_socks
    try:
        if Ard_socks:
            Ard_socks.send(b"SCAN\n")
            threading.Thread(target=scan_for_bikes).start()
        else:
            update_status("Socket connection not available.")
    except Exception as e:
        update_status("Error: " + str(e))



# Function to set up the initial scan screen
def setup_scan_screen():
	global window
	for widget in window.winfo_children():
		widget.destroy()

	scan_button = tk.Button(window, text="Scan for Bikes", command=send_scan_command, width=20)
	scan_button.pack(pady=20)

	global status_label
	status_label = tk.Label(window, text=" ")
	status_label.pack(pady=20)
   


# Function to start the Wi-SUN connection process and then show the scan screen
def start_connection():
    global connect_button
    update_status("Connecting to Wi-SUN...")

    set_wisun_thread = ThreadWithReturnValue(target=setup_wisun)
    set_wisun_thread.start()
    wisun_setup = set_wisun_thread.join(timeout=600)  # 10 minutes to setup Wi-SUN else BR not setup

    if wisun_setup:
        print("EVscript: Wi-SUN Connection Successful")
        setup_scan_screen()
    else:
        print("EVscript: Wi-SUN Not connected")
        update_status("EVscript: Failed to connect to Wi-SUN.")
        time.sleep(1)
        for widget in window.winfo_children():
            widget.destroy()
        connect_button.pack(pady=20)


def EV(sock_port=6002, Ard_port=6003):
    global connect_button
    global status_label
    global cli_socks
    global window
    global socket_q
    global Ard_socks
    global Ard_serial_q
    global read_Arduino_thread

    print("EVscript: EV_charger")

    # Create a socket object
    cli_socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli_socks.connect((socket.gethostname(), sock_port))  # Bind to the port
    print("EVscript: Connected to local server.")

    time.sleep(1)

    # Create an Arduino Socket
    Ard_socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Ard_socks.connect((socket.gethostname(), Ard_port))  # Bind to the port
    print("EVscript: Connected to Arduino server.")

    socket_q = deque()
    Ard_serial_q = deque()

    read_thread = threading.Thread(target=read_socket)
    read_thread.start()

    read_Arduino_thread = threading.Thread(target=read_Ard_serial)
    read_Arduino_thread.start()
    
    
    # Create the main window
    window = tk.Tk()
    window.title("EV Charger")

    # Set up a button to initiate the Wi-SUN connection
    connect_button = tk.Button(window, text="Connect to Wi-SUN", command=start_connection, width=20)
    connect_button.pack(pady=20)

    # Add a label for status updates
    status_label = tk.Label(window, text="")
    status_label.pack(pady=20)

    # Start the Tkinter event loop
    window.mainloop()


