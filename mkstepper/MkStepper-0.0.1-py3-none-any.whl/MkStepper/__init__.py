from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

class ULN2003:
	def __init__(self, pins, speed):
		"""
		Stepper Motor Python Driver for ULN 2003 Driver
		Raspberry Pi
		Note: GPIO BCM Will Be Set
		Note: add GPIO.cleanup() at the end of your scripts

		ULN2003([10,12,13,14], 5)

		pins:list - Location of pins according to your wiring

		speed:int - 0-5 Speed of the stepper motor. 1 being the fastest

		"""                
		self.IN1=6 # IN1
		self.IN2=13 # IN2
		self.IN3=19 # IN3
		self.IN4=26 # IN4
		self.time = speed*0.001
		GPIO.setup(self.IN1,GPIO.OUT)
		GPIO.setup(self.IN2,GPIO.OUT)
		GPIO.setup(self.IN3,GPIO.OUT)
		GPIO.setup(self.IN4,GPIO.OUT)

		GPIO.output(self.IN1, False)
		GPIO.output(self.IN2, False)
		GPIO.output(self.IN3, False)
		GPIO.output(self.IN4, False)

	def Step1():
		GPIO.output(self.IN4, True)
		sleep(time)
		GPIO.output(self.IN4, False)

	def Step2():
		GPIO.output(self.IN4, True)
		GPIO.output(self.IN3, True)
		sleep(time)
		GPIO.output(self.IN4, False)
		GPIO.output(self.IN3, False)

	def Step3():
		GPIO.output(self.IN3, True)
		sleep(time)
		GPIO.output(self.IN3, False)

	def Step4():
		GPIO.output(self.IN2, True)
		GPIO.output(self.IN3, True)
		sleep(time)
		GPIO.output(self.IN2, False)
		GPIO.output(self.IN3, False)

	def Step5():
		GPIO.output(self.IN2, True)
		sleep(time)
		GPIO.output(self.IN2, False)

	def Step6():
		GPIO.output(self.IN1, True)
		GPIO.output(self.IN2, True)
		sleep(time)
		GPIO.output(self.IN1, False)
		GPIO.output(self.IN2, False)

	def Step7():
		GPIO.output(self.IN1, True)
		sleep(time)
		GPIO.output(self.IN1, False)

	def Step8():
		GPIO.output(self.IN4, True)
		GPIO.output(self.IN1, True)
		sleep(time)
		GPIO.output(self.IN4, False)
		GPIO.output(self.IN1, False)


	def Left(steps): 
		for i in range(step):
			self.Step1()
			self.Step2()
			self.Step3()
			self.Step4()
			self.Step5()
			self.Step6()
			self.Step7()
			self.Step8()

	def right(steps):
		for i in range(step):
			self.Step8()
			self.Step7()
			self.Step6()
			self.Step5()
			self.Step4()
			self.Step3()
			self.Step2()
			self.Step1()

