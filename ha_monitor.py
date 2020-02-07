#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Requirements
create a permanent key in HA and copy into the AUTHKEY
Update the HAServer URL
Review the WAIT_TIME and HOSTNAME if you want to change them

Sensor format is:
  sensor.hostname_temperature
  sensor.hostname_cpu_percent
  sensor.hostname_memory_used
  sensor.hostname_disk_used

Install psutil if required

#install psutil
#pip install psutil
'''

import time
import sys
import socket
from requests import post
import psutil

# Configuration

WAIT_TIME = 60 #[s] Time to wait between each refresh
HAServer = "http://192.168.1.62:8123" #Home assistant server
AUTHKEY = "YOURAUTHKEY.eyJpc3MiOiI5N2QyMzE4ZTRlOTU0YWMyYTAyODdkOGZlZTk4OWYzMyIsImlhdCI6MTU4MDk0NDkyNiwiZXhwIjoxODk2MzA0OTI2fQ.SbFw6bHDlwTjN0N7xmHsL4d23OVOjIh5pzaH2GeFkt8"
HOSTNAME = socket.gethostname()

lastcpuTemp = 0
lastcpupercent = 0
lastvirtualmamory = 0
lastdiskusage = 0
count = 0

#function manages POST to home assistant api
def HAPost(sensorname,state,unitmeasure,friendlyname,icon):
    url = HAServer + '/api/states/sensor.' + HOSTNAME+ "_" + sensorname
    headers = {'Authorization': 'Bearer ' + AUTHKEY,
               'content-type': 'application/json'}
    attributes = {"unit_of_measurement":unitmeasure,
                  "friendly_name":friendlyname,
                  "icon":icon}
    data = {'state':str(state),
            'attributes':attributes}
    try:
      response = post(url, headers=headers, json=data)
    except(Timeout):
      #HA is not available, rebooting maybe, just keep retrying
      pass #do nothing

try:
    while (1):
        #Only POST a value if the temp has changed or every 10 cycles
        #to minimise the network taffic
        #on restart of Home Assistant it may take 10 cycles to get 
        #all the sensors back

        # Read CPU temperature
        cpuTempFile=open("/sys/class/thermal/thermal_zone0/temp","r")
        cpuTemp=float(cpuTempFile.read())/1000
        cpuTempFile.close()

        if cpuTemp != lastcpuTemp:
            HAPost("temperature",cpuTemp,"C","CPU Temp","mdi:thermometer")
            lastcpuTemp = cpuTemp
        if psutil.cpu_percent() != lastcpupercent:
            HAPost("cpu_percent",psutil.cpu_percent(),"%","Processor Use","mdi:memory")
            lastcpupercent = psutil.cpu_percent()
        if psutil.virtual_memory()[2] != lastvirtualmamory:
            HAPost("memory_used",psutil.virtual_memory()[2],"%","Memory Use","mdi:memory")
            lastvirtualmamory = psutil.virtual_memory()[2]
        if psutil.disk_usage('/')[3] != lastdiskusage:
            HAPost("disk_used",psutil.disk_usage('/')[3],"%","Disk Use","mdi:harddisk")
            lastdiskusage = psutil.disk_usage('/')[3]
        
        count = count + 1
        if count >= 10:
            count = 0
            lastcpuTemp = 0
            lastcpupercent = 0
            lastvirtualmamory = 0
            lastdiskusage = 0          

        # Wait until next refresh
        time.sleep(WAIT_TIME)

# If a keyboard interrupt occurs (ctrl + c)
except(KeyboardInterrupt):
    print("PI Monitor Interupted")
    sys.exit()
