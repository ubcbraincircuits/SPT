import RPi.GPIO as GPIO
from time import sleep
import time
import board
import busio
import datetime as dt
from picamera import PiCamera
from threading import Thread
import cv2
from picamera import PiCamera
import os
class selenoid:
	def __init__(self, pin):
		GPIO.setmode(GPIO.BCM)
		self.pin=pin
		GPIO.setup(self.pin,GPIO.OUT)
	def activate(self,open_time):
		GPIO.setwarnings(False)
		GPIO.output(self.pin,GPIO.HIGH)
		sleep(float(open_time))
		GPIO.output(self.pin,GPIO.LOW)
class data_logger:
	def __init__(self,cage,txtspacer):
		self.cage=cage
		self.txtspacer=txtspacer
		today=dt.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
		self.filename=self.cage+'/'+'SPT_'+today+'_'+self.cage+'.csv'
		if not os.path.exists(cage+'/'):
			os.mkdir(self.cage+'/')
			print(cage+' Dictionary created')
		else:
			pass
		if not os.path.exists(self.filename):
			print('Starting a new day starting SPT')
			with open(self.filename,'a') as file:
				file.write('Time,Tag,Surcose_Pattern,SPT_level,Event,Event_dict\n')
		else:
			pass
	def event_outcome(self,mice,mouse,event,event_dict):
		spacer="    "
		sucrose_pattern=mice[int(mouse)]['SPT_pattern']
		spt_level=str(mice[int(mouse)]['SPT_level'])
		current_time=dt.datetime.now().strftime('%Y-%m-%d %H-%M-%S.%f')[:-3]
		Event= current_time+spacer+mouse+spacer+sucrose_pattern+spacer+spt_level+spacer+event+spacer+event_dict
		with open(self.filename,'a') as file:
			file.write(dt.datetime.now().strftime('%Y-%m-%d %H-%M-%S')+self.txtspacer+mouse+self.txtspacer+sucrose_pattern+self.txtspacer+spt_level+self.txtspacer+event+self.txtspacer+event_dict+'\n')
		print(Event+'\n')
class piVideoStream:
	def __init__(self,folder,resolution=(640,480),framerate=90,vidformat='h264',quality=25,preview=(0,0,640,480)):
		self.cam=PiCamera()
		self.resolution=resolution
		self.framerate=framerate
		self.vidformat=vidformat
		self.quality=quality
		self.preview=preview
		self.folder= folder
	def cam_setup(self):
		self.cam.resolution=self.resolution
		self.cam.framerate=self.framerate 
	def record(self,tag):
		self.cam.start_preview(fullscreen=False,window=self.preview)
		self.filename=str(tag)+'_'+dt.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')+'.h264' 
		self.filepath=self.folder+self.filename
		self.cam.start_recording(self.filepath,quality=self.quality)
		return self.filename
	def stop_record(self):
		self.cam.stop_preview()
		self.cam.stop_recording()
class buzzer:
	def __init__(self,pin,pitch,times):
		GPIO.setmode(GPIO.BCM)
		self.pin=pin
		self.delay=(1/pitch)/2
		self.cycle=times
		GPIO.setup(self.pin,GPIO.OUT)
	def buzz(self):
		for i in range(self.cycle):
			GPIO.output(self.pin, True)
			sleep(self.delay)
			GPIO.output(self.pin, False)
			sleep(self.delay)
		
				
