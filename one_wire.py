#!/usr/bin/python
from RPLCD.i2c import CharLCD
from gpiozero import RotaryEncoder, Button, Buzzer
import threading
import os
import sys
import time


class One_Wire(threading.Thread):
    Device_Temp = ['00.0','00.0','00.0']
    Device_ID = []

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        base_dir = '/sys/devices/w1_bus_master1/'
        dir = open(base_dir + 'w1_master_slaves' , 'r')
        for x in range(3):
            self.Device_ID.append(dir.readline()[:15])                  
        dir.close()

        while True:
            # Find 1-Wire sensor
            i = 0 
            for x in self.Device_ID:
                self.Device_Temp[i] = self.read_temp(base_dir + x)
                i = i + 1 

            time.sleep(2)      
    
    def read_temp(self, device_value):
        
        # Read temp of sensor
        file = open(device_value + '/w1_slave', 'r')
        filecontent = file.read()
        file.close()

        # Format temp
        stringvalue = filecontent.split("\n")[1].split(" ")[9]
        temp = float(stringvalue[2:]) / 1000

        return (str('%3.1f' % temp))

class Stop_Watch(threading.Thread):
    Display_value = ['0','30','00']
    Timer_running = False
    Timer_value = 1800

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("stop watch running")
        rotor = RotaryEncoder(16, 20)
        rotor.steps = 1800
        btn = Button(21, pull_up=False)
        
        done = threading.Event()

        btn.when_released = self.toggle_timer

        rotor.when_rotated_clockwise = self.rotate_clockwise
        rotor.when_rotated_counter_clockwise = self.rotate_counter_clockwise

        done.wait()

    def toggle_timer(self):
        if self.Timer_running == False:
            self.Timer_running = True
        else:
            self.Timer_running = False

        print("Timer_running: " + str(self.Timer_running))
            
    def rotate_clockwise(self):
        if self.Timer_value < 9000 and self.Timer_running == False:
            self.Timer_value = self.Timer_value + 60
            self.format_time()
            
    def rotate_counter_clockwise(self):
        if self.Timer_value > 60 and self.Timer_running == False:
            self.Timer_value = self.Timer_value - 60
            self.format_time()

    def format_time(self):
        hours = int(self.Timer_value / 3600)
        minutes = int((self.Timer_value-hours*3600) / 60)
        seconds = int((self.Timer_value-hours*3600-minutes*60))

        self.Display_value[0] = str(hours)
        self.Display_value[1] = str(minutes)
        self.Display_value[2] = str(seconds)




def main():

    try:
        
        thread_one_wire = One_Wire()
        thread_one_wire.start()

        thread_stop_watch = Stop_Watch()
        thread_stop_watch.start()
        
        lcd = CharLCD('PCF8574', 0x27)
        degree = (0b00010, 0b00101, 0b00101, 0b00010, 0b00000, 0b00000, 0b00000, 0b00000)
        lcd.create_char(0, degree)
        
        sandclock = (0b00000, 0b11111, 0b01010, 0b00100, 0b00100, 0b01010, 0b11111, 0b00000)
        lcd.create_char(1, sandclock)
        
        lcd.cursor_pos = (0, 0)
        lcd.write_string('Temp 1: 00.0\x00C')
        lcd.cursor_pos = (1, 0)
        lcd.write_string('Temp 2: 00.0\x00C')
        lcd.cursor_pos = (2, 0)
        lcd.write_string('Temp 3: 00.0\x00C')
        lcd.cursor_pos = (3, 0)
        lcd.write_string('Timer : 00:00:00')

        Display_ref = ['0','02','03']

        print("End program with CRLT+C !!")

        while(True):
            for i in range(3):
                lcd.cursor_pos = (i, 8)
                lcd.write_string(thread_one_wire.Device_Temp[i])

          
            if Display_ref[0] != thread_stop_watch.Display_value[0]:
                lcd.cursor_pos = (3, 9)
                Display_ref[0] = thread_stop_watch.Display_value[0]
                lcd.write_string(thread_stop_watch.Display_value[0])
                #print("treffer hour")
            
            
            if Display_ref[1] != thread_stop_watch.Display_value[1]:
                lcd.cursor_pos = (3, 11)
                Display_ref[1] = thread_stop_watch.Display_value[1]
                #print("treffer min")
                if len(thread_stop_watch.Display_value[1]) > 1:
                    lcd.write_string(thread_stop_watch.Display_value[1])
                else:
                    lcd.write_string("0" + thread_stop_watch.Display_value[1])
            
            if Display_ref[2] != thread_stop_watch.Display_value[2]:
                lcd.cursor_pos = (3, 14)
                Display_ref[2] = thread_stop_watch.Display_value[2]
                #print("treffer sec")
                if len(thread_stop_watch.Display_value[2]) > 1:
                    lcd.write_string(thread_stop_watch.Display_value[2])
                else:
                    lcd.write_string("0" + thread_stop_watch.Display_value[2])
            
            if thread_stop_watch.Timer_running == True: 
                lcd.cursor_pos = (3, 18)
                lcd.write_string('\x01')
            else:
                lcd.cursor_pos = (3, 18)
                lcd.write_string(' ')

            time.sleep(.5)

    except Exception as err:
        print(err)


if __name__ == "__main__":
    main()