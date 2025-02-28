# Guy
# opensky.py
# Copyright 2025, Jonathan Koren
# Licensed under the Gnu Public License v3

import displayio
import hashlib
import json

from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.circle import Circle

from scale import linear_scale

def make_simple_text(text):
    '''Creates a displayio.Group that shows a simple line of text.'''
    group = displayio.Group()
    BASE_FONT_SIZE = 24
    font = bitmap_font.load_font(f"Junction-Regular-{BASE_FONT_SIZE}.pcf", displayio.Bitmap)
    font_scale = 1
    color = 0xFF0000
    text_area = label.Label(font, text=text, color=color, scale=font_scale)
    text_area.x = 100
    text_area.y = 100
    group.append(text_area)
    return group

def parse_state(rec):
    keys = ['icao24', 'callsign', 'origin_country', 'time_position',
    'last_contact', 'longitude', 'latitude', 'baro_altitude',
    'on_ground', 'true_track', 'vertical_rate', 'sensors', 'geo_altitude',
    'squawk', 'spi', 'position_source', 'category']
    d = {}
    for i in range(len(rec)):
        d[keys[i]] = rec[i]
    return d

def split_callsign(callsign):
    if callsign is None:
        callsign = "????????"
    callsign = callsign.strip()
    if len(callsign) == 0:
        callsign = "????????"

    fields = ['']
    field_idx = 0
    was_digit = False
    for (i, c) in enumerate(callsign):
        if (i > 0) and (was_digit != c.isdigit()):
            fields.append('')
            field_idx += 1
        fields[field_idx] = fields[field_idx] + c
        was_digit = c.isdigit()
    return fields

def callsign_to_color(callsign):
    h = hashlib.new('sha1')
    h.update(bytearray(split_callsign(callsign)[0], 'utf8'))
    return int.from_bytes(h.digest()[0:3])

class OpenSky:
    '''Grabs data from OpenSky'''
    def __init__(self, lat_min, lat_max, long_min, long_max, request_session, screen_size):
        '''Retrieves data from the box denoated my that minimum and maximum
        latitudes and longitudes. South and West are negative.'''
        self.url = f'https://opensky-network.org/api/states/all?lamin={lat_min}&lomin={long_min}&lamax={lat_max}&lomax={long_max}'
        self.lat_min = float(lat_min)
        self.lat_max = float(lat_max)
        self.long_min = float(long_min)
        self.long_max = float(long_max)
        self.request_ttl = 15 #5 * 60 # 5 minutes
        self.tracks = {} # tracks oircraft grouped by icao24 transponder id
        self.track_expiration = 20 * 60 # 20 minutes
        self.screen_size = screen_size
        self.request_session = request_session
        self.last_update = 0
        self.radar_group = None

    def draw(self, timestamp):
        '''Returns a displayio.Group and TTL in seconds for next drawing update.'''
        print('OPENSKY draw()')
        try:
            if self.last_update + self.request_ttl < timestamp:
                with self.request_session.get(self.url) as response:
                    print('OPENSKY: data fetched.')
                    self.radar_group = displayio.Group()
                    self.draw_radar(self.radar_group, response.json())
                    print('OPENSKY update complete')
                    self.last_update = timestamp
            return (self.request_ttl, self.radar_group)

        except (ValueError, RuntimeError, ConnectionError, OSError) as e:
            print(f'EXCEPTION: {e}. Retrying.')
            return (1 * 60, make_simple_text(str(e)))

    def tap(self, x, y):
        '''Takes an x,y coordinate of a tap on the touch screen and returns a
        displayio.Group and TTL in seconds for next drawing update.'''
        return (self.request_ttl, self.radar_group)

    #########################################
    def latlong_to_screen(self, plane_lat, plane_long):
        x_t = linear_scale(self.long_min, plane_long, self.long_max)
        y_t = linear_scale(self.lat_min, plane_lat, self.lat_max)
        return (round(self.screen_size * x_t), round(self.screen_size * y_t))

    def draw_radar(self, radar_group, opensky_json):
        for raw_state in opensky_json['states']:
            state = parse_state(raw_state)
            coords = self.latlong_to_screen(state['latitude'], state['longitude'])
            radius = 4
            stroke = 1
            color = callsign_to_color(state['callsign'])
            radar_group.append(Circle(x0=coords[0], y0=coords[1], r=radius, fill=color, outline=color, stroke=stroke))
