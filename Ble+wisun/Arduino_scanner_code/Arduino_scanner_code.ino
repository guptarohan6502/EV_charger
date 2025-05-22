#include <ArduinoBLE.h>

int oldButtonState = LOW;

// Store discovered devices
BLEDevice discoveredDevices[10];

int deviceCount = 0;
bool isArduinoVerified = false; // To track if the device has been verified as an Arduino

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // begin initialization
  if (!BLE.begin()) {
    Serial.println("starting Bluetooth® Low Energy module failed!");
    while (1);
  }

  Serial.println("Bluetooth® Low Energy Central scan callback");

  // Set the discovered event handler
  BLE.setEventHandler(BLEDiscovered, bleCentralDiscoverHandler);

  // start scanning for peripherals with duplicates
  // BLE.scan();
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
  // Check for Emergency Peripheral
  if (peripheral.advertisedServiceUuid() == "180a") {
    Serial.println("Emergency: Emergency Peripheral Discovered");
    Serial.println("-----------------------");
  }

  // Store discovered peripheral
  if (!isPeripheralAlreadyDiscovered(peripheral) && deviceCount < 10) {
    discoveredDevices[deviceCount] = peripheral;
    deviceCount++;
  }
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

    // While the peripheral is connected, handle button interaction
    while (peripheral.connected()) {
      if (Serial.available() > 0) {
        String command = Serial.readString();
        command.trim();
        if (command == "DISCONNECT") {
          Serial.println("EV_Bike: Charging Completed");
          peripheral.disconnect();
          return;
        } else {
          Serial.println("EV_Bike: Invalid input. Type 'DISCONNECT' to end connection.");
        }
      } else {
        // Simulate button state change
        int buttonState = !oldButtonState;
        delay(1000);

        if (oldButtonState != buttonState) {
          oldButtonState = buttonState;
          if (buttonState) {
            Serial.println("button pressed");
            ledCharacteristic.writeValue((byte)0x01); // Turn LED on
          } else {
            Serial.println("button released");
            ledCharacteristic.writeValue((byte)0x00); // Turn LED off
          }
        }
      }
    }
    Serial.println("EV_Bike: Peripheral Disconnected");
  } else {
    Serial.println("EV_Bike: Failed to connect!");
  }

  // Restart scanning after disconnection
  startScanning();
}

void startScanning() {
  deviceCount = 0;
  Serial.println("EV_Bike: Scanning for devices...");
  BLE.scanForUuid("181A", false);
  BLE.poll();
  delay(1500);

  Serial.println("EV_Bike: Bikes are available to connect:");
  Serial.print("EV_Bike: ");
  Serial.println(deviceCount);


  for (int i = 0; i < deviceCount; i++) {
    BLEDevice peripheral = discoveredDevices[i];
    Serial.print("EV_Bike: ");
    Serial.print(i + 1);
    Serial.print(":");
    Serial.println(peripheral.localName());
  }

  Serial.println("Select a device to connect:");
}

void loop() {
  // Check for Arduino verification message
  if (!isArduinoVerified && Serial.available() > 0) {
    String command = Serial.readString();
    command.trim();
    if (command == "CHECK_ARDUINO") {
      Serial.println("ARDUINO_OK");
      isArduinoVerified = true;
      Serial.println("Arduino verified. You can now scan or connect.");
    }
  }

  // Check for scan or connect commands
  if (isArduinoVerified) {
    if (Serial.available() > 0) {
      String command = Serial.readString();
      command.trim();
      if (command == "SCAN") {
        startScanning();
      } else if (command.toInt() > 0 && command.toInt() <= deviceCount) {
        connectToDevice(command.toInt() - 1);
      } else {
        Serial.println("EV_Bike: Invalid input or no devices available. Please type 'SCAN' to scan for devices.");
      }
    }
  }
}
