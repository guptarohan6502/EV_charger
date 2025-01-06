#!/bin/sh
# launcher.sh
# Navigate to home directory, then to the target directory, execute the Python script, and return to home

cd /
cd /home/pi/Desktop/EV_charger/BLE_App/Wisun_BLE_UI || exit 1  # Ensure the script stops if the directory doesn't exist
sudo python3 run.py
cd /
