import requests
from sensors.GoveeSensor import GoveeReading

class RenderComService:
    def __init__(self, user: str):
        self.user = user
        self.url = "https://fridge-monitor.onrender.com/api/alert"

    def post(self, message: str, report: GoveeReading = None):
        print(f'Sending Message: {message}')
        temp_text, batt_text = "n/a", "n/a" # default values
        if report != None:
            temp_text = f'{report.temp_F():.1f} deg F'
            batt_text = f'{report.battery()}%'
        body = {
            "user": self.user,
            "message": message,
            "temperature": temp_text,
            "battery": batt_text
        }
        print(f'Constructed body: {body}')
        return requests.post(self.url, json=body, timeout=(10, 240))