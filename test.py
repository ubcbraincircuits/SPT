from time import time, sleep
import board
import busio
from SPT import SPT
import RFIDTagReader
from RFIDTagReader import TagReader
import RPi.GPIO as GPIO 
import datetime as dt
import adafruit_mpr121 as mpr121
'''
Default variables to be read by json file
'''
serialPort = '/dev/ttyUSB0'
tag_in_range_pin=18
selenoid_pin_LW=26
selenoid_pin_LS=13
selenoid_pin_RW=21
selenoid_pin_RS=12
i2c=busio.I2C(board.SCL,board.SDA)
lickdector=mpr121.MPR121(i2c,address=0x5A)
selenoid_RW=SPT.selenoid(selenoid_pin_RW)
selenoid_RS=SPT.selenoid(selenoid_pin_RS)
selenoid_LW=SPT.selenoid(selenoid_pin_LS)
selenoid_LS=SPT.selenoid(selenoid_pin_LW)
buzzer_pin=24
globalReader = None
globalTag = 0
vid_folder='/home/Documents/'
k_day_hour=19
'''
sample mice dic for json
SPT_levels
    0: with entry reward, with both sides just giving out water

'''
mice={801010565:{'SPT_level':1,'SPT_pattern':'R'}}
"""
Main loop for SPT 
Need to add camera and scale in loop
Need to think of open design for tunnel
"""
vs=SPT.piVideoStream(folder='/home/pi/Documents')
vs.cam_setup()
buzzer=SPT.buzzer(buzzer_pin,1500,50)
hours=5
def main ():
    global globalReader
    global globalTag
    globalReader = TagReader(serialPort, True, timeOutSecs = 0.05, kind='ID')
    globalReader.installCallback (tag_in_range_pin)
    cage=input('cage?')
    txtspacer=input('txt spacer?')
    now=dt.datetime.now()
    while True:
        try:
            log=SPT.data_logger(cage,txtspacer)
            now=dt.datetime.now()
            print ("Waiting for mouse....")
            while dt.datetime.now()-now < dt.timedelta(minutes=hours):
                #try:
                    #while RFIDTagReader.globalTag == 0:
                    #    sleep (0.02)
                if RFIDTagReader.globalTag == 0:
                    sleep (0.02)
                else:
                    tag = RFIDTagReader.globalTag
                    filename=vs.record(tag)
                    log.event_outcome(mice,str(tag),'VideoStart',filename)
                    if mice[tag]['SPT_level']== 0:
                        if mice[tag]['SPT_pattern']=='R':
                            selenoid_LW.activate(0.5)
                            log.event_outcome(mice,str(tag),'Entered','Entry_Reward')
                            pass
                        elif mice[tag]['SPT_pattern']=='L':
                            selenoid_RW.activate(0.5)
                            log.event_outcome(mice,str(tag),'Entered','Entry_Reward')
                            pass
                    else:
                        log.event_outcome(mice,str(tag),'Entered','No_Entry_Reward')
                    while RFIDTagReader.globalTag == tag:
                        while GPIO.input(tag_in_range_pin) == GPIO.HIGH:
                            if lickdector[0].value:
                                if mice[tag]['SPT_level'] ==0:
                                    selenoid_RW.activate(0.2)
                                    log.event_outcome(mice,str(tag),'licked-Rightside','Water_Reward')
                                elif mice[tag]['SPT_level'] ==1:
                                    if mice[tag]['SPT_pattern']=='R':
                                        selenoid_RW.activate(0.2)
                                        log.event_outcome(mice,str(tag),'licked-Rightside','Water_Reward')
                                    elif mice[tag]['SPT_pattern']=='L':
                                        #speaker on 
                                        print('Speaker on\n')
                                        buzzer.buzz()
                                        log.event_outcome(mice,str(tag),'licked-Rightside','No_Reward')
                                        sleep(0.2)
                                elif mice[tag]['SPT_level'] ==2:
                                    if mice[tag]['SPT_pattern']=='R':
                                        selenoid_RW.activate(0.2)
                                        log.event_outcome(mice,str(tag),'licked-Rightside','Sucrose_Reward')
                                    elif mice[tag]['SPT_pattern']=='L':
                                        selenoid_LW.activate(0.2)
                                        log.event_outcome(mice,str(tag),'licked-Rightside','Water_Reward')
                            elif lickdector[1].value:
                                if mice[tag]['SPT_level'] ==0:
                                    selenoid_LW.activate(0.2)
                                    log.event_outcome(mice,str(tag),'licked-Leftside','Water_Reward')
                                elif mice[tag]['SPT_level'] ==1:
                                    if mice[tag]['SPT_pattern']=='R':
                                        print('Speaker on\n')
                                        buzzer.buzz()
                                        log.event_outcome(mice,str(tag),'licked-leftside','No_Reward')
                                        sleep(0.2)
                                    elif mice[tag]['SPT_pattern']=='L':
                                        selenoid_LW.activate(0.2)
                                        log.event_outcome(mice,str(tag),'licked-Leftside','Water_Reward')
                                elif mice[tag]['SPT_level'] ==2:
                                    if mice[tag]['SPT_pattern']=='R':
                                        selenoid_LW.activate(0.2)
                                        log.event_outcome(mice,str(tag),'licked-Leftside','Water_Reward')
                                    elif mice[tag]['SPT_pattern']=='L':
                                        selenoid_LS.activate(0.2)
                                        log.event_outcome(mice,str(tag),'licked-Leftside','Sucrose_Reward')
                            else:
                                sleep(0.05)
                        vs.stop_record()
                        log.event_outcome(mice,str(tag),'VideoEnd',filename)
                    ###sleep time must match reward and buzzer sleep time
                    sleep(0.02)
                    log.event_outcome(mice,str(tag),'Exit','None')
                    #print('Waiting for mouse')
                    print('end')
        except KeyboardInterrupt:
            del globalReader
            print ("Quitting")
            break
if __name__ == '__main__':
   main()
