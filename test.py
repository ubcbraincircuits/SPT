import RPi.GPIO as GPIO
import time
selenoid1_pin= 17 
selenoid2_pin=27
selenoid3_pin=21
selenoid4_pin=25
class selenoid:
	def __init__(self, pin):
		selenoid.pin=pin
	def activate(self,open_time):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self.pin,GPIO.OUT)
		GPIO.output(self.pin,GPIO.HIGH)
		time.sleep(int(open_time))
		GPIO.output(self.pin,GPIO.LOW)
	@staticmethod 
	def clean_up(self):
		GPIO.cleanup()
'''
def turnvalve(value=1):
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	if value ==1 :
		GPIO.setup(servo1_pin,GPIO.OUT)
		GPIO.output(servo1_pin, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(servo1_pin, GPIO.LOW)
		GPIO.cleanup()
	elif value ==2:
		GPIO.setup(servo2_pin,GPIO.OUT)
		GPIO.output(servo2_pin, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(servo2_pin, GPIO.LOW)
		GPIO.cleanup()
	else:
		print('retry')
	
if __name__== '__main__':
	value=input('1 or 2')
	turnvalve(int(value))
'''
