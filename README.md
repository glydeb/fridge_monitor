# Refrigerator Monitor

A python app to use a raspberry pi with bluetooth as a scanner for the Govee H5101 Temp & Humidity sensor, and issue alerts though IFTTT.

Uses bleak to scan for the GVH5101 - credit to the code of https://github.com/Thrilleratplay/GoveeWatcher and https://github.com/tsaitsai/govee_bluetooth_gateway for help with the scanning.

## Program flow

1. Discover the sensor
2. Alert the user that monitoring has started
3. Monitoring loop:
    a. Sleep for the delay time (initially 5 minutes)
    b. Scan BLE for 1 minute
    c. Examine results
    d. Set to alert if sensor isn't found
    e. Set to alert if temperature is above the setpoint (default: 20 deg F)
    f. Set to alert if sensor battery is below setpoint (default: 25%)
    g. Send alert to IFTTT if alert is set
    h. clear scanning results
    i. Set delay longer if alert was sent (so we don't flood with alerts)