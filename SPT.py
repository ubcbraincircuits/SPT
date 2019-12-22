#contains classes and fucntion used in the SPT main 
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
			
			
'''
need to integrate into main as class
'''
import json
import datetime as dt
from RFIDTagReader import TagReader
RFID_serialPort = '/dev/ttyUSB0'
RFID_kind = 'ID'
RFID_timeout = None
RFID_doCheckSum = True
mice={124112412:{'SPT_level':0, 'SPT_Spout':'R'},
      290940990:{'SPT_level':1, 'SPT_Spout':'L'},
      365236336:{'SPT_level':2, 'SPT_Spout':'R'},
      284592849:{'SPT_level':3, 'SPT_Spout':'L'},
      122451521:{'SPT_level':1, 'SPT_Spout':'R'}}

class mice_dict:
    def __init__(self,cage):
        self.cage=cage
        self.config_file_path=cage+'/'+'SPT_mouse_config.jsn'
        if not os.path.exist(self.config_file):
            pass
        else:
            with  open(self.config_file_path,'r') as file:
                self.mice_config=json.loads(file.read().replace('\n',',')) 
    def startup(self):
        if os.path.exist(self.config_file):
            print('Config file for '+self.cage+' already exists')
            pass
        else:
            self.mice_config={}
            numMice=input('Enter number of mice for the current SPT:')
            i=0
            while i<numMice:
                self.add_mice()
                i+=1
            print('All mice '+str(numMice)+' added')                
    def add_mice(self):
        try: 
            tagreader = TagReader (RFID_serialPort, RFID_doCheckSum, timeOutSecs = RFID_timeout, kind=RFID_kind)
        except Exception as e:
                raise e
        i=0
        while i<1:
            try:
                tag = tagReader.readTag ()
                i+=1
                print (tag)
            except ValueError as e:
                print (str (e))
        tagReader.clearBuffer()
        SPT_lvl=input('Enter SPT level for new mouse:')
        SPT_Spout=input('Enter initial SPT spout for new mouse (R/L):')
        temp={tag:{'SPT_Spout': SPT_Spout, 'SPT_level': int(SPT_lvl)}}
        mice. update(temp)
    def write_log_config():
        if not os.path.exist(): 
            with open('SPT_mouse_past_config.csv','w') as file:
                file.write('Date,Tag,SPT_level,SPT_Spout\n')
        else: 
            with open('SPT_mouse_past_config.csv','a') as file:
               log_date=dt.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
               for k, v in self.mice_config.items():
                   file.write(log_date+','+str(k)+','+str(v['SPT_level'])+','+v['SPT_Spout']+'\n')
    def spout_swtich():
        self.write_log_config()
        for k, v in self.mice_config.items():
            if mice[k]['SPT_Spout'] == 'R':
                mice[k]['SPT_Spout']='L'
            elif mice[k]['SPT_Spout']=='L':
                mice[k]['SPT_Spout']='R'
        		
				
