#include <ArduinoBLE.h>

const char* ledBikeAddress = "ec:62:60:8f:45:02"; // BLE address of Arduino Nano BLE 1
const char* ledServiceUUID = "19B10000-E8F2-537E-4F6C-D104768A1214";
const char* switchCharacteristicUUID = "19B10001-E8F2-537E-4F6C-D104768A1214";

BLEDevice peripheral; // BLE Device to connect to
BLEService ledService(ledServiceUUID);
BLECharacteristic switchCharacteristic(switchCharacteristicUUID, BLERead | BLEWrite);

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!BLE.begin()) {
    Serial.println("starting Bluetooth® Low Energy module failed!");
    while (1);
  }

  BLE.scanForUuid(ledServiceUUID); // Scan for the BLE service
  Serial.println("Scanning for BLE peripherals...");
}

void loop() {
  peripheral = BLE.available(); // Check if a BLE peripheral is available

  if (peripheral) {
    Serial.println("Found BLE Peripheral");
    if (peripheral.address() == ledBikeAddress) { // Check if it's the right peripheral
      Serial.println("Connecting to BLE Peripheral...");
      if (peripheral.connect()) {
        Serial.println("Connected to BLE Peripheral");

        BLEService service = peripheral.service(ledServiceUUID);
        if (service) {
          Serial.println("Service found");

          switchCharacteristic = service.characteristic(switchCharacteristicUUID);
          if (switchCharacteristic) {
            Serial.println("Characteristic found");

            // Toggle LED on and off every second
            while (true) {
              switchCharacteristic.writeValue(1); // Turn LED on
              Serial.println("LED on");
              delay(1000); // Wait for 1 second
              switchCharacteristic.writeValue(0); // Turn LED off
              Serial.println("LED off");
              delay(1000); // Wait for 1 second
            }
          } else {
            Serial.println("Characteristic not found");
          }
        } else {
          Serial.println("Service not found");
        }
        peripheral.disconnect();
      } else {
        Serial.println("Failed to connect to BLE Peripheral");
      }
    } else {
      Serial.println("Peripheral address does not match");
    }
  }
}
