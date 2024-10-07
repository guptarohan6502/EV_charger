import warnings
import threading
import RPi.GPIO as GPIO
import time



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
    




        




def  Charger():
  
   """
   Error Codes:
   1. Charging Completed Successfully
   2. Power meter not working
   3. Insufficient Balance
   4. Invalid ID
   5. Any other error
   """ 
    try:
        power_sensor = PZEM()
    except:
       return 2
        

    print(f"Amount: {keypad_input} and VehicleidTag: {user_idTag}")
    idtag_str = f"{{'Amount': {keypad_input}, 'VehicleidTag' : '{user_idTag}','Time': {time.time()}, 'Chargerid': 'EV-L001-03'}}"
    

    costperunit = 10
    unit_1 = 36000000 # ideally 36000000
    
    
    
    RFID_thread = ThreadWithReturnValue(target = check_rfid_valid, args=(idtag_str,))
    RFID_thread.start()
    Rfid_valid = RFID_thread.join(timeout = 60) # 1 minute to verify RFID
    time.sleep(2)
    
    
    
    if(Rfid_valid== True):
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        print(f"Totalunit you get = {keypad_input/costperunit}")
        
        
        netunit = keypad_input/costperunit
        netenergy = netunit*unit_1
        GPIO.setup(4, GPIO.OUT)
        start=time.time()

        try:
            print("Charger: Checking readiness")
            if(1):
                print(f"Charger: Charging started ")
                GPIO.output(4, GPIO.HIGH)
                time.sleep(0.1)
                power = 500#power_sensor.readPower()
                while(power <= 0):
                    power = 500#power_sensor.readPower()

                energy_cons = 0
                energy_cons = (power*(time.time()-start))
                print(f"Charger: power={power}")
                print('\n')
                while(energy_cons < netenergy ):
                    print("\r", f"Charger: units_cons = {energy_cons/unit_1: .2f}", end='\r')
                    energy_cons = (power*(time.time()-start))
                    """
                    if stop_charge_keypad():  # Break if 'C' key is pressed
                        print("Charger: Stopping")
                        break
                    else:
                        continue
                    """
                        
                    
                    

                print(time.time()-start)
                print("Charger: Done")
                GPIO.output(4, GPIO.LOW)
        finally:
            power=0
            power_sensor.close()
            print("Charger: ok")
            )
       
        
    elif (Rfid_valid == False):
        print(f"Charger: VehicleidTag: {user_idTag} is not registered")
        return 4
      
        
    elif (Rfid_valid == "Low balance"):
        print("Charger: User Has low balancd Kindly recharge")
        return 3
        
    else:
        print("Charger: " + Rfid_valid)
        return 5        
        
    





