/*
  GDG Arduino LED Strip Tree Controller with BLE Scanning

  This sketch uses the ArduinoBLE library to create a Bluetooth Low Energy (BLE) device
  that controls LED effects through BLE characteristics for color and effect, while also
  scanning for other BLE peripherals advertising a specific UUID (`180a`) and prints
  a message when such a device is detected.

  Author: Leonardo Cavagnis (Modified by OpenAI's ChatGPT)
*/

#include <ArduinoBLE.h>

// Define BLE Service and Characteristics UUIDs for LED Control
#define LED_SERVICE_UUID          "1e03ce00-b8bc-4152-85e2-f096236d2833"
#define LED_COLOR_CHAR_UUID       "1e03ce01-b8bc-4152-85e2-f096236d2833"
#define LED_EFFECT_CHAR_UUID      "1e03ce02-b8bc-4152-85e2-f096236d2833"

// Define UUID to Scan For
#define SCAN_SERVICE_UUID         "180a"  // Example UUID to scan for

// Define LED Effects
#define OFF_EFFECT      0  
#define STEADY_EFFECT   1
#define BLINK_EFFECT    2
#define ALTBLINK_EFFECT 3
#define GDG_EFFECT      4

// BLE Service and Characteristics
BLEService            ledService                  (LED_SERVICE_UUID);
BLECharacteristic     ledColorCharacteristic      (LED_COLOR_CHAR_UUID, BLERead | BLEWrite, 3);
BLEByteCharacteristic ledEffectCharacteristic     (LED_EFFECT_CHAR_UUID, BLERead | BLEWrite);

// Variables to store LED states
byte ledColor[3] = {255, 0, 0};  // Initial RGB color
byte prevColor[3] = {255, 0, 0}; // To track previous color state
byte ledEffect = STEADY_EFFECT;

// Variables for Scanning
const int MAX_DEVICES = 10;
BLEDevice discoveredDevices[MAX_DEVICES];
int deviceCount = 0;

// Function Prototypes
void bleCentralDiscoverHandler(BLEDevice peripheral);
void startScanning();

// Flag to track scanning state
bool isScanning = false;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Initialize BLE
  if (!BLE.begin()) {
    Serial.println("Starting BLE module failed!");
    while (1);
  }

  // Set up Peripheral Role
  BLE.setLocalName("USER-1");
  BLE.setAdvertisedService(ledService);
  
  // Add Characteristics to Service
  ledService.addCharacteristic(ledColorCharacteristic);
  ledService.addCharacteristic(ledEffectCharacteristic);
  
  // Add Service
  BLE.addService(ledService);
  
  // Set Initial Characteristic Values
  ledColorCharacteristic.writeValue(ledColor, 3);
  ledEffectCharacteristic.writeValue(ledEffect);
  
  // Start Advertising
  BLE.advertise();
  
  Serial.println("BLE Peripheral is now advertising.");

  // Set up Central Role for Scanning
  BLE.setEventHandler(BLEDiscovered, bleCentralDiscoverHandler);

  // Start scanning for the specified UUID
  startScanning();
}

void loop() {
  // Handle Peripheral Connections and Characteristics
  BLEDevice central = BLE.central();

  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    while (central.connected()) {
      // Check if LED Color Characteristic was written to
      if (ledColorCharacteristic.written()) {
        if (ledColorCharacteristic.valueLength() == 3) {
          ledColorCharacteristic.readValue(ledColor, 3);

          // Check if the new color is different from the previous color
          if (ledColor[0] != prevColor[0] || ledColor[1] != prevColor[1] || ledColor[2] != prevColor[2]) {
            Serial.print("New Color Set: ");
            Serial.print(ledColor[0], HEX);
            Serial.print(", ");
            Serial.print(ledColor[1], HEX);
            Serial.print(", ");
            Serial.println(ledColor[2], HEX);

            // Update previous color
            prevColor[0] = ledColor[0];
            prevColor[1] = ledColor[1];
            prevColor[2] = ledColor[2];
          }
        }
      }

      // Check if LED Effect Characteristic was written to
      if (ledEffectCharacteristic.written()) {
        ledEffect = ledEffectCharacteristic.value();

        Serial.print("Effect: ");
        Serial.println(ledEffect, HEX);
      }

      // Poll BLE for Peripheral role
      BLE.poll();
    }

    Serial.println("Central disconnected.");
  }

  // Poll BLE for Central role (scanning)
  BLE.poll();
}

// Function to handle BLE scan results
void bleCentralDiscoverHandler(BLEDevice peripheral) {
  // Check if the peripheral advertises the specific service UUID
  if (peripheral.advertisedServiceUuid() == "180a") {
    Serial.println("Emergency vehicle detected!");
    Serial.print("Device Name: ");
    Serial.println(peripheral.localName());
    Serial.print("Device Address: ");
    Serial.println(peripheral.address());

    // Optionally, you can stop scanning after detecting the emergency vehicle
    // BLE.stopScan();
    // isScanning = false;
  }
}


// Function to initiate scanning
void startScanning() {
  deviceCount = 0;
  Serial.println("Starting BLE scan for devices with UUID: " SCAN_SERVICE_UUID);
  BLE.scanForUuid(SCAN_SERVICE_UUID, false); // false to allow duplicates
  isScanning = true;
}
