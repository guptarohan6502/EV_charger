
import threading
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import serial
import select
import struct
import socket
import time
from collections import deque

ser_com = serial.Serial('/dev/ttyACM0', 9600)  # Update baud rate if necessary

if ser_com.is_open:
    print("Serial port is open.")


serial_q = deque()
# Create a socket object
cli_socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cli_socks.connect((socket.gethostname(), 6002))  # Bind to the port
print("Connected to local server.")


# def read_serial():
# global serial_read_queue

# while True:
# if ser_com.in_waiting > 0:
# data = ser_com.readline()
# serial_read_queue.append(data.decode().strip())
# print("Received:", data.decode().strip())


def read_serial():
    global serial_q

    while True:
        msg = cli_socks.recv(1024)
        serial_q.append(msg.decode().strip())
        print("Received:", msg.decode().strip())


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


def keypad():
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
                        time.sleep(0.2)
                        while(GPIO.input(ROW[i]) == 1):
                            pass
                        if(a == '#'):
                            y = len(xmap)
                            del xmap[y-1]
                            z = int(''.join(str(m) for m in xmap))
                           # print(z)
                            y = len(xmap)
                            return(z)
                            raise StopIteration

                GPIO.output(COL[j], GPIO.LOW)
    except StopIteration:
        GPIO.cleanup()


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


def check_rfid_valid(idtag_str):
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

    if "valid_yes" in str(read_string):
        return True
    elif "valid_not" in str(read_string):
        return False
    elif"valid_insuff" in str(read_string):
        return "Low balance"


def rfid():
    try:
        id, text = reader.read()
        print(text)
        return(id)
    finally:
        GPIO.cleanup()


read_thread = threading.Thread(target=read_serial)
read_thread.start()
print("out of thread")

setup_wisun()


while True:
    power_sensor = PZEM()

    #setup_wisun_thread = threading.Thread(target=setup_wisun())
    # setup_wisun_thread.start()

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
        print(COL[j])
        GPIO.setup(COL[j], GPIO.OUT)
        GPIO.output(COL[j], 1)
    for i in range(4):
        GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    q = []
    n = []
    l = 0

    # keypad interfacing with raspberry pi
    print('Amount you want to charge for : Press the amount and press#')

    keypad_input = keypad()
    print(f"Amount you want to charge for : {keypad_input}")
    GPIO.cleanup()

    GPIO.setmode(GPIO.BOARD)
    reader = SimpleMFRC522()
    print('Vehicle identity number:Scan the card')

    user_idTag = rfid()
    print(f"Amount: {keypad_input} and VehicleidTag: {user_idTag}")
    idtag_str = f"{{'Amount': {keypad_input}, 'VehicleidTag' : '{user_idTag}','Time': {time.time()}, 'Chargerid': 1}}"

    costperunit = 7
    unit_1 = 36  # ideally 36000000

    Rfid_valid = check_rfid_valid(idtag_str)

    if(Rfid_valid == True):
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        print(f"Totalunit you get = {keypad_input/costperunit}")
        netunit = keypad_input/costperunit
        netenergy = netunit*unit_1
        GPIO.setup(4, GPIO.OUT)

        try:
            print("Checking readiness")
            if(power_sensor.isReady()):
                print("Charging started")
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
        finally:
            power_sensor.close()
    elif (Rfid_valid == False):
        print(f"VehicleidTag: {user_idTag} is not registered")
    elif (Rfid_valid == "Low balance"):
        print("User Has low balancd Kindly recharge")

    g = {
        "amount": keypad_input,
        "VehicleidTag": user_idTag
    }
