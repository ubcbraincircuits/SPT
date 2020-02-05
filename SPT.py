# Standard libraries
import RPi.GPIO as GPIO
from time import sleep
import time
import board
import busio
import datetime as dt
from threading import Thread
from picamera import PiCamera
import os

# User libraries
import pi_IO_lib as pi_IO


class solenoid:
    def __init__(self, pin):
        GPIO.setmode(GPIO.BCM)
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def activate(self, open_time):
        GPIO.setwarnings(False)
        GPIO.output(self.pin, GPIO.HIGH)
        sleep(float(open_time))
        GPIO.output(self.pin, GPIO.LOW)


class data_logger:
    def __init__(self, cage, txtspacer):
        self.cage = cage
        self.txtspacer = txtspacer
        today = dt.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self.filename = self.cage + '/' + 'SPT_' + today + '_' + self.cage + '.csv'
        if not os.path.exists(cage + '/'):
            os.mkdir(self.cage + '/')
            print(cage + ' Dictionary created')
        else:
            pass
        if not os.path.exists(self.filename):
            print('Starting a new day starting SPT')
            with open(self.filename, 'a') as file:
                file.write('Time,Tag,Surcose_Pattern,SPT_level,Event,Event_dict\n')
        else:
            pass

    def event_outcome(self, mice, mouse, event, event_dict):
        spacer = "    "
        sucrose_pattern = mice[mouse]['SPT_Pattern']
        spt_level = str(mice[mouse]['SPT_level'])
        current_time = dt.datetime.now().strftime('%Y-%m-%d %H-%M-%S.%f')[:-3]
        Event = current_time + spacer + mouse + spacer + sucrose_pattern + spacer + spt_level + spacer + event + spacer + event_dict
        with open(self.filename, 'a') as file:
            file.write(dt.datetime.now().strftime(
                '%Y-%m-%d %H-%M-%S') + self.txtspacer + mouse + self.txtspacer + sucrose_pattern + self.txtspacer + spt_level + self.txtspacer + event + self.txtspacer + event_dict + '\n')
        print(Event + '\n')


class piVideoStream:
    def __init__(self, folder, resolution=(640, 480), framerate=90, vidformat='h264', quality=25,
                 preview=(0, 0, 640, 480)):
        self.cam = PiCamera()
        self.resolution = resolution
        self.framerate = framerate
        self.vidformat = vidformat
        self.quality = quality
        self.preview = preview
        self.folder = folder

    def cam_setup(self):
        self.cam.resolution = self.resolution
        self.cam.framerate = self.framerate

    def record(self, tag):
        self.cam.start_preview(fullscreen=False, window=self.preview)
        self.filename = str(tag) + '_' + dt.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.h264'
        self.filepath = self.folder + self.filename
        self.cam.start_recording(self.filepath, quality=self.quality)
        return self.filename

    def stop_record(self):
        self.cam.stop_preview()
        self.cam.stop_recording()


class buzzer:
    def __init__(self, pin, pitch, times):
        GPIO.setmode(GPIO.BCM)
        self.pin = pin
        self.delay = (1 / pitch) / 2
        self.cycle = times
        GPIO.setup(self.pin, GPIO.OUT)

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
    def __init__(self, cage):
        self.cage = cage
        self.config_file_path = cage + '/' + 'SPT_mouse_config.jsn'
        if not os.path.exists(self.config_file_path):
            print('No previoues mice configurations found')
            self.startup()
        else:
            with open(self.config_file_path, 'r') as file:
                self.mice_config = json.loads(file.read().replace('\n', ','))

    def startup(self):
        if os.path.exists(self.config_file_path):
            print('Config file for ' + self.cage + ' already exists')
            pass
        else:
            self.mice_config = {}
            numMice = input('Enter number of mice for the current SPT:')
            i = 0
            while i < int(numMice):
                self.add_mice()
                i += 1
        temp = json.dumps(self.mice_config).replace(',', '\n')
        with open(self.config_file_path, 'w') as outfile:
            outfile.write(temp)

        print('All mice ' + str(numMice) + ' added')

    def add_mice(self):
        try:
            tagreader = TagReader(RFID_serialPort, RFID_doCheckSum, timeOutSecs=RFID_timeout, kind=RFID_kind)
        except Exception as e:
            raise e
        i = 0
        print('Scan mice now')
        while i < 1:
            try:
                tag = tagreader.readTag()
                i += 1
                print(tag)
            except ValueError as e:
                print(str(e))
        tagreader.clearBuffer()
        SPT_lvl = input('Enter SPT level for new mouse:')
        SPT_Spout = input('Enter initial SPT spout for new mouse (R/L):')
        temp = {tag: {'SPT_Pattern': SPT_Spout, 'SPT_level': int(SPT_lvl)}}
        self.mice_config.update(temp)

    def remove_mouse(self):
        try:
            tagreader = TagReader(RFID_serialPort, RFID_doCheckSum, timeOutSecs=RFID_timeout, kind=RFID_kind)
        except Exception as e:
            raise e
        i = 0
        print('Scan mice to remove now')
        while i < 1:
            try:
                tag = tagreader.readTag()
                i += 1
                print(tag)
            except ValueError as e:
                print(str(e))
        del self.mice_config[str(tag)]

    def write_log_config(self):
        if not os.path.exists(self.cage + '/' + 'SPT_mouse_past_config.csv'):
            with open(self.cage + '/' + 'SPT_mouse_past_config.csv', 'w') as file:
                file.write('Date,Tag,SPT_level,SPT_Pattern\n')
            log_date = dt.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            for k, v in self.mice_config.items():
                file.write(log_date + ',' + str(k) + ',' + str(v['SPT_level']) + ',' + v['SPT_Pattern'] + '\n')
        else:
            with open(self.cage + '/' + 'SPT_mouse_past_config.csv', 'a') as file:
                log_date = dt.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                for k, v in self.mice_config.items():
                    file.write(log_date + ',' + str(k) + ',' + str(v['SPT_level']) + ',' + v['SPT_Pattern'] + '\n')

    def spout_swtich(self):
        self.write_log_config()
        for k, v in self.mice_config.items():
            if self.mice_config[k]['SPT_Pattern'] == 'R':
                self.mice_config[k]['SPT_Pattern'] = 'L'
            elif self.mice_config[k]['SPT_Pattern'] == 'L':
                self.mice_config[k]['SPT_Pattern'] = 'R'

    def spt_levelup(self):
        n_level = input('Enter level for all mice to increase to: ')
        for k, v in self.mice_config.items():
            self.mice_config[k]['SPT_level'] = int(n_level)


###############
class task_settings():
    # default settings
    tag_in_range_pin_def = 17
    solenoid_pin_LW_def = 13
    solenoid_pin_LS_def = 13
    solenoid_pin_RW_def = 13
    solenoid_pin_RS_def = 13
    buzzer_pin_def = 25
    hours_def = 1
    reward_amount = 0.4
    vid_folder_def = '\home\Documents\SPTvids'

    def __init__(self, task_name):
        '''
        Loads a JSON config file if available, creates a new JSON of that name otherwise
        :param task_name: Name of the config file to use or create
        :return None
        '''
        self.task_name = task_name
        self.config_file_name = 'SPT_' + self.task_name + '.jsn'
        if not os.path.exists(self.config_file_name):
            print('Task settings file ' + self.task_name + ' not found')
            temp = input('Do you want to create a new file? Y to create file, any key to quit')
            if temp == 'y' or temp == 'Y':
                self.task_config = self.config_user_get()
                pi_IO.dict_to_file(self.task_config, self.config_file_name)
            else:
                return
        else:    
            self.task_config = pi_IO.file_to_dict(self.config_file_name)
            print('SPT_' + self.task_name + ' settings loaded')

    def config_user_get(self, starterDict={}):
        '''
        Gets user configuration.
        :param starterDict: empty dictionary if not specified
        :return: starterDict: dict after user modification
        '''
        # RFID pin
        tag_in_range_pin = starterDict.get('tag_in_range_pin', self.tag_in_range_pin_def)
        tempInput = input('Set tag in range pin(currently {0}): '.format(tag_in_range_pin))
        if tempInput != '':
            tag_in_range_pin = int(tempInput)
        starterDict.update({'tag_in_range_pin': tag_in_range_pin})

        # Left solenoids
        solenoid_pin_LW = starterDict.get('solenoid_pin_LW', self.solenoid_pin_LW_def)
        tempInput = input('What is the pin for the left water valve?(currently {0})'.format(solenoid_pin_LW))
        if tempInput != '':
            solenoid_pin_LW = int(tempInput)
        starterDict.update({'solenoid_pin_LW': solenoid_pin_LW})
        solenoid_pin_LS = starterDict.get('solenoid_pin_LS', self.solenoid_pin_LS_def)
        tempInput = input('What is the pin for the left sucrose/restricted valve?(currently {0})'.format(solenoid_pin_LS))
        if tempInput != '':
            solenoid_pin_LS = int(tempInput)
        starterDict.update({'solenoid_pin_LS': solenoid_pin_LS})

        # Right solenoids
        solenoid_pin_RW = starterDict.get('solenoid_pin_RW', self.solenoid_pin_RW_def)
        tempInput = input('What is the pin for the right water valve?(currently {0})'.format(solenoid_pin_RW))
        if tempInput != '':
            solenoid_pin_RW = int(tempInput)
        starterDict.update({'solenoid_pin_RW': solenoid_pin_RW})
        solenoid_pin_RS = starterDict.get('solenoid_pin_RS', self.solenoid_pin_RS_def)
        tempInput = input('What is the pin for the right sucrose/restricted valve?(currently {0}): '.format(solenoid_pin_RS))
        if tempInput != '':
            solenoid_pin_RS = int(tempInput)
        starterDict.update({'solenoid_pin_RS': solenoid_pin_RS})

        #Buzzer
        buzzer_pin = starterDict.get('buzzer_pin', self.buzzer_pin_def)
        tempInput = input('Set buzzer pin(currently {0}): '.format(buzzer_pin))
        if tempInput != '':
            buzzer_pin = int(tempInput)
        starterDict.update({'buzzer_pin': buzzer_pin})

        #Video folder
        vid_folder = starterDict.get('vid_folder', self.vid_folder_def)
        tempInput = input('Enter the folderin whcih the video is saved to (currently{0}): '.format(vid_folder))
        if tempInput != '':
            vid_folder = tempInput
        starterDict.update({'vid_folder':vid_folder})

        #Timing
        hours = starterDict.get('hours', self.hours_def)
        tempInput = input('Enter the hour for the valve switch? (currently {0})'.format(hours))
        if tempInput != '':
            hours = int(tempInput)
        starterDict.update({'hours': hours})

        #Reward amount
        reward_amount = starterDict.get('reward_amount', self.reward_amount)
        tempInput = input('Enter the reward amount (valve open time in seconds) (currently {0}): '.format(reward_amount))
        if tempInput != '':
            reward_amount = float(tempInput)
        starterDict.update({'reward_amount': reward_amount})
        return starterDict

    def change_settings(self):
        pi_IO.show_ordered_dict(self.task_config, self.task_name)
        parameter_change = input('Enter parameter to change: ')
        value_to_change_to = input('Value to change to: ')
        #TODO: test this
        self.task_config[dic[int(parameter_change)]] = eval(
            type(self.task_config[dic[int(parameter_change)]]).__name__ + '(' + str(value_to_change_to) + ')')
        pi_IO.dict_to_file(self.task_config, self.config_file_name)



