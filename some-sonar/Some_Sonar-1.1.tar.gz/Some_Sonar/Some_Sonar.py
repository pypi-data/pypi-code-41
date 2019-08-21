import RPi.GPIO as GPIO
from time import sleep, time

class Sonar:
    def __init__(self, trig, echo):
        self.trig = trig
        self.echo = echo
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(trig, GPIO.OUT)
        GPIO.setup(echo, GPIO.IN)
    def read(self):
        GPIO.output(self.trig, True)
        sleep(0.00001)
        GPIO.output(self.trig, False)
        StartTime = time()
        StopTime = time()
        while GPIO.input(self.echo) == 0:
            StartTime = time()
        while GPIO.input(self.echo) == 1:
            StopTime = time()
        TimeElapsed = StopTime - StartTime
        distance = (TimeElapsed * 34300) / 2
        return distance
    

