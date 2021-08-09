#!/usr/bin/python
import threading
import os
import sys
import time


class One_Wire(threading.Thread):
    Device_Temp = ['Error','Error','Error']
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
            for x in self.Device_ID:
                self.Device_Temp = self.read_temp(base_dir + x)
                   
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


def main():

    thread_one_wire = One_Wire()

    try:
        thread_one_wire.start()

    except Exception as err:
        print(err)


if __name__ == "__main__":
    main()












