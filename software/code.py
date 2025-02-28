# Guy
# code.py
# Copyright 2025, Jonathan Koren
# Licensed under the Gnu Public License v3
#
# Find the array `modules` and add your own modules there.

import os
import wifi
import ssl
import socketpool
import adafruit_requests
from adafruit_qualia.graphics import Graphics, Displays
import displayio
import time

from weather import Weather
from opensky import OpenSky

##############################################################################

def touch_area(x, size):
    left = size // 4
    right = left * 3
    # These are reversed because the touch screen is upsdide down
    if x < left:
        return 1
    elif x > right:
        return -1
    else:
        return 0

##############################################################################

# Connect to network
wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
print(f"Connected to {os.getenv('CIRCUITPY_WIFI_SSID')}")
context = ssl.create_default_context()

# Create the face
graphics = Graphics(Displays.ROUND21, default_bg=0x103260, auto_refresh=True, rotation=180)

next_refresh = 0
next_touch = 0
TOUCH_TTL = 1
ERROR_TIMEOUT = 60
while True:
    try:
        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, context)

        # Edit this array to add your own modules
        modules = [ Weather(os.getenv('WEATHER_URL'), requests, graphics.display.width),
            OpenSky(os.getenv('OPENSKY_LAT_MIN'), os.getenv('OPENSKY_LAT_MAX'),
                os.getenv('OPENSKY_LONG_MIN'), os.getenv('OPENSKY_LONG_MAX'),
                requests, graphics.display.width) ]
        current_module_idx = 0

        group_caches = [None] * len(modules)

        while True:
            current_module = modules[current_module_idx]

            ttl = None
            group = None
            if graphics.touch.touched and time.time() > next_touch:
                side = touch_area(graphics.touch.touches[0]['x'], graphics.display.width)
                print('TOUCH!', side)
                if side != 0:
                    if side < 0:
                        current_module_idx -= 1
                        if current_module_idx < 0:
                            current_module_idx = len(modules) - 1
                    elif side > 0:
                        current_module_idx = (current_module_idx + 1) % len(modules)

                    if group_caches[current_module_idx] is not None:
                        graphics.display.root_group = group_caches[current_module_idx]
                    current_module = modules[current_module_idx]
                    (ttl, group) = current_module.draw(time.time())
                else:
                    (ttl, group) = current_module.tap(graphics.touch.touches[0]['x'], graphics.touch.touches[0]['y'])

                next_touch = time.time() + TOUCH_TTL
            elif time.time() > next_refresh:
                (ttl, group) = current_module.draw(time.time())
                group_caches[current_module_idx] = group

            if ttl is not None:
                graphics.display.root_group = group
                next_refresh = time.time() + ttl


    except RuntimeError as e:
        print(f'caught {e}')
        time.sleep(ERROR_TIMEOUT)
