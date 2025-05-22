/*
  Scan Callback

  This example scans for Bluetooth® Low Energy peripherals and prints out their advertising details:
  address, local name, advertised service UUIDs. Unlike the Scan example, it uses
  the callback style APIs and disables filtering so the peripheral discovery is
  reported for every single advertisement it makes.

  The circuit:
  - Arduino MKR WiFi 1010, Arduino Uno WiFi Rev2 board, Arduino Nano 33 IoT,
    Arduino Nano 33 BLE, or Arduino Nano 33 BLE Sense board.

  This example code is in the public domain.
*/

#include <ArduinoBLE.h>

int oldButtonState = LOW;


// Store discovered devices
BLEDevice discoveredDevices[10];



int deviceCount = 0;


void setup() {
  Serial.begin(9600);
  while (!Serial);

  // begin initialization
  if (!BLE.begin()) {
    Serial.println("starting Bluetooth® Low Energy module failed!");

    while (1);
  }

  Serial.println("Bluetooth® Low Energy Central scan callback");

  // set the discovered event handle
  BLE.setEventHandler(BLEDiscovered, bleCentralDiscoverHandler);

  // start scanning for peripherals with duplicates
//  BLE.scan();
}


// Function to check if a peripheral is already in the discoveredDevices array
bool isPeripheralAlreadyDiscovered(BLEDevice peripheral) {
  for (int i = 0; i < deviceCount; i++) {
    if (discoveredDevices[i].address() == peripheral.address()) {
      return true; // Device is already in the array
    }
  }
  return false; // Device is not in the array
}

void bleCentralDiscoverHandler(BLEDevice peripheral) {


  //   // print the local name, if present
  // if (peripheral.hasLocalName()) {
  //   Serial.print("Bike Name: ");
  //   Serial.println(peripheral.localName());
  // }
  if (peripheral) {
    // Store discovered peripheral
    if (!isPeripheralAlreadyDiscovered(peripheral) && deviceCount < 10) {
      discoveredDevices[deviceCount] = peripheral;
      deviceCount++;
      // Serial.println("Stored");
    }
  }


  // print the advertised service UUIDs, if present
  // if (peripheral.hasAdvertisedServiceUuid()) {
  //   Serial.print("Service UUIDs: ");
  //   for (int i = 0; i < peripheral.advertisedServiceUuidCount(); i++) {
  //     Serial.print(peripheral.advertisedServiceUuid(i));
  //     Serial.print(" ");
  //   }
  //   Serial.println();
  // }

  // print the RSSI

}

void connectToDevice(int index) {
  BLEDevice peripheral = discoveredDevices[index];
  Serial.print("EV_Bike: ");
  Serial.println(peripheral.localName());
  Serial.print("EV_Bike: ");
  Serial.println(peripheral.address());

  // Stop scanning
  BLE.stopScan();

  Serial.print("EV_Bike: Connecting to ");
  Serial.print(peripheral.localName());
  Serial.println("...");

  if (peripheral.connect()) {
    Serial.println("EV_Bike: Connected");

    // Discover peripheral attributes
    Serial.println("EV_Bike: Discovering attributes ...");
    if (peripheral.discoverAttributes()) {
      Serial.println("EV_Bike: Attributes discovered");
    } else {
      Serial.println("EV_Bike: Attribute discovery failed!");
      peripheral.disconnect();
      return;
    }

    // Retrieve the LED characteristic
    BLECharacteristic ledCharacteristic = peripheral.characteristic("2A57");

    if (!ledCharacteristic) {
      Serial.println("EV_Bike: Peripheral does not have LED characteristic!");
      peripheral.disconnect();
      return;
    } else if (!ledCharacteristic.canWrite()) {
      Serial.println("EV_Bike: Peripheral does not have a writable LED characteristic!");
      peripheral.disconnect();
      return;
    }

    while (peripheral.connected()) {
      // While the peripheral is connected

      // Read the button pin
    if (Serial.available() > 0) {
      String command = Serial.readString();
      command.trim();
      if (command == "DISCONNECT") {
        Serial.println("EV_Bike: Charging Completed");
        peripheral.disconnect();
        return;
        } 
      else {
        Serial.println("EV_Bike: Invalid input or no devices available. Please type 'SCAN' to scan for devices.");
      }
      }
    else{
      int buttonState = !oldButtonState;
      delay(1000);

      if (oldButtonState != buttonState) {
        // Button changed
        oldButtonState = buttonState;

        if (buttonState) {
          Serial.println("button pressed");

          // Button is pressed, write 0x01 to turn the LED on
          ledCharacteristic.writeValue((byte)0x01);
        } else {
          Serial.println("button released");

          // Button is released, write 0x00 to turn the LED off
          ledCharacteristic.writeValue((byte)0x00);
        }
      }
    }
    }

    Serial.println("EV_Bike: Peripheral Disconnected");
  } 
  
  else {

    Serial.println("EV_Bike: Failed to connect!");
  }

  // Restart scanning after disconnection
  startScanning();
}


void startScanning()
 {
  deviceCount =0;
  Serial.println("EV_Bike: Scanning for devices...");
  BLE.scanForUuid("181A",false);  
 // poll the central for events
  BLE.poll();

  delay(1500);
  
  Serial.println("EV_Bike: Bikes are available to connect:");
  Serial.print("EV_Bike: ");
  Serial.println(deviceCount);

  for(int i =0; i<deviceCount; i++){

    BLEDevice peripheral = discoveredDevices[i];


    Serial.print("EV_Bike: ");
    Serial.print(i+1);
    Serial.print(":");
    Serial.println(peripheral.localName());

  }

  Serial.println("Select Bike to Charge:");


   // Check for user input
  if (Serial.available() > 0) {
    int index = Serial.read();

    if (index < deviceCount ) {
        

      connectToDevice(index);
      
    } else {
      Serial.println("EV_Bike: Invalid input or no devices available. Please type 'SCAN' to scan for devices.");
    }
  }


}


void loop() {


  BLE.scanForUuid("180A",false);  
 // poll the central for events
  BLE.poll();


unsigned long startTime = millis();  // Record the start time
bool dataReceived = false;

while (millis() - startTime < 100) {  // Loop for up to 10 seconds
  if (Serial.available() > 0) {
    dataReceived = true;  // Data is received within the time frame
    String command = Serial.readString();
    command.trim();
    if (command == "SCAN") {
      startScanning();
    } else if (command.toInt() > 0 && command.toInt() <= deviceCount) {
      connectToDevice(command.toInt() - 1);
    } else {
      Serial.println("EV_Bike: Invalid input or no devices available. Please type 'SCAN' to scan for devices.");
    }
    break;  // Exit the loop once data is received and processed
  }
}



  
}
