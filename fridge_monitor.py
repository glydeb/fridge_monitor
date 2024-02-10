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
        self.scanner = SensorScanner(60.0)
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
        detections = await self.scanner.scan()
        # for now, just loop until you find the right reading
        for detection in detections:
            report = GoveeReading(detection[0], detection[1])
            if report.name == self.sensor:
                self.set_delay(report)
                # set initial day of month for alerting
                self.reset_last_alert()
                return report
        if retries == 0:
            print("device not found - exiting")
            raise DeviceNotFoundError
        else:
            print("device not found - looking again")
            self.discover(retries - 1)

    async def monitor(self, retries: int=2):
        await asyncio.sleep(self.delay)
        detections = await self.scanner.scan()
        status = self.health_check(detections)
        return status

    def our_sensor_reading(self):
        our_reading = None
        detection = self.scanner.findDeviceByName(self.sensor)
        if detection != None:
            our_reading = GoveeReading(detection[0], detection[1])
        return our_reading

    def health_check(self, detections: dict):
        healthy = True
        readings = self.our_sensor_report(detections)
        if readings == None:
            print("Sending loss of contact")
            alert = f'Lost contact with {self.sensor}'
            healthy = False

        elif readings.temp_F() > self.temp_limit:
            print("sending temp alarm")
            alert = 'High temp alert!'
            healthy = False

        elif readings.battery() < self.batt_limit:
            print("sending battery alarm")
            alert = 'Sensor Battery Failing!'
            healthy = False

        if healthy:
            alert = ""
        self.set_delay(readings, healthy)
        return alert, readings