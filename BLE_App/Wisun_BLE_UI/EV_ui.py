
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
        self.root.geometry("600x400")
        self.root.title("EV Charger Wi-SUN Connection")

        # Initialize variables
        self.wisun_port = wisun_port
        self.arduino_port = arduino_port
        self.Emergency_vehicle_discovered = False

        # Set up the Arduino socket
        self.arduino_socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.arduino_socks.connect((socket.gethostname(), self.arduino_port))
        self.arduino_socket_q = deque()


        read_arduino_thread = threading.Thread(target=self.read_Ard_serial)
        read_arduino_thread.start()

        # Show the initial frame first
        self.show_initial_frame("Connecting to Wisun...", light="Y")

        # Perform Wi-SUN setup in a separate thread
        setup_thread = threading.Thread(target=self.setup_wisun_and_update)
        setup_thread.start()
        

    def read_Ard_serial(self):
        while True:
            time.sleep(0.5)
            msg = self.arduino_socks.recv(1024).decode().strip()

            if "Emergency:" in msg:
                if not self.Emergency_vehicle_discovered:
                    print("EVscript: Emergency vehicle discovered")
                    self.Emergency_vehicle_discovered = True
                    threading.Thread(target=self.reset_emergency_status).start()

            elif "APP" in msg:
                #lean_msg = msg.replace("EV_Bike: ", "")
                self.arduino_socket_q.append(msg)
                print(f"UIscript: Arduino q appended msg: {msg}")

    def reset_emergency_status(self):
        time.sleep(10)
        self.Emergency_vehicle_discovered = False

    def show_initial_frame(self, msg, light=""):
        self.clear_frame()

        self.initial_frame = tk.Frame(self.root)
        self.initial_frame.pack(fill="both", expand=True)

        # Traffic light frame
        traffic_frame = tk.Frame(self.initial_frame)
        traffic_frame.pack(pady=20)

        def get_led_color(led, current_light):
            if led == current_light:
                return {"G": "#00FF00", "Y": "#FFFF00", "R": "#FF0000"}.get(led, "#808080")
            return {"G": "#008000", "Y": "#808000", "R": "#800000"}.get(led, "#808080")

        green_color = get_led_color('G', light)
        yellow_color = get_led_color('Y', light)
        red_color = get_led_color('R', light)

        tk.Label(traffic_frame, width=10, height=5, bg=green_color).pack(side="left", padx=10)
        tk.Label(traffic_frame, width=10, height=5, bg=yellow_color).pack(side="left", padx=10)
        tk.Label(traffic_frame, width=10, height=5, bg=red_color).pack(side="left", padx=10)

        self.status_label = tk.Label(self.initial_frame, text=msg, font=("Helvetica", 25))
        self.status_label.pack(pady=20)

        explanation_frame = tk.Frame(self.initial_frame)
        explanation_frame.pack(pady=10)

        tk.Label(explanation_frame, text="Green - Available for connection", font=("Helvetica", 15)).pack(anchor="w")
        tk.Label(explanation_frame, text="Yellow - Connecting to Wisun", font=("Helvetica", 15)).pack(anchor="w")
        tk.Label(explanation_frame, text="Red - Busy", font=("Helvetica", 15)).pack(anchor="w")
    
    
    def check_rfid_valid(self, idtag_str):
        print(f"EVscript: Input Validation started")
        print(f"EVscript: data being sent")

        read_string = ""
        # self.cli_socks.send(("wisun socket_write 4 \"" + idtag_str + "\"\n").encode())
        # print("EVscript: wisun socket_write 4 \"" + idtag_str + "\"\n")

        # if self.wisun_socket_q:
            # read_string = self.wisun_socket_q.popleft().strip()
            # print(f"read_string:{read_string}")

        # while "valid" not in str(read_string):
            # if self.wisun_socket_q:
                # read_string = self.wisun_socket_q.popleft().strip()
                # print(f"read_string:{read_string}")
            # else:
                # continue
            # print("\r", f"Charger: waiting For ID validation", end='\r')
        # print(f"Charger: Validation done")

        #if "valid_yes" in str(read_string):
        return True
        # elif "valid_not" in str(read_string):
            # return False
        # elif "valid_insuff" in str(read_string):
            # return "Low balance"
        # elif "valid_error" in str(read_string):
    
    def charger_func(self, Creds_to_verify):
        """Simulates the charging process."""
        print(f"Creds: {Creds_to_verify}")
        idtag_str = f"{{'Amount': {Creds_to_verify[2]}, 'VehicleidTag': {Creds_to_verify[1]}, 'Time': {time.time()}, 'Chargerid': 'EV-L001-03'}}"
        try:
            RFID_thread = ThreadWithReturnValue(target=self.check_rfid_valid, args=(idtag_str,))
            RFID_thread.start()
            Rfid_valid = RFID_thread.join(timeout=60)  # 1 minute to verify RFID
            print(f"RFID Validity: {Rfid_valid}")
            time.sleep(2)  # Simulate charging time
            charge_status = Charger_script.Charger(Rfid_valid, amount)
            print(f"UIscript: Charging encountered status {charge_status}")
            return charge_status
        except Exception as e:
            print(f"Error in charging: {e}")
            return 5  # Error code
            
            
    def Connect_to_BLE_User(self):
        User_ID = Arduino.read_central_connection(self.arduino_socket_q)
        self.show_initial_frame("Busy", light="R")
        PIN,Amount = Arduino.app_communication(self.arduino_socket_q, self.arduino_socks)
        Creds_to_verify = [User_ID, PIN, Amount]
        print(Creds_to_verify)
        return Creds_to_verify 
    
    def setup_wisun_and_update(self):
        set_wisun_thread = ThreadWithReturnValue(target=setup_wisun)
        set_wisun_thread.start()
        self.wisun_connected = set_wisun_thread.join(timeout=60)

        if self.connected:
            print("Wi-SUN Connected!")
            self.show_initial_frame("Wi-SUN Connected!", light="G")
            self.Connect_to_BLE_User()
            
        else:
            print("Failed to connect to Wi-SUN")
            self.show_initial_frame("Failed to connect to Wi-SUN. Press '#' to retry.", light="R")

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root, wisun_port=12345, arduino_port=12346)
    root.mainloop()
