import tkinter as tk
import socket
import threading
from collections import deque
from keypad import Keypad
from wisun_set_script import setup_wisun
import Arduino  # Import the Arduino.py functions
import Charger_script
import time


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

class MainApp:
    def __init__(self, root, wisun_port, arduino_port):
        self.root = root
        #self.root.geometry("600x400")
        self.root.attributes('-fullscreen', True)
        self.root.title("EV Charger Wi-SUN Connection")

        # Initialize variables
        self.wisun_port = wisun_port
        self.arduino_port = arduino_port
        self.Emergency_vehicle_discovered = False

        # Set up the Arduino socket
        self.arduino_socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.arduino_socks.connect((socket.gethostname(), self.arduino_port))
        self.arduino_socket_q = deque()

        # Start thread to read Arduino messages
        threading.Thread(target=self.read_Ard_serial, daemon=True).start()

        # Start the setup process
        threading.Thread(target=self.setup_process, daemon=True).start()

    def read_Ard_serial(self):
        while True:
            time.sleep(0.5)
            try:
                msg = self.arduino_socks.recv(1024).decode().strip()
                if "Emergency:" in msg:
                    if not self.Emergency_vehicle_discovered:
                        msg = "Emergency Vehicle Discovered"
                        print("EVscript: Emergency vehicle discovered")
                        #self.wisun_socks.send(("wisun socket_write 4 \"" + str((str(msg) + str(" Near Node Charger EV-L001-04")) + "\"\n")).encode())
                        self.Emergency_vehicle_discovered = True
                        threading.Thread(target=self.reset_emergency_status, daemon=True).start()
                elif "APP" in msg:
                    self.arduino_socket_q.append(msg)
                    print(f"UIscript: Arduino q appended msg: {msg}")
            except Exception as e:
                print(f"Error reading from Arduino: {e}")

    def reset_emergency_status(self):
        time.sleep(10)
        self.Emergency_vehicle_discovered = False

    def show_initial_frame(self, msg, light=""):
        self.clear_frame()

        self.initial_frame = tk.Frame(self.root)
        # Make this frame occupy the entire window
        self.initial_frame.pack(fill="both", expand=True)

        # Create a container frame that we place in the center
        container = tk.Frame(self.initial_frame)
        # relx=0.5, rely=0.5 means "center of the window";
        # anchor="center" means the container's (0,0) is pinned to the center
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Traffic light frame (goes inside the container)
        traffic_frame = tk.Frame(container)
        traffic_frame.pack(pady=20)  # Stack vertically inside container

        def get_led_color(led, current_light):
            # Dim vs. bright LED colors
            if led == current_light:
                return {"G": "#00FF00", "Y": "#FFFF00", "R": "#FF0000"}.get(led, "#808080")
            return {"G": "#008000", "Y": "#808000", "R": "#800000"}.get(led, "#808080")

        green_color = get_led_color('G', light)
        yellow_color = get_led_color('Y', light)
        red_color = get_led_color('R', light)

        tk.Label(traffic_frame, width=10, height=5, bg=green_color).pack(side="left", padx=10)
        tk.Label(traffic_frame, width=10, height=5, bg=yellow_color).pack(side="left", padx=10)
        tk.Label(traffic_frame, width=10, height=5, bg=red_color).pack(side="left", padx=10)

        # Status label
        self.status_label = tk.Label(container, text=msg, font=("Helvetica", 25))
        self.status_label.pack(pady=20)

        # Explanation frame
        explanation_frame = tk.Frame(container)
        explanation_frame.pack(pady=10)

        tk.Label(explanation_frame, text="Green - Available for connection", font=("Helvetica", 15)).pack(anchor="w")
        tk.Label(explanation_frame, text="Yellow - Connecting to Wi-SUN", font=("Helvetica", 15)).pack(anchor="w")
        tk.Label(explanation_frame, text="Red - Busy", font=("Helvetica", 15)).pack(anchor="w")



    def check_rfid_valid(self, idtag_str):
        print(f"EVscript: Input Validation started")
        try:
            time.sleep(2)
            return True  # Assume validation succeeds
        except Exception as e:
            print(f"Error in RFID validation: {e}")
            return False

    def charger_func(self, creds_to_verify):
        print(f"Creds: {creds_to_verify}")
        idtag_str = f"{{'Amount': {creds_to_verify[2]}, 'VehicleidTag': {creds_to_verify[1]}, 'Time': {time.time()}, 'Chargerid': 'EV-L001-04'}}"
        try:
            # Start a background thread to verify RFID
            RFID_thread = ThreadWithReturnValue(target=self.check_rfid_valid, args=(idtag_str,))
            RFID_thread.start()
            Rfid_valid = RFID_thread.join(timeout=60)  # Wait up to 1 minute for RFID verification
            
            print(f"RFID Validity: {Rfid_valid}")
            if not Rfid_valid:
                print("Error: Invalid RFID.")
                return 5  # Error code for RFID failure
            else:
                self.arduino_socks.send(b"ANDROID: OK\n")

            time.sleep(2)  # Simulate charging time
            Incomplete_percentage = None
            # Perform the charging operation
            Return_status = Charger_script.Charger(Rfid_valid, creds_to_verify[2],self.arduino_socket_q,self.arduino_socks)
            charge_status = Return_status[0]
            Incomplete_percentage = 1-Return_status[1]
            if(Incomplete_percentage):
                print(f"EVscript: Charging was completed only {1-Incomplete_percentage} %")
            print(f"EVscript: Charging encountered status {charge_status}")
            if charge_status ==1:
                self.arduino_socks.send(b"ANDROID: PRG_1.0\n")
                # time.sleep(0.1)
                # self.arduino_socks.send(b"Disconnect")
            elif charge_status == 6:
                print(f"EVscript: Posting latest data due to incomplete charging.")
                idtag_str = f"{{'Amount': {str(int(-1*(Incomplete_percentage)*int(creds_to_verify[2])))}, 'VehicleidTag': {creds_to_verify[1]}, 'Time': {time.time()}, 'Chargerid': 'EV-L001-04'}}"
                RFID_thread = ThreadWithReturnValue(target=self.check_rfid_valid, args=(idtag_str,))
                RFID_thread.start()
                Rfid_valid = RFID_thread.join(timeout=10)  # Wait up to 10 sec to post updated data
                
            return charge_status
        except Exception as e:
            print(f"Error in charging: {e}")
            return 5  # General error code


    def connect_to_ble_user(self):
        try:
            user_id = Arduino.read_central_connection(self.arduino_socket_q)
            self.show_initial_frame("Busy", light="R")
            pin, amount = Arduino.app_communication(self.arduino_socket_q, self.arduino_socks)
            return [user_id, pin, amount]
        except Exception as e:
            print(f"Error in connect_to_ble_user: {e}")
            return None

    def setup_process(self):
        self.show_initial_frame("Connecting to Wi-SUN...", light="Y")
        try:
            wisun_connected = setup_wisun()
            if wisun_connected:
                print("Wi-SUN Connected!")
                self.show_initial_frame("Wi-SUN Connected!", light="G")
                self.main_loop()
            else:
                print("Failed to connect to Wi-SUN.")
                self.show_initial_frame("Failed to connect to Wi-SUN. Press '#' to retry.", light="R")
        except Exception as e:
            print(f"Error during Wi-SUN setup: {e}")
            self.show_initial_frame("Error in setup. Retrying...", light="R")
            time.sleep(2)
            self.setup_process()

    def main_loop(self):
        while True:
            self.show_initial_frame("Wi-SUN Connected!", light="G")
            creds = self.connect_to_ble_user()
            if creds:
                charge_status = self.charger_func(creds)
                print(f"Charge status: {charge_status}")
                self.arduino_socks.send(b"ANDROID: Disconnect\n")
            else:
                print("Reconnecting to BLE User...")

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root, wisun_port=12345, arduino_port=12346)
    root.mainloop()
