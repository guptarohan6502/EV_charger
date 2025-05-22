#include <ArduinoBLE.h>
#include<string.h>

// variables for button
int oldButtonState = LOW;

// Store discovered devices
BLEDevice discoveredDevices[10];
int deviceCount = 0;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Initialize the Bluetooth® Low Energy hardware
  BLE.begin();

  Serial.println("Bluetooth® Low Energy Central - LED control");

}

void loop() {

    // Check for user input
  if (Serial.available() > 0) {
    String command = Serial.readString();
    command.trim();
    if (command == "SCAN") {
      startScanning();
    } else if (command.toInt() > 0 && command.toInt() <= deviceCount) {
      connectToDevice(command.toInt() - 1);
    } else {
      Serial.println("Invalid input or no devices available. Please type 'SCAN' to scan for devices.");
    }
  }

  
  // Check if a peripheral has been discovered
  BLEDevice peripheral = BLE.available();

  if (peripheral) {
    // Store discovered peripheral
    if (deviceCount < 10) {
      discoveredDevices[deviceCount] = peripheral;
      deviceCount++;
    }
  }


}

void startScanning() {
  Serial.println("Scanning for devices...");
  deviceCount = 0; // Reset device count
  BLE.scanForUuid("180A"); // Start scanning for devices with the specified UUID
}

void connectToDevice(int index) {
  BLEDevice peripheral = discoveredDevices[index];

  // Stop scanning
  BLE.stopScan();

  Serial.print("Connecting to ");
  Serial.print(peripheral.localName());
  Serial.println("...");

  if (peripheral.connect()) {
    Serial.println("Connected");

    // Discover peripheral attributes
    Serial.println("Discovering attributes ...");
    if (peripheral.discoverAttributes()) {
      Serial.println("Attributes discovered");
    } else {
      Serial.println("Attribute discovery failed!");
      peripheral.disconnect();
      return;
    }

    // Retrieve the LED characteristic
    BLECharacteristic ledCharacteristic = peripheral.characteristic("2A57");

    if (!ledCharacteristic) {
      Serial.println("Peripheral does not have LED characteristic!");
      peripheral.disconnect();
      return;
    } else if (!ledCharacteristic.canWrite()) {
      Serial.println("Peripheral does not have a writable LED characteristic!");
      peripheral.disconnect();
      return;
    }

    while (peripheral.connected()) {
      // While the peripheral is connected

      // Read the button pin
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

    Serial.println("Peripheral disconnected");
  } else {
    Serial.println("Failed to connect!");
  }

  // Restart scanning after disconnection
  startScanning();
}
