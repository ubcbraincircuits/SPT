import RPi.GPIO as GPIO
from time import sleep
import board
import busio
import datetime as dt

import os
class selenoid:
	def __init__(self, pin):
		self.pin=pin
		GPIO.setup(self.pin,GPIO.OUT)
	def activate(self,open_time):
		GPIO.setwarnings(False)
		GPIO.output(self.pin,GPIO.HIGH)
		sleep(float(open_time))
		GPIO.output(self.pin,GPIO.LOW)
		sleep(0.05)		
class data_logger:
	def __init__(self,cage,txtspacer):
		self.cage=cage
		self.txtspacer=txtspacer
		today=dt.datetime.now().strftime('%Y-%m-%d')
		self.filename=self.cage+'/'+'SPT_'+today+'_'+self.cage+'.csv'
		if not os.path.exists(cage+'/'):
			os.mkdir(self.cage+'/')
			print(cage+' Dictionary created')
		else:
			pass
		if not os.path.exists(self.filename):
			print('First day starting SPT')
			with open(self.filename,'a') as file:
				file.write('Time,Tag,Surcose_Pattern,Event\n')
		else:
			pass
	def event_outcome(self,mice,mouse,x):
		spacer='\t'
		sucrose_pattern=mice[int(mouse)]['SPT_pattern']
		current_time=dt.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
		Event= current_time+spacer+mouse+spacer+x
		with open(self.filename,'a') as file:
			file.write(dt.datetime.now().strftime('%Y-%m-%d %H-%M-%S')+self.txtspacer+mouse+self.txtspacer+sucrose_pattern+self.txtspacer+x+'\n')
		print(Event)
		
