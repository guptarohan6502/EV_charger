/*
  GDG Arduino LED Strip Tree Controller

  This sketch uses the ArduinoBLE library to create a Bluetooth Low Energy (BLE) device
  that controls LED effects through BLE characteristics for color and effect, with outputs printed to the serial monitor only when new RGB values are set.
  
  Author: Leonardo Cavagnis
*/

#include <ArduinoBLE.h>

#define OFF_EFFECT      0  
#define STEADY_EFFECT   1
#define BLINK_EFFECT    2
#define ALTBLINK_EFFECT 3
#define GDG_EFFECT      4

BLEService            ledService                  ("1e03ce00-b8bc-4152-85e2-f096236d2833");
BLECharacteristic     ledColorCharacteristic      ("1e03ce01-b8bc-4152-85e2-f096236d2833", BLERead | BLEWrite, 3);
BLEByteCharacteristic ledEffectCharacteristic     ("1e03ce02-b8bc-4152-85e2-f096236d2833", BLERead | BLEWrite);

// ya so i dont think arduino is sending any data
//// okey I understand , now I need to chec how to receive the data give me one second to check?
//ok
// can you push this code 


byte ledColor[3] = {255, 0, 0};  // Initial RGB color
byte prevColor[3] = {255, 0, 0}; // To track previous color state
byte ledEffect = STEADY_EFFECT;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // BLE initialization
  if (!BLE.begin()) {
    Serial.println("Starting BLE module failed!");
    while (1);
  }

  // set advertised local name and service UUID
  BLE.setLocalName("USER-1");
  BLE.setAdvertisedService(ledService);
  BLE.advertise();

  // add the characteristics to the service
  ledService.addCharacteristic(ledColorCharacteristic);
  ledService.addCharacteristic(ledEffectCharacteristic);

  // add ledService service
  BLE.addService(ledService);

  // set the initial value for the characteristics
  ledColorCharacteristic.writeValue(ledColor, 3);
  ledEffectCharacteristic.writeValue(ledEffect);

  // start advertising
  BLE.advertise();

  Serial.println("BLE device is now advertising.");
}

void loop() {
  // listen for BLE peripherals to connect
  BLEDevice central = BLE.central();



  // if a central is connected to peripheral
  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    while (central.connected()) {
      // Check ledColor characteristic write
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

      // Check ledEffect characteristic write
      if (ledEffectCharacteristic.written()) {
        ledEffect = ledEffectCharacteristic.value();

        Serial.print("Effect: ");
        Serial.println(ledEffect, HEX);
      }
    }
  }
}
