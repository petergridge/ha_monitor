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
$ install psutil
$ pip install psutil
'''

from time import sleep
import sys
from socket import gethostname
import requests
import psutil

# Configuration
DEBUG = 0 #set to 1 to get debug output

WAIT_TIME = 60 #[s] Time to wait between each refresh
REFRESH_ALL = 600 #[s] time to send all states even if unchanged
HAServer = "http://192.168.1.62:8123" #Home assistant server
#ha_monitor long lived token
AUTHKEY = "YOUR.AUTHKEY.eyJpc3MiOiI4OGY1MDdkNjY0MmE0NTBjYTU1MWFlNzlhZWEyZDY3MiIsImlhdCI6MTU4MTA0OTIwMSwiZXhwIjoxODk2NDA5MjAxfQ.oo1SLDPXH2Nx5pnAkzeGEbdgkZpzqBoHuRU9E3i4ex0"
HOSTNAME = gethostname()

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
        response = requests.post(url, headers=headers, json=data)
        if DEBUG == 1:
            print(url, response, state)
        if str(response) == '<Response [201]>':
            #Home Assistant is creating this for the first time so ensure all the states are written
            #states are written if this is a restart of HA
            return 1
    except(requests.exceptions.Timeout):
        #HA is slow, just keep retrying
        if DEBUG == 1:
            print('requests.exceptions.Timeout')
        pass #do nothing
    except(requests.exceptions.ConnectionError):
        #This is the exception I get when HA is rebooting, just keep retrying
        #and force a refresh of all states
        if DEBUG == 1:
            print('requests.exceptions.ConnectionError')
        return 1
        pass #do nothing

try:
    while (1):
        #Only POST a value if the state has changed or every REFRESH_ALL/WAIT_TIME cycles
        #to minimise the network taffic

        # Read CPU temperature
        cpuTempFile=open("/sys/class/thermal/thermal_zone0/temp","r")
        cpuTemp=float(format(float(cpuTempFile.read())/1000,'.2f'))
        cpuTempFile.close()
        if cpuTemp != lastcpuTemp:
            ret = HAPost("temperature",cpuTemp,"°C","CPU Temp","mdi:thermometer")
            lastcpuTemp = cpuTemp

        # Read CPU processor use
        cpu_percent = psutil.cpu_percent()
        if cpu_percent != lastcpupercent:
            HAPost("cpu_percent",cpu_percent,"%","Processor Use","mdi:memory")
            lastcpupercent = cpu_percent

        #Read Memory use
        virtual_memory = psutil.virtual_memory()[2]
        if virtual_memory != lastvirtualmamory:
            ret = HAPost("memory_used",virtual_memory,"%","Memory Use","mdi:memory")
            lastvirtualmamory = virtual_memory

        #Read Disk use
        disk_usage = psutil.disk_usage('/')[3]
        if disk_usage != lastdiskusage:
            ret = HAPost("disk_used",disk_usage,"%","Disk Use","mdi:harddisk")
            lastdiskusage = disk_usage

        count = count + 1
        if count >= REFRESH_ALL/WAIT_TIME or ret == 1:
            if DEBUG == 1:
                print('Resend All Sensors')
            #force next cycle to send all states
            count = 0
            lastcpuTemp = 0
            lastcpupercent = 0
            lastvirtualmamory = 0
            lastdiskusage = 0

        # Wait until next refresh
        sleep(WAIT_TIME)

# If a keyboard interrupt occurs (ctrl + c)
except(KeyboardInterrupt):
    print("PI Monitor Interupted")
    sys.exit()
except:
    if DEBUG == 1:
        print("Unexpected error:", sys.exc_info()[0])
    raise
