/*
  GDG Arduino BLE Text Message Receiver

  This sketch uses the ArduinoBLE library to create a Bluetooth Low Energy (BLE) device
  that receives text messages through a BLE characteristic and prints them to the Serial Monitor.

  Author: OpenAI's ChatGPT (based on original code by Leonardo Cavagnis)
*/

// you can start

#include <ArduinoBLE.h>

// Define BLE Service and Characteristics UUIDs
#define TEXT_SERVICE_UUID       "1e03ce00-b8bc-4152-85e2-f096236d2833"
#define TEXT_MESSAGE_CHAR_UUID  "1e03ce01-b8bc-4152-85e2-f096236d2833"
// THESE ID NEEDS TO REFERCEN ON ANDRODI CODE I THINK
//ARE YOU THERE?yes

// BLE Service and Characteristic
BLEService            textService               (TEXT_SERVICE_UUID);
BLECharacteristic     textMessageCharacteristic(TEXT_MESSAGE_CHAR_UUID, BLERead | BLEWrite, 100); // Up to 100 characters

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Initialize BLE
  if (!BLE.begin()) {
    Serial.println("Starting BLE module failed!");
    while (1);
  }

  // Set up Peripheral Role
  BLE.setLocalName("TextReceiver");
  BLE.setAdvertisedService(textService);
  
  // Add Characteristic to Service
  textService.addCharacteristic(textMessageCharacteristic);
  
  // Add Service
  BLE.addService(textService);
  
  // Start Advertising
  BLE.advertise();
  
  Serial.println("BLE Text Receiver is now advertising.");
}

void loop() {
  // Handle Peripheral Connections and Characteristics
  BLEDevice central = BLE.central();

  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    while (central.connected()) {
      // Check if Text Message Characteristic was written to
      if (textMessageCharacteristic.written()) {
        // Get the value and convert it to a String
        const uint8_t* value = textMessageCharacteristic.value();
        int length = textMessageCharacteristic.valueLength();
        
        // Convert to a String
        String receivedText = "";
        for (int i = 0; i < length; i++) {
          receivedText += (char)value[i];
        }

        // Print the received text message to the Serial Monitor
        Serial.print("Received Text: ");
        Serial.println(receivedText);
      }

      // Poll BLE for Peripheral role
      BLE.poll();
    }

    Serial.println("Central disconnected.");
  }

  // Poll BLE for Central role
  BLE.poll();
}
