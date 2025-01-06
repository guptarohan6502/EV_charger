https://stackoverflow.com/questions/76020133/how-to-get-python-tkinter-application-to-run-automatically-and-reliably-at-rpi

Why?
We want to use systemctl because it provides an easy way to configure, start, and stop our program. We want to block and detect display availability so that it is able to launch the GUI at the earliest availability. This notion of waiting within the program is the key for reliability.

How (step by step)?
Run sudo nano /etc/systemd/system/my-service.service changing 'my-service' to the name of your choice.
Configure the service by pasting the following in (make sure to update the contents with your path and name):
[Unit]
Description=My Application
After=graphical.target
Wants=graphical.target

[Service]
Type=simple
User=prototype
Environment=DISPLAY=:0
ExecStart=python3 /home/path-to-program/main.py

[Install]
WantedBy=graphical.target
Run sudo systemctl enable my-service.service
Within your code base, setup your tk window as such:
def initialize_gui():
   root_window = tk.Tk()
   # Setup GUI, ect.
   root_window.mainloop()

while True:
   try:
      initialize_gui()
   except Exception as e:
      print(f"Waiting for GUI to become available: {e}")
      time.sleep(0.2) # Small delay, not needed but recommended
    
And there you have it, if the display is not available when the service is started at boot, it will retry until it does become available. After implementing this method I have not had any issues with the program launching on bootup. Hope this helps someone else out because it was a pain to try every technique and figure out.


###################################################################

sudo nano /etc/systemd/system/EV_meter.service

[Unit]
Description=EV Charger Application
After=graphical.target
Wants=graphical.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
ExecStart=/usr/bin/python3 /home/pi/Desktop/EV_charger/BLE_App/Wisun_BLE_UI/run.py

[Install]
WantedBy=graphical.target


##################


sudo systemctl daemon-reload
sudo systemctl restart EV_meter.service



#################