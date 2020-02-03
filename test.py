from time import time, sleep
import board
import busio
import SPT 
import RFIDTagReader
from RFIDTagReader import TagReader
import RPi.GPIO as GPIO 
import datetime as dt
import adafruit_mpr121 as mpr121
import sys
import os


#Main function to run SPT
def main():
    global globalReader
    global globalTag
    global cage
    global log
    global mice_dic
    globalReader = TagReader(serialPort, True, timeOutSecs = 0.05, kind='ID')
    globalReader.installCallback (tag_in_range_pin)
    now=dt.datetime.now()
    mice_dic=SPT.mice_dict(cage)
    txtspacer=input('txt spacer?')
    while True:
        # loops to check date and if date passes the define time settings, a new day/file is started
        now=dt.datetime.now()
        print ("Waiting for mouse....")
        log=SPT.data_logger(cage,txtspacer)
        #switches the spout for L/R every indicated time interval (in hours)
        mice_dic.spout_swtich()
        while dt.datetime.now()-now < dt.timedelta(minutes=hours*60):
            if RFIDTagReader.globalTag == 0:
                sleep (0.02)
            else:
                tag = RFIDTagReader.globalTag
                filename=vs.record(tag)
                print(mice_dic.mice_config)
                print(str(tag))
                print(filename)
                log.event_outcome(mice_dic.mice_config,str(tag),'VideoStart',filename)
                # provides the mouse at level 0 an entry reward; the reward is given randomly at r or l at 50% each
                if mice_dic.mice_config[str(tag)]['SPT_level']== 0:
                    if mice_dic.mice_config[str(tag)]['SPT_Pattern']=='R':
                        solenoid_LW.activate(0.5)
                        log.event_outcome(mice_dic.mice_config,str(tag),'Entered','Entry_Reward')
                        pass
                    elif mice_dic.mice_config[str(tag)]['SPT_Pattern']=='L':
                        solenoid_RW.activate(0.5)
                        log.event_outcome(mice_dic.mice_config,str(tag),'Entered','Entry_Reward')
                        pass
                else:
                    log.event_outcome(mice_dic.mice_config,str(tag),'Entered','No_Entry_Reward')
                #tag is read and checks the mouse spt level
                #level 0: a water reward is given
                #level 1: only one the spt pattern spout will dispense water, licking the other will give a buzz
                #level 2: the spt preference test, spt dispensed at the spt pattern spout
                while RFIDTagReader.globalTag == tag:
                    while GPIO.input(tag_in_range_pin) == GPIO.HIGH:
                        if lickdector[0].value:
                            if mice_dic.mice_config[str(tag)]['SPT_level'] ==0:
                                solenoid_RW.activate(0.1)
                                log.event_outcome(mice_dic.mice_config,str(tag),'licked-Rightside','Water_Reward')
                            elif mice_dic.mice_config[str(tag)]['SPT_level'] ==1:
                                if mice_dic.mice_config[str(tag)]['SPT_Pattern']=='R':
                                    solenoid_RW.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(tag),'licked-Rightside','Water_Reward')
                                elif mice_dic.mice_config[str(tag)]['SPT_Pattern']=='L':
                                    #speaker on 
                                    print('Speaker on\n')
                                    buzzer.buzz()
                                    log.event_outcome(mice_dic.mice_config,str(tag),'licked-Rightside','No_Reward')
                                    sleep(0.2)
                            elif mice_dic.mice_config[str(tag)]['SPT_level'] ==2:
                                if mice_dic.mice_config[str(tag)]['SPT_Pattern']=='R':
                                    solenoid_RW.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(tag),'licked-Rightside','Sucrose_Reward')
                                elif mice_dic.mice_config[str(tag)]['SPT_Pattern']=='L':
                                    solenoid_LW.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(tag),'licked-Rightside','Water_Reward')
                        elif lickdector[1].value:
                            if mice_dic.mice_config[str(tag)]['SPT_level'] ==0:
                                solenoid_LW.activate(0.1)
                                log.event_outcome(mice_dic.mice_config,str(tag),'licked-Leftside','Water_Reward')
                            elif mice_dic.mice_config[str(tag)]['SPT_level'] ==1:
                                if mice_dic.mice_config[str(tag)]['SPT_Pattern']=='R':
                                    print('Speaker on\n')
                                    buzzer.buzz()
                                    log.event_outcome(mice_dic.mice_config,str(tag),'licked-leftside','No_Reward')
                                    sleep(0.2)
                                elif mice_dic.mice_config[str(tag)]['SPT_Pattern']=='L':
                                    solenoid_LW.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(tag),'licked-Leftside','Water_Reward')
                            elif mice_dic.mice_config[str(tag)]['SPT_level'] ==2:
                                if mice_dic.mice_config[tag]['SPT_Pattern']=='R':
                                    solenoid_LW.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(tag),'licked-Leftside','Water_Reward')
                                elif mice_dic.mice_config[str(tag)]['SPT_Pattern']=='L':
                                    solenoid_LS.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(tag),'licked-Leftside','Sucrose_Reward')
                        else:
                            sleep(0.02)
                vs.stop_record()
                log.event_outcome(mice_dic.mice_config,str(tag),'VideoEnd',filename)
                ###sleep time must match reward and buzzer sleep time
                sleep(0.05)
                log.event_outcome(mice_dic.mice_config,str(tag),'Exit','None')
                print('Waiting for mouse')
               
if __name__ == '__main__':
    #loads the json task file and quites if there is an error
    task_name=input('Enter the task name: ')
    task_settings = SPT.task_settings(task_name)
    try: 
        #reads from task json file loaded
        tag_in_range_pin=task_settings.task_config['tag_in_range_pin']
        solenoid_pin_LW=task_settings.task_config['solenoid_pin_LW']
        solenoid_pin_LS=task_settings.task_config['solenoid_pin_LS']
        solenoid_pin_RW=task_settings.task_config['solenoid_pin_RW']
        solenoid_pin_RS=task_settings.task_config['solenoid_pin_RS']
        buzzer_pin=task_settings.task_config['buzzer_pin']
        vid_folder=task_settings.task_config['vid_folder']
        hours=task_settings.task_config['hours']
        #starts the rest of the hardware
        serialPort = '/dev/ttyUSB0'
        i2c=busio.I2C(board.SCL,board.SDA)
        lickdector=mpr121.MPR121(i2c,address=0x5A)
        solenoid_RW=SPT.solenoid(solenoid_pin_RW)
        solenoid_RS=SPT.solenoid(solenoid_pin_RS)
        solenoid_LW=SPT.solenoid(solenoid_pin_LS)
        solenoid_LS=SPT.solenoid(solenoid_pin_LW)
        globalReader = None
        globalTag = 0
        vs=SPT.piVideoStream(folder=vid_folder)
        vs.cam_setup()
        #may need a better function for the buzzer
        buzzer=SPT.buzzer(buzzer_pin,1500,50)
    except Exception as e: 
        print(e)
        print('Error in iniatializing hardware, please check wiring and task settings')
        print('System shuting down')
        sys.exit()
    #asks for cage name to check cage configs
    cage=input('cage?')
    #if no cage folder (data and past'/current configurations) are found, a new one is created
    if not os.path.exists(cage+'/'):
        os.mkdir(cage+'/')
        print(cage+' Dictionary created')
    mice_dic=SPT.mice_dict(cage) 
    #loop that runs main
    #interrupts to enter SPT menu
    while True:
        try:
            if not os.path.exists(cage+'/'):
                os.mkdir(cage+'/')
                print(cage+' Dictionary created')
            mice_dic=SPT.mice_dict(cage)
            #main function and menue if crt+c
            try: 
                main()
            #need to work on the menu
            # currently doesn't work
            except KeyboardInterrupt:
                #print('1')
                inputStr = '\n************** SPT Manager ********************\nEnter:\n'
                inputStr += '1 to change SPT level for mice\n'
                inputStr += '2 to change SPT task settings\n'
                inputStr += '3 to add mice\n'
                inputStr += '4 to remove mice\n'
                inputStr += 'R to Return to head fix trials\n'
                inputStr += 'Q to quit\n:'
                event = input(inputStr)
                while True:
                    event = input(inputStr)
                    if event == 'r' or event == "R":
                        break
                    elif event == 'q' or event == 'Q':
                        print('Quitting SPT run')
                        sys.exit()
        except Exception as anError:
            print('SPT error:' + str(anError))
            raise anError
        finally:
            print('Quitting SPT run')
            GPIO.cleanup()
            sys.exit()
