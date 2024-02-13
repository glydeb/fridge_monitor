
import asyncio
from sensors.GoveeSensor import GoveeReading
from bleak import *

class SensorScanner:
    def __init__(self, scan_time: float, target_sensor: str = "GVH5101_334C"):
        self.scan_time = scan_time
        self.target_sensor = target_sensor
        self.scanner = BleakScanner()

    async def scan(self):
        await self.scanner.start()
        await asyncio.sleep(self.scan_time)
        await self.scanner.stop()
        result = self.findDeviceByName(self.target_sensor)
        return result

    def findDeviceByName(self, name: str):
        for device in self.scanner.discovered_devices_and_advertisement_data.values():
            print(device[0], device[0].name)
            print(device[1])
            if device[0].name == name:
                return device
        return None
# can be run standalone
if __name__ == "__main__":
    scanner = SensorScanner(30.0, "GVH5101_7F32")

    while True:
        detections = asyncio.run(scanner.scan())
        # print and clear readings
        for detection in detections:
            sensor = GoveeReading(detection[0], detection[1])
            temp_C, humidity, battery = sensor.decode_5101()
            print("sensor: {}, temp: {} degC, rh: {}%, battery: {}%".format(sensor.name, temp_C, humidity, battery))