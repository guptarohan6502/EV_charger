import time

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.output(4, GPIO.HIGH)

time.sleep(50.0)

GPIO.output(4, GPIO.LOW)
GPIO.cleanup()
