import time
import asyncio
from btle_scanner import SensorScanner
from sensors.GoveeSensor import GoveeReading

class DeviceNotFoundError(Exception):
    print("Device not found")
    pass

class FridgeWatcher:
    def __init__(self, sensor: str, temp_limit: float=20.0, batt_limit: int=30):
        self.sensor = sensor
        self.temp_limit = temp_limit
        self.batt_limit = batt_limit
        self.scanner = SensorScanner(60.0, "GVH5101_7F32")
        self.delay = 300
        self.last_alert_day = time.gmtime(time.time())[2] # day of month
    
    def reset_last_alert(self):
        self.last_alert_day = time.gmtime(time.time())[2] # day of month

    # set delay until next scan
    def set_delay(self, report: GoveeReading=None, healthy: bool=False):
        if healthy:
            # TODO: scale to safety margin from setpoints
            self.delay = 300
        else:
            # scale up to daily alerts if not corrected
            self.delay = min([self.delay * 4, 3600 * 24])

    async def discover(self, retries: int=3):
        device = await self.scanner.scan()
        # for now, just loop until you find the right reading
        if device != None:   
            report = GoveeReading(device[0], device[1])
            self.set_delay(report)
            # set initial day of month for alerting
            self.reset_last_alert()
            return report
        if retries == 0:
            print("device not found - exiting")
            raise DeviceNotFoundError
        else:
            print("device not found - looking again")
            retry = await self.discover(retries - 1)
            return retry

    async def monitor(self, retries: int=2):
        await asyncio.sleep(self.delay)
        device = await self.scanner.scan()
        reading = self.our_sensor_reading(device)
        status = self.health_check(reading)
        return status

    def our_sensor_reading(self, device):
        our_reading = None
        if device != None:
            our_reading = GoveeReading(detection[0], detection[1])
        return our_reading

    def health_check(self, reading: GoveeReading):
        healthy = True
        if reading == None:
            print("Sending loss of contact")
            alert = f'Lost contact with {self.sensor}'
            healthy = False

        elif reading.temp_F() > self.temp_limit:
            print("sending temp alarm")
            alert = 'High temp alert!'
            healthy = False

        elif reading.battery() < self.batt_limit:
            print("sending battery alarm")
            alert = 'Sensor Battery Failing!'
            healthy = False

        if healthy:
            alert = ""
        self.set_delay(reading, healthy)
        return alert, reading