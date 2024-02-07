from multiprocessing.sharedctypes import Value
import os
import sys
import asyncio
from fridge_monitor import FridgeWatcher
from ifttt_service import IFTTTService
from render_com_service import RenderComService
from dotenv import load_dotenv

# Loads IFTTT_KEY from .env file
load_dotenv()

SENSOR_NAME =  "GVH5101_334C"
EVENT_NAME = "fridge_alert"
DEFAULT_MAX_TEMP_F = 10.0
DEFAULT_MIN_BATTERY = 25

# initialize web service
def ifttt():
    web_key = os.environ.get('IFTTT_KEY')
    # If there's no key present, we can't request to IFTTT
    if web_key == None:
        print("IFTTT_KEY environment variable not set!")
        sys.exit(1)
    return IFTTTService(EVENT_NAME, web_key)

# initialize monitoring app
def fridge_mon_service():
    return FridgeWatcher(sensor=SENSOR_NAME, temp_limit=max_temp(), batt_limit=min_batt())

def max_temp():
    env_var = os.environ.get('MAX_TEMP_F')
    if type(env_var) is str:
        try:
            output = float(env_var)
            return output
        except ValueError:
            pass

    return DEFAULT_MAX_TEMP_F
    
def min_batt():
    env_var = os.environ.get('MIN_BATTERY')
    if type(env_var) is str:
        try:
            min_batt = int(env_var)
            if min_batt > 70 | min_batt < 10:
                raise ValueError
            return min_batt
        except ValueError:
            pass

    return DEFAULT_MIN_BATTERY
    

async def main():
    notifier = ifttt()

    # initialize Fridge watcher
    watcher = FridgeWatcher(sensor=SENSOR_NAME, temp_limit=max_temp(), batt_limit=min_batt())

    # Discover fridge
    initial_readings = await watcher.discover()

    try:
        # Notify of monitoring start/initial status
        notifier.post(f'{SENSOR_NAME} monitoring established', initial_readings)

        # Monitoring loop
        while True:
            alert, readings = await watcher.monitor()
            if alert != "":
                notifier.post(alert, readings)
    finally:
        # Fault handling
        notifier.post(f'{SENSOR_NAME} monitoring disabled')

if __name__ == "__main__":
    asyncio.run(main())