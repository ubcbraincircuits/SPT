import RPi.GPIO as GPIO
from time import sleep
import time
import board
import busio
import datetime as dt
from picamera import PiCamera
from threading import Thread
#import cv2
from picamera import PiCamera
import os
import json

class solenoid:
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
        sucrose_pattern=mice[mouse]['SPT_Pattern']
        spt_level=str(mice[mouse]['SPT_level'])
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

class mice_dict:
    def __init__(self,cage):
        self.cage=cage
        self.config_file_path=cage+'/'+'SPT_mouse_config.jsn'
        if not os.path.exists(self.config_file_path):
            print('No previoues mice configurations found')
            self.startup()
        else:
            with open(self.config_file_path,'r') as file:
                self.mice_config=json.loads(file.read().replace('\n',','))

    def startup(self):
        if os.path.exists(self.config_file_path):
            print('Config file for '+self.cage+' already exists')
            pass
        else:
            self.mice_config={}
            numMice=input('Enter number of mice for the current SPT:')
            i=0
            while i<int(numMice):
                self.add_mice()
                i+=1
        temp=json.dumps(self.mice_config).replace(',','\n')
        with open (self.config_file_path,'w') as outfile:
                outfile.write(temp)
        print('All mice '+str(numMice)+' added')

    def add_mice(self):
        try:
            tagreader = TagReader (RFID_serialPort, RFID_doCheckSum, timeOutSecs = RFID_timeout, kind=RFID_kind)
        except Exception as e:
                raise e
        i=0
        print('Scan mice now')
        while i<1:
            try:
                tag = tagreader.readTag ()
                i+=1
                print (tag)
            except ValueError as e:
                print (str (e))
        tagreader.clearBuffer()
        SPT_lvl=input('Enter SPT level for new mouse:')
        SPT_Spout=input('Enter initial SPT spout for new mouse (R/L):')
        temp={tag:{'SPT_Pattern': SPT_Spout, 'SPT_level': int(SPT_lvl)}}
        self.mice_config.update(temp)

    def remove_mouse(self):
        try:
            tagreader = TagReader (RFID_serialPort, RFID_doCheckSum, timeOutSecs = RFID_timeout, kind=RFID_kind)
        except Exception as e:
            raise e
        i=0
        print('Scan mice to remove now')
        while i<1:
            try:
                tag = tagreader.readTag ()
                i+=1
                print (tag)
            except ValueError as e:
                print (str (e))
        del self.mice_config[str(tag)]

    def write_log_config(self):
        if not os.path.exists(self.cage+'/'+'SPT_mouse_past_config.csv'):
            with open(self.cage+'/'+'SPT_mouse_past_config.csv','w') as file:
                file.write('Date,Tag,SPT_level,SPT_Pattern\n')
            log_date=dt.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            for k, v in self.mice_config.items():
                file.write(log_date+','+str(k)+','+str(v['SPT_level'])+','+v['SPT_Spout']+'\n')
        else:
            with open(self.cage+'/'+'SPT_mouse_past_config.csv','a') as file:
               log_date=dt.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
               for k, v in self.mice_config.items():
                   file.write(log_date+','+str(k)+','+str(v['SPT_level'])+','+v['SPT_Pattern']+'\n')

    def spout_swtich(self):
        self.write_log_config()
        for k, v in self.mice_config.items():
            if self.mice_config[k]['SPT_Pattern'] == 'R':
                self.mice_config[k]['SPT_Pattern']='L'
            elif self.mice_config[k]['SPT_Pattern']=='L':
                self.mice_config[k]['SPT_Pattern']='R'

    def spt_levelup(self):
        n_level=input('Enter level for all mice to increase to: ')
        for k, v in self.mice_config.items():
            self.mice_config[k]['SPT_level']=int(n_level)

###############
class task_settings():
    tag_in_range_pin_def = 17
    #TODO: other settings

    def __init__(self,task_name):
        self.task_name=task_name
        self.config_file_name= 'SPT_' + self.task_name + '.jsn'
        if not os.path.exists(self.config_file_name):
            print('Task settings file '+ self.task_name+' not found')
            print('Please create new task file')
            pass
        else:
            self.task_config = self.file_to_dict(self.config_file_name)
            print('SPT_'+self.task_name+' settings loaded')

    def config_user_get(self, starterDict={}):
        '''
        Gets user configuration
        :param starterDict: empty dictionary if not specified
        :return: starterDict: dict after user modification
        '''
        #RFID pin
        tag_in_range_pin = starterDict.get('speakerPin', self.tag_in_range_pin_def)
        tempInput = input('Set speaker pin(currently {0}): '.format(tag_in_range_pin))
        if tempInput != '':
            tag_in_range_pin = int(tempInput)
        starterDict.update({'tag_in_range_pin': tag_in_range_pin})
        #TODO: other settings
        return starterDict

    def file_to_dict(nameStr, dir=''):
        """
        Sets attributes for the object anObject from the keys and values of dictionay aDict loaded from the file
        :param nameStr: The full file name
        :param dir: Directory of the file
        :return:
        """
        try:
            filename = nameStr
            errFlag = False
            with open(dir + filename, 'r') as fp:
                data = fp.read()
                data = data.rstrip("\n")
                data = data.replace('\n', ',')
                data = data.replace('=', ':')
                configDict = json.loads(data)
                fp.close()
        except FileNotFoundError as e:
            raise e
        return configDict

    def dict_to_file(anyDict, nameStr, dir=''):
        """
         Saves a dicitonary as JSON encoded text file
        :param anyDict Dictionary to be converted
        :param nameStr: Name of JSON file
        :param dir: Directory to save JSON file
        :return: None
        """
        configFile = nameStr
        with open(dir + configFile, 'w') as fp:
            fp.write(json.dumps(anyDict, separators=('\n', '='), sort_keys=True, skipkeys=True))
            fp.close()

    def write_new_settings(self):
        if os.path.exists(self.config_file_name):
            print('Config file for '+self.cage+' already exists')
            pass
        else:
            self.task_name=input('What is the task name?')
            tag_in_range_pin=input('What is the tag in range pin?')
            selenoid_pin_LW=input('What is the pin for the left water valve?')
            selenoid_pin_LS=input('What is the pin for the left sucrose/resrticted valve?')
            selenoid_pin_RW=input('What is the pin for the right water valve?')
            selenoid_pin_RS=input('What is the pin for the right sucrose/resrticted valve?')
            buzzer_pin=input('What is the buzzer pin?')
            vid_folder=input('Enter the folderin whcih the video is saved to: ')
            hours=input('Enter the hour for the valve switch?')
            reward_amount=input('Enter the reward amount (valve open time in seconds): ')
            self.task_config={'tag_in_range_pin':int(tag_in_range_pin),'selenoid_pin_LW':int(selenoid_pin_LW),'selenoid_pin_LS':int(selenoid_pin_LS),'selenoid_pin_RW':int(selenoid_pin_RW),'selenoid_pin_RS':int(selenoid_pin_RS),'buzzer_pin':int(buzzer_pin),'vid_folder':vid_folder,'hours':int(hours),'reward_amount':float(reward_amount)}
            self.task_config = {k: self.task_config[k] for k in sorted(self.task_config)}
            temp= json.dumps(self.task_config).replace(',','\n')
            with open ('SPT_'+self.task_name+'.jsn','w') as outfile:
                outfile.write(temp)

    def change_settings(self):
        dic={0: 'tag_in_range_pin',1: 'selenoid_pin_LW', 2: 'selenoid_pin_LS', 3: 'selenoid_pin_RW', 4: 'selenoid_pin_RS', 5: 'buzzer_pin',  6: 'vid_folder', 7: 'hours', 8: 'reward_amount'}
        print('Current Settings for the task '+self.task_name) 
        for i,(key, values) in zip(dic,self.task_config.items()):
            print (i, key+':',values)
        parameter_change=input('Enter parameter to change: ')
        value_to_change_to=input('Value to change to: ')
        self.task_config[dic[int(parameter_change)]]=eval(type(self.task_config[dic[int(parameter_change)]]).__name__+'('+str(value_to_change_to)+')')
        temp= json.dumps(self.task_config).replace(',','\n')
        with open ('SPT_'+self.task_name+'.jsn','w') as outfile:
            outfile.write(temp)
