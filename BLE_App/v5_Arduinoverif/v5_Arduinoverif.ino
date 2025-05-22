#include <ArduinoBLE.h>

// Define BLE Service and Characteristics UUIDs
#define TEXT_SERVICE_UUID       "1e03ce00-b8bc-4152-85e2-f096236d2833"
#define TEXT_MESSAGE_CHAR_UUID  "1e03ce01-b8bc-4152-85e2-f096236d2833"

// BLE Service and Characteristic
BLEService textService(TEXT_SERVICE_UUID);
BLECharacteristic textMessageCharacteristic(
  TEXT_MESSAGE_CHAR_UUID,
  BLERead | BLEWrite | BLENotify,
  100
);

String inputBuffer = "";          // Buffer to collect Serial input
bool isArduinoVerified = false;   // Added for CHECK_ARDUINO feature
bool bleAdvertisingStarted = false;  // Track whether BLE advertising has started

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Initialize BLE
  if (!BLE.begin()) {
    Serial.println("Starting BLE module failed!");
    while (1);
  }

  Serial.println("Awaiting CHECK_ARDUINO command to begin BLE advertising...");
}

void loop() {
  // Check if we need to verify this device as Arduino
  if (!isArduinoVerified && Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "CHECK_ARDUINO") {
      Serial.println("ARDUINO_OK");
      isArduinoVerified = true;
      Serial.println("Arduino verified. BLE advertising will begin now.");
    }
  }

  // Start BLE advertising *only after* verification
  if (isArduinoVerified && !bleAdvertisingStarted) {
    BLE.setLocalName("Wi-SUN EV Charger-001");
    BLE.setAdvertisedService(textService);

    textService.addCharacteristic(textMessageCharacteristic);
    BLE.addService(textService);

    BLE.advertise();
    bleAdvertisingStarted = true;

    Serial.println("BLE Text Transceiver is now advertising.");
  }

  if (!bleAdvertisingStarted) {
    return;
  }

  BLEDevice central = BLE.central();
  if (central) {
    Serial.print("APP: Connected to central: ");
    Serial.println(central.address());

    while (central.connected()) {
      // Check if Text Message Characteristic was written to
      if (textMessageCharacteristic.written()) {
        String receivedText = "";
        const uint8_t* value = textMessageCharacteristic.value();
        int length = textMessageCharacteristic.valueLength();

        for (int i = 0; i < length; i++) {
          receivedText += (char)value[i];
        }

        if (receivedText.equalsIgnoreCase("DISCONNECT")) {
          Serial.println("Received DISCONNECT command. Disconnecting...");
          BLE.disconnect();
          break;
        }

        Serial.print("APP: ");
        Serial.println(receivedText);
      }

      // Handle Serial input
      if (Serial.available()) {
        char c = Serial.read();
        if (c == '\n' || c == '\r') {
          if (inputBuffer.startsWith("ANDROID: ")) {
            String message = inputBuffer.substring(9);
            textMessageCharacteristic.writeValue((const uint8_t*)message.c_str(), message.length());
            Serial.print("Sent to Android: ");
            Serial.println(message);

            if (message.equalsIgnoreCase("DISCONNECT")) {
              Serial.println("Disconnect command received. Disconnecting...");
              BLE.disconnect();
              break;
            }
          } else {
            Serial.println("Invalid input format. Use 'ANDROID: <message>' or 'CHECK_ARDUINO'.");
          }
          inputBuffer = ""; // Clear buffer after processing
        } else {
          inputBuffer += c;
        }
      }

      BLE.poll();
    }

    Serial.println("APP: Central disconnected.");
    inputBuffer = ""; // Clear buffer on disconnection
  }

  BLE.poll();
}
