## Web server demo
import time

#from machine import Pin
import network

import gc
gc.collect()

import config
import Web
import Control
from Logger import Logger

# Setup Logging
Logger.setup_logger("MicroHex")
Logger.info("Booting up")

# Turn on WiFi and connect
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(config.SSID, config.PASSWORD)

# Wait for Wi-Fi connection
connection_timeout = 10
while connection_timeout > 0:
    if wifi.status() >= 3:
        break
    connection_timeout -= 1
    print('Waiting for Wi-Fi connection...')
    time.sleep(1)

# Check if connection is successful
if wifi.status() != 3:
    Logger.err("Failed to establish a network connection")
    raise RuntimeError('Failed to establish a network connection')
else:
    print('WiFi connection successful!')
    network_info = wifi.ifconfig()
    print('IP address:', network_info[0])
    Logger.info(f"IP Adress: {network_info[0]}")

control = Control.Control()

server = Web.Server(control)

while True:
    try:
        server.poll()
    except Exception as e:
        Logger.err(f"Server Error: {str(e)}")
    
    try:
        control.step()
    except Exception as e:
        Logger.err(f"Control step: {str(e)}")
