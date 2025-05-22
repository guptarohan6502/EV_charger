#include <ArduinoBLE.h>

BLEService ledService("180A"); // Bluetooth® Low Energy LED Service

// Bluetooth® Low Energy LED Switch Characteristic - custom 128-bit UUID, read and writable by central
BLEByteCharacteristic switchCharacteristic("2A57", BLERead | BLEWrite);

const int ledPin = LED_BUILTIN; // pin to use for the LED
const int buttonPin = 2; // using Dx notation, button connected to pin D2
unsigned long advertiseStartTime = 0; // to keep track of when advertising started
bool isAdvertising = false;

void setup() {
  Serial.begin(9600);
  
  // Set LED pin to output mode and button pin to input mode
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);  // Button connected to D2

  // Begin BLE initialization
  if (!BLE.begin()) {
    Serial.println("starting Bluetooth® Low Energy module failed!");
    while (1);
  }

  // Set advertised local name and service UUID:
  BLE.setLocalName("BIKE-2");
  Serial.println("BIKE-2");
  BLE.setAdvertisedService(ledService);

  // Add the characteristic to the service
  ledService.addCharacteristic(switchCharacteristic);

  // Add service
  BLE.addService(ledService);

  // Set the initial value for the characteristic:
  switchCharacteristic.writeValue(0);

  Serial.println("Ready to advertise when button is pressed.");
}

void loop() {
  // Check if the button is pressed to start advertising
    if (!isAdvertising) {
      Serial.println("Advertising again");
      startAdvertising();
    
  }

  

  // Listen for BLE peripherals to connect:
  BLEDevice central = BLE.central();

  // If a central is connected to peripheral:
  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    // While the central is still connected to peripheral:
    while (central.connected()) {
      // If the remote device wrote to the characteristic,
      // use the value to control the LED:
      if (switchCharacteristic.written()) {
        if (switchCharacteristic.value()) {   // any value other than 0
          Serial.println("LED on");
          digitalWrite(ledPin, HIGH);         // will turn the LED on
        } else {                              // a 0 value
          Serial.println(F("LED off"));
          digitalWrite(ledPin, LOW);          // will turn the LED off
        }
      }
    }

    // When the central disconnects, print it out:
    Serial.print(F("Disconnected from central: "));
    Serial.println(central.address());
  }
}

void startAdvertising() {
  // Start advertising
  BLE.advertise();
  Serial.println("Advertising started.");

  // Mark the time when advertising started
  advertiseStartTime = millis();
  isAdvertising = true;
}

void stopAdvertising() {
  // Stop advertising
  BLE.stopAdvertise();
  Serial.println("Advertising stopped after 1 minute.");

  isAdvertising = false;
}
