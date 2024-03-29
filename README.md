# Refrigerator Monitor

A python app to use a raspberry pi with bluetooth as a scanner for the Govee H5101 Temp & Humidity sensor, and issue alerts though IFTTT.

Uses bleak to scan for the GVH5101 - credit to the code of https://github.com/Thrilleratplay/GoveeWatcher and https://github.com/tsaitsai/govee_bluetooth_gateway for help with the scanning.

## Program flow

1. Discover the sensor
2. Alert the user that monitoring has started
3. Monitoring loop:
*   Sleep for the delay time (initially 5 minutes)
*   Scan BLE for 1 minute
*   Examine results
*   Set to alert if sensor isn't found
*   Set to alert if temperature is above the setpoint (default: 20 deg F)
*   Set to alert if sensor battery is below setpoint (default: 25%)
*   Send alert to IFTTT if alert is set
*   clear scanning results
*   Set delay longer if alert was sent (so we don't flood with alerts)

## Installation/Setup
To set up the Refrigerator Monitor on a Raspberry Pi, follow these steps:

1. Set up a Raspberry Pi with the latest version of Raspbian Lite; you can find the installation guide [here](https://www.raspberrypi.org/documentation/installation/installing-images/README.md).  We recommend using a Pi Zero W for this project, as it is low-cost and has built-in Bluetooth.  Lite is recommended because you can use a smaller SD card and it has less overhead.
2. Install git and pip: `sudo apt-get install git python3-pip python3-venv`
3. Clone the repository: `git clone https://github.com/fridge_monitor.git`
4. Navigate to the project directory: `cd fridge_monitor`
5. Create a virtual environment: `python3 -m venv ./.venv`
6. Activate the virtual environment: `source ./.venv/bin/activate`
7. Install the required dependencies: `pip3 install -r requirements.txt`
8. Create a .env file in the fridge_monitor directory with the following contents:
```
SENSOR_NAME=your_sensor_name (e.g. GVH5101_XXXX, where XXXX is the unique hexadecimal digits for your sensor)
FRIDGEMON_USER=your_user_name, given to you by the relay server admin (not necessary if you are using the IFTTT service)
MAX_TEMP_F=10.0 (the app will alert if the temperature is above this value)
MIN_BATTERY=25 (the app will alert if the remaind charge in the battery is below this value)
SERVICE=render (If you are using the new render server)
EVENT_NAME=the ifttt event name (e.g. fridge_alert). Not needed if you are using the new render server
IFTTT_KEY=your_ifttt_key (not needed if you are using the new render server)    
```
9. Copy the fridge.service file to /etc/systemd/system: `sudo cp fridge.service /etc/systemd/system`
10. Start the service: `sudo systemctl start fridge` (you can stop the service with `sudo systemctl stop fridge`)
    You should now start getting alerts - the first will be a "monitoring started" alert.
11. Enable the service to start on boot: `sudo systemctl enable fridge`
    This will start the service on boot, so you don't have to manually start it after a power outage.
12. Reboot the Pi: `sudo reboot`
    You should again get a "monitoring started" alert after the reboot.


