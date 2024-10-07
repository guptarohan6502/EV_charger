import warnings
import threading
import socket
import time
import tkinter as tk
from collections import deque

warnings.filterwarnings("ignore")


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

    while True:
        msg = Ard_socks.recv(1024).decode().strip()

        # Condition 1: Check if it is an emergency message
        if "Emergency: Emergency Peripheral Discovered" in msg:
            cli_socks.send(msg.encode())

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

        while ("IPv6 address" not in str(read_string)) and ("wisun.border_router = fd12:3456" not in str(read_string)):
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


def get_amount():
    global window
    amount_window = tk.Toplevel(window)
    amount_window.title("Enter Amount")

    amount_label = tk.Label(amount_window, text="Enter amount (in integer):")
    amount_label.pack(pady=10)

    amount_entry = tk.Entry(amount_window)
    amount_entry.pack(pady=5)

    def submit_amount():
        try:
            amount = int(amount_entry.get())
            amount_window.destroy()  # Close the input window after submitting
            return_value.append(amount)
        except ValueError:
            # Display an error if the input is not an integer
            error_label.config(text="Invalid input. Please enter an integer.")

    # A list to store the return value since Tkinter's command functions can't return directly
    return_value = []

    submit_button = tk.Button(amount_window, text="Submit", command=submit_amount)
    submit_button.pack(pady=10)

    error_label = tk.Label(amount_window, text="", fg="red")
    error_label.pack()

    # Wait for the user to submit the amount
    amount_window.grab_set()
    window.wait_window(amount_window)

    return return_value[0] if return_value else None


# Charging function to simulate charging for 10 seconds
def charging():
    global window, status_label

    try:
        time.sleep(10)  # Simulate charging time of 10 seconds
        return 1  # Charging success
    except Exception as e:
        print(f"Error in charging: {e}")
        return 0  # Charging failed


def but_startcharge(bike, bike_details):
    global Ard_serial_q, Ard_socks, window, status_label

    # Get the amount input from the user
    amount = get_amount()
    if amount is None:
        update_status("Error: Invalid amount. Please try again.")
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
        index = bike_details.index(bike) + 1

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
            charging_status = charging()

            # Handle the post-charging process
            if charging_status == 1:
                Ard_socks.send(b"DISCONNECT\n")
                update_status("Charging completed")

            elif charging_status == 0:
                Ard_socks.send(b"DISCONNECT\n")
                update_status("Error: Charging failed")

            # After showing the status, return to the scan screen
            window.after(2000, setup_scan_screen)

        else:
            Ard_socks.send(str("DISCONNECT").encode()) #INCASE arduino bluetooth is connected
            print("EV_script: Error: Not enough data in the queue to read peripheral details.")
            update_status("Error: Could not retrieve peripheral details.")
            window.after(2000, setup_scan_screen)

    except Exception as e:
        Ard_socks.send(str("DISCONNECT").encode()) #Incase arduino bluetooth is connected
        print(f"EV_script: Error in but_startcharge: {e}")
        update_status(f"Error: {e}")
        window.after(2000, setup_scan_screen)


# Function to display bike options
def display_bike_options(bike_details):
    global window, status_label

    print("evbIKE: FINALLY")

    # Clear previous widgets except the status label
    for widget in window.winfo_children():
        if widget != status_label:
            widget.destroy()

    # Display bike buttons
    for bike in bike_details:
        btn = tk.Button(window, text=bike, width=20, command=lambda b=bike: but_startcharge(b, bike_details))
        btn.pack(pady=10)

    # Back button to return to the previous screen
    back_btn = tk.Button(window, text="Back", command=setup_scan_screen)
    back_btn.pack(pady=20)


# Function to handle the scanning process
def scan_for_bikes():
    global Ard_serial_q
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

                        display_bike_options(bike_details)
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


