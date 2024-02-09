import warnings
import threading
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import serial
import select
import struct
import socket
import time
from tkinter import *

from collections import deque
warnings.filterwarnings("ignore")



def read_serial():
    global serial_q

    while True:
        msg = cli_socks.recv(1024)
        serial_q.append(msg.decode().strip())
        #print("Received:", msg.decode().strip())

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


class PZEM:

    setAddrBytes = [0xB4, 0xC0, 0xA8, 0x01, 0x01, 0x00, 0x1E]
    readVoltageBytes = [0xB0, 0xC0, 0xA8, 0x01, 0x01, 0x00, 0x1A]
    readCurrentBytes = [0XB1, 0xC0, 0xA8, 0x01, 0x01, 0x00, 0x1B]
    readPowerBytes = [0XB2, 0xC0, 0xA8, 0x01, 0x01, 0x00, 0x1C]
    readRegPowerBytes = [0XB3, 0xC0, 0xA8, 0x01, 0x01, 0x00, 0x1D]

    # dmesg | grep tty       list Serial linux command

    def __init__(self, com="/dev/ttyUSB0", timeout=10.0):       # Usb serial port
        # def __init__(self, com="/dev/ttyAMA0", timeout=10.0):  	 # Raspberry Pi port Serial TTL
        # def __init__(self,com="/dev/rfcomm0", timeout=10.0):

        self.ser = serial.Serial(
            port=com,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=timeout
        )
        if self.ser.isOpen():
            self.ser.close()
        self.ser.open()

    def checkChecksum(self, _tuple):
        _list = list(_tuple)
        _checksum = _list[-1]
        _list.pop()
        _sum = sum(_list)
        if _checksum == _sum % 256:
            return True
        else:
            raise Exception("Wrong checksum")

    def isReady(self):
        self.ser.write(serial.to_bytes(self.setAddrBytes))
        rcv = self.ser.read(7)
        if len(rcv) == 7:
            unpacked = struct.unpack("!7B", rcv)
            if(self.checkChecksum(unpacked)):
                return True
        else:
            raise serial.SerialTimeoutException("Timeout setting address")

    def readVoltage(self):
        self.ser.write(serial.to_bytes(self.readVoltageBytes))
        rcv = self.ser.read(7)
        if len(rcv) == 7:
            unpacked = struct.unpack("!7B", rcv)
            if(self.checkChecksum(unpacked)):
                tension = unpacked[2]+unpacked[3]/10.0
                return tension
        else:
            raise serial.SerialTimeoutException("Timeout reading tension")

    def readCurrent(self):
        self.ser.write(serial.to_bytes(self.readCurrentBytes))
        rcv = self.ser.read(7)
        if len(rcv) == 7:
            unpacked = struct.unpack("!7B", rcv)
            if(self.checkChecksum(unpacked)):
                current = unpacked[2]+unpacked[3]/100.0
                return current
        else:
            raise serial.SerialTimeoutException("Timeout reading current")

    def readPower(self):
        self.ser.write(serial.to_bytes(self.readPowerBytes))
        rcv = self.ser.read(7)
        if len(rcv) == 7:
            unpacked = struct.unpack("!7B", rcv)
            if(self.checkChecksum(unpacked)):
                power = unpacked[1]*256+unpacked[2]
                return power
        else:
            raise serial.SerialTimeoutException("Timeout reading power")

    def readRegPower(self):
        self.ser.write(serial.to_bytes(self.readRegPowerBytes))
        rcv = self.ser.read(7)
        if len(rcv) == 7:
            unpacked = struct.unpack("!7B", rcv)
            if(self.checkChecksum(unpacked)):
                regPower = unpacked[1]*256*256+unpacked[2]*256+unpacked[3]
                return regPower
        else:
            raise serial.SerialTimeoutException(
                "Timeout reading registered power")

    def readAll(self):
        if(self.isReady()):
            return(self.readVoltage(), self.readCurrent(), self.readPower(), self.readRegPower())

    def close(self):
        self.ser.close()
    
    
    
def setup_wisun():
    global serial_q
    read_string = ""

    
    ser_com.write(("wisun get wisun\n").encode())
    ser_com.write(("wisun join_fan10\n").encode())
    
    if serial_q:
        read_string = serial_q.pop()
        
    while(("IPv6 address" not in str(read_string)) and ("wisun.border_router = fd12:3456" not in str(read_string))):
        if serial_q:
            read_string = serial_q.pop()
        else:
            continue
        print("\r", f"waiting For wisun to setup", end='\r')
    print("Connneted to wisun")
    if(("IPv6 address" in str(read_string))):
        ser_com.write(("wisun udp_server 5001\n").encode())
        time.sleep(1)
        ser_com.write(("wisun udp_client fd12:3456::1 5005\n").encode())
        time.sleep(1)
        ser_com.write(("wisun get wisun\n").encode())
        time.sleep(1)
        ser_com.write(("wisun socket_list\n").encode())
        time.sleep(1)

    return True


def keypad():
    GPIO.setmode(GPIO.BCM)
    j = 0
    i = 0
    h = 0
    g = 0

    # elements of keypad
    MATRIX = [[1, 2, 3, 'A'],
              [4, 5, 6, 'B'],
              [7, 8, 9, 'C'],
              ['*', 0, '#', 'D']]

    # connections to GPIO pins
    ROW = [5, 6, 13, 19]  # rows of key
    COL = [12, 16, 20, 21]

    for j in range(4):
        GPIO.setup(COL[j], GPIO.OUT)
        GPIO.output(COL[j], 1)
    for i in range(4):
        GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    q = []
    n = []
    l = 0

    i = 0
    j = 0
    try:
        xmap = []
        while(j != 2 and i != 4):
            for j in range(4):
                GPIO.output(COL[j], GPIO.HIGH)
                for i in range(4):
                    if GPIO.input(ROW[i]) == 1:
                        a = MATRIX[i][j]
                        xmap.append(str(a))
                        print(a,end='')
                        time.sleep(0.2)
                        while(GPIO.input(ROW[i]) == 1):
                            pass
                        if(a == '#'):
                            print('\n')
                            y = len(xmap)
                            del xmap[y-1]
                            z = (''.join(str(m) for m in xmap))
                           # print(z)
                            return(z)
                            raise StopIteration

                GPIO.output(COL[j], GPIO.LOW)
    except StopIteration:
        GPIO.cleanup()



def keypad_take_inp():
    input_correct = False
    #check if take inp can be converted to int
    while(input_correct == False):
        take_inp = keypad()
        try:
            take_inp = int(take_inp)
            input_correct = True
        except:
            print("Input is not a number. Pls input again\n")
            input_correct = False
    return take_inp
    
    

        
def check_rfid_valid(idtag_str):
    global start_time
    print(f"Input give Validation started")
    print(f"data being sent")
    global serial_q
    read_string = ""
    ser_com.write(("wisun socket_write 4 \""+idtag_str + "\"\n").encode())
    print("wisun socket_write 4 \""+idtag_str + "\"\n")
    
    if serial_q:
        read_string = serial_q.pop()
    
    while "valid" not in str(read_string):
        if serial_q:
            read_string = serial_q.pop()
        else:
            continue
        print("\r", f"waiting For Id validation", end='\r')
    print(f"Validation done")

    if "valid_yes" in str(read_string):
        return True
    elif "valid_not" in str(read_string):
        return False
    elif"valid_insuff" in str(read_string):
        return "Low balance"
    elif"valid_error" in str(read_string):
        return "Onem2m Not \n responding at \n the Moment"
        

def rfid():
    global reader
    try:
        id, text = reader.read()
        print(text)
        return(id)
    finally:
        GPIO.cleanup()

def  but_start_wisun():
    global root
    global start_button
    global start_charge
    
    start_button.grid_forget()
    set_wis_label = Button(root,text = "Connecting to BR....", padx = 100,pady=100,font=("Helvetica",20))
    set_wis_label.grid(row =0,column =0)
    root.update_idletasks()
    
    set_wisun_thread = ThreadWithReturnValue(target = setup_wisun)
    set_wisun_thread.start()
    wisun_setup = set_wisun_thread.join(timeout = 600) #10 minutes to setup wisum else br not setup
    
    if wisun_setup:
        set_wis_label.grid_forget()
        set_wis_label = Button(root,text = "--Connected--", padx = 100,pady=100,font=("Helvetica",20))
        set_wis_label.grid(row =0,column =0)
        root.update_idletasks()
        time.sleep(5)
        set_wis_label.grid_forget()
        start_charge.grid(row =0, column = 0)
        root.update_idletasks()
        
        
    else:
        set_wis_label.grid_forget()
        set_wis_label = Button(root,text = "Wisun wasn't able to setup", padx = 100,pady=100,font=("Helvetica",20))
        set_wis_label.grid(row =0,column =0)
        root.update_idletasks()
        time.sleep(5)
        set_wis_label.grid_forget()
        start_button.grid(row =0,column =0)
        root.update_idletasks()
        

def  but_startcharge():
    global root
    global start_charge
    global start_button
    global reader
    
    
    try:
        power_sensor = PZEM()
    except:
        start_charge.grid_forget()
        root.update_idletasks()
        time.sleep(1)
        power_label =  Button(root,text = "Power Meter Not working", padx = 100,pady=100,font=("Helvetica",20))
        power_label.grid(row =0,column =0)
        time.sleep(10)
        power_label.grid_forget()
        start_button.grid(row =0,column =0)
        
        

    
    start_charge.grid_forget()
    set_charge_label = Button(root,text = "Enter Amount", padx = 100,pady=100,font=("Helvetica",20))
    set_charge_label.grid(row =0,column =0)
    root.update_idletasks()
    time.sleep(0.1)
    # keypad interfacing with raspberry pi
    print('Amount you want to charge for : Press the amount and press#')
    keypad_input = keypad_take_inp()
    
    print(f"Amount you want to charge for : {keypad_input}")
    GPIO.cleanup()
    
    set_charge_label.grid_forget()
    root.update_idletasks()
    set_charge_label = Button(root,text = f"Amount to charge: {keypad_input}\n Scan ID ", padx = 100,pady=100,font=("Helvetica",20))
    set_charge_label.grid(row =0,column =0)
    root.update_idletasks()
    
    
    
    GPIO.setmode(GPIO.BOARD)
    reader = SimpleMFRC522()
    print('Vehicle identity number:Scan the card')


    user_idTag = rfid()
    print(f"Amount: {keypad_input} and VehicleidTag: {user_idTag}")
    idtag_str = f"{{'Amount': {keypad_input}, 'VehicleidTag' : '{user_idTag}','Time': {time.time()}, 'Chargerid': 1}}"
    

    costperunit = 7
    unit_1 = 36  # ideally 36000000
    
    RFID_thread = ThreadWithReturnValue(target = check_rfid_valid, args=(idtag_str,))
    RFID_thread.start()
    Rfid_valid = RFID_thread.join(timeout = 60) # 1 minute to verify RFID
    
    
    
    
    if(Rfid_valid== True):
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        print(f"Totalunit you get = {keypad_input/costperunit}")
        
        set_charge_label.grid_forget()
        root.update_idletasks()
        set_charge_label = Button(root,text = f"Total Units= {keypad_input/costperunit:0.2f}\n Charging...", padx = 100,pady=100,font=("Helvetica",20))
        set_charge_label.grid(row =0,column =0)
        root.update_idletasks()
        
        time.sleep(1)
        
        netunit = keypad_input/costperunit
        netenergy = netunit*unit_1
        GPIO.setup(4, GPIO.OUT)

        try:
            print("Checking readiness")
            if(power_sensor.isReady()):
                print(f"Charging started ")
                GPIO.output(4, GPIO.HIGH)
                time.sleep(0.1)
                power = power_sensor.readPower()
                while(power <= 0):
                    power = power_sensor.readPower()

                start = time.time()
                energy_cons = 0
                energy_cons = (power*(time.time()-start))
                print(f"power={power}")
                print('\n')
                while(energy_cons < netenergy):
                    print("\r", f"units_cons = {energy_cons/unit_1}", end='\r')
                    energy_cons = (power*(time.time()-start))

                print(time.time()-start)
                print("Done")
                GPIO.output(4, GPIO.LOW)
                #print(f"Charging finshed {time.time()-start_time}")

        finally:
            power_sensor.close()
            
        set_charge_label.grid_forget()
        root.update_idletasks()
        set_charge_label = Button(root,text = f"Charging Done", padx = 100,pady=100,font=("Helvetica",20))
        set_charge_label.grid(row =0,column =0)
        root.update_idletasks()
        time.sleep(5)
        set_charge_label.grid_forget()
        start_charge.grid(row = 0, column =0)
        root.update_idletasks()
        
    elif (Rfid_valid == False):
        print(f"VehicleidTag: {user_idTag} is not registered")
        set_charge_label.grid_forget()
        root.update_idletasks()
        set_charge_label = Button(root,text =f"VehicleidTag: {user_idTag} \n is not registered", padx = 100,pady=100,font=("Helvetica",20))
        set_charge_label.grid(row =0,column =0)
        root.update_idletasks()
        time.sleep(5)
        set_charge_label.grid_forget()
        start_charge.grid(row = 0,column = 0)
        root.update_idletasks()
        
        
    elif (Rfid_valid == "Low balance"):
        print("User Has low balancd Kindly recharge")
        set_charge_label.grid_forget()
        root.update_idletasks()
        set_charge_label = Button(root,text ="Low Balance \n Kindly recharge", padx = 100,pady=100,font=("Helvetica",20))
        set_charge_label.grid(row =0,column =0)
        root.update_idletasks()
        time.sleep(5)
        set_charge_label.grid_forget()
        start_charge.grid(row = 0,column = 0)
        root.update_idletasks()
        
    else:
        print(Rfid_valid)
        set_charge_label.grid_forget()
        root.update_idletasks()
        set_charge_label = Button(root,text =str(Rfid_valid), padx = 100,pady=100,font=("Helvetica",20))
        set_charge_label.grid(row =0,column =0)
        root.update_idletasks()
        time.sleep(5)
        set_charge_label.grid_forget()
        start_button.grid(row = 0,column = 0)
        root.update_idletasks()
        
    

    g = {
        "amount": keypad_input,
        "VehicleidTag": user_idTag
    }







ser_com = serial.Serial('/dev/ttyACM0', 9600)  # Update baud rate if necessary

if ser_com.is_open:
    print("Serial port is open.")


serial_q = deque()
# Create a socket object
cli_socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cli_socks.connect((socket.gethostname(), 6001))  # Bind to the port
print("Connected to local server.")



read_thread = threading.Thread(target=read_serial)
read_thread.start()





        
root = Tk()
root.geometry("500x500")     

reader = None

start_button = Button(root,text = "Start Wi-sun setup", padx = 100,pady=100,font=("Helvetica",20),command=but_start_wisun)
start_button.grid(row =0,column =0)

start_charge = Button(root,text = "Start Charging", padx = 100,pady=100,font=("Helvetica",20),command = but_startcharge)




root.mainloop()
