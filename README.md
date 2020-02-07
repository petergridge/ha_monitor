# ha_monitor
Using the Home Assistant REST API (https://developers.home-assistant.io/docs/en/external_api_rest.html) to provide a python script that monitors and publishes data similar to the systemmonitor platform in HA.

The program will update each of four sensors ever minute if they change but will all refresh four sensors every 10 minutes.

The sensor format is:
* sensor.hostname_temperature
* sensor.hostname_cpu_percent
* sensor.hostname_memory_used
* sensor.hostname_disk_used

Two files are provided
* ha_monitor.py
* ha_monitor.service

You will need to modify **ha_monitor.py** to apply your specific configuration.
* Generate and a **Long-Lived Access Token** from your profile in Home Assistant (http://192.168.1.99:8123/profile)
* Copy the key and paste it into the **AUTHKEY** variable in the script
* Update the **HAServer** variable with your Home AssistantURL and port (http://192.168.1.99:8123)
* Review **WAIT_TIME**, currently set to 60 Seconds
* Review the **HOSTNAME** variable, it currently uses the devices Host Name
* Copy the file to an appropriate location on your PI, I use **/home/pi/scripts**
* You can test it by executing the script python **ha_monitor.py**
* Verify using the (http://192.168.1.99:8123/developer-tools/state)

The **ha_monitor.service** is used to create the service that will run the python script
* Review the **WorkingDirectory** to ensure is matches the directory you saved the python file in
* Review the **ExecStart** to ensure it matches you python installation
* Copy the file to **/etc/systemd/system**
* Start the service **sudo systemctl start ha_monitor.service**
* Set the service to start on boot **sudo systemctl enable ha_monitor.service**





