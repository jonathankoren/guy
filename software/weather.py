# Guy
# weather.py
# Copyright 2025, Jonathan Koren
# Licensed under the Gnu Public License v3

import displayio
import json

from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

from chernoff import Face, Emotion, bound_pupil_to_eye

def clamp(low, val, high):
    return min(max(val, low), high)

class Module:
    '''A basic module'''
    def __init__(self):
        pass

    def draw(self):
        '''Returns a displayio.Group and TTL in seconds for next drawing update.'''
        raise NotImplementedError

    def tap(self, x, y):
        '''Takes an x,y coordinate of a tap on the touch screen and returns a
        displayio.Group and TTL in seconds for next drawing update.'''
        raise NotImplementedError


class Weather(Module):
    def __init__(self, url, request_session, face_size):
        self.url = url
        self.requests = request_session
        self.show_face = True
        self.ttl = 5 * 60 # five minutes
        self.datajson = None
        self.face = Face(face_size)
        self.face_group = None
        self.text_group = None
        self.last_update = 0

    def draw(self, timestamp):
        print('WEATHER: draw()')
        try:
            if self.last_update + self.ttl < timestamp:
                with self.requests.get(self.url) as response:
                    self.datajson = response.json()
                    print('WEATHER: data fetched.')
                    self.make_face_group()
                    self.make_text_view_group()
                    self.last_update = timestamp

                    print('WEATHER: face updated')
            return self.current_display_group()

        except (ValueError, RuntimeError, ConnectionError, OSError) as e:
            print(f'EXCEPTION: {e}. Retrying.')
            text = f'Error fetching from {URL}'

            # make face
            self.face.emotion = Emotion.CONFUSED
            self.face.color = 0xffff00
            self.face.reset_color()
            self.make_face_group()

            # make text
            self.text_group = make_simple_text(str(e))

            return self.current_display_group()

    def tap(self, x, y):
        '''Switches between face and text mode.'''
        if self.datajson is None:
            return (1, make_simple_text('Nothing fetched'))

        self.show_face = not self.show_face
        if self.show_face:
            return (self.ttl, self.face_group)
        else:
            return (self.ttl, self.text_group)

    #####################################################
    def current_display_group(self):
        if self.show_face:
            return (self.ttl, self.face_group)
        else:
            return (self.ttl, self.text_group)

    #####################################################
    def make_confused(self):
        self.face.emotion = Emotion.CONFUSED
        self.face.color = 0xffff00

    def make_face_temp(self):
        windchill = round(float(self.datajson['Wind Chill'].split('&')[0]))
        heatindex = round(float(self.datajson['Heat Index'].split('&')[0]))
        airtemp = round(float(self.datajson['Outside Temperature'].split('&')[0]))

        usable_temp = airtemp
        if windchill < airtemp * 0.9:
            usable_temp = windchill
        elif heatindex > airtemp * 1.1:
            usable_temp = heatindex

        MIN_SIZE = 20
        MAX_SIZE = 100
        self.face.nose.height = MIN_SIZE
        self.face.nose.width = MIN_SIZE
        if usable_temp > 0:
            self.face.nose.height = round(usable_temp) + 20
            if self.face.nose.height > MAX_SIZE:
                self.face.nose.width += self.face.nose.height - MAX_SIZE
                self.face.nose.height = MAX_SIZE
        else:
            self.face.nose.width = round(-usable_temp) + 20
            if self.face.nose.width > MAX_SIZE:
                self.face.nose.height += self.face.nose.width - MAX_SIZE
                self.face.nose.width = MAX_SIZE

    def make_face_humid(self):
        humidity = float(self.datajson['Humidity'].split('%')[0]) / 100.0
        for i in range(len(self.face.eyes)):
            offset = round(humidity * (2 * self.face.eyes[i].radius))
            self.face.pupils[i].x = self.face.eyes[i].x - self.face.eyes[i].radius + offset
            bound_pupil_to_eye(self.face.eyes[i], self.face.pupils[i])

    def make_face_aqi(self):
        self.face.color = int(self.datajson['Current AQI PM 2.5 color'][1:], 16)
        self.face.reset_color()
        try:
            AQI_CATEGORIES = ['Good', 'Moderate', 'Unhealthy for Sensitive Groups', 'NOT USED', 'Unhealthy', 'Very Unhealthy', 'Hazardous']
            idx = AQI_CATEGORIES.index(self.datajson['Current AQI PM 2.5 category'])
            self.face.mouth.emotion = Emotion.HAPPY_3 - idx
        except ValueError as e:
            print(f'{e}')
            self.face.mouth.emotion = Emotion.NEUTRAL

    def make_face_wind(self):
        mph = clamp(0, round(float(self.datajson['Wind'].split(' ')[0])) // 10, 3)
        self.face.eyebrows[0].angle = 15 * mph
        self.face.eyebrows[1].angle = -15 * mph

    def make_face(self):
        self.face.reset_pupils()
        self.face.reset_eyebrows()
        self.make_face_aqi()
        self.make_face_temp()
        self.make_face_wind()
        self.make_face_humid()

    def make_face_group(self):
        self.face_group = displayio.Group()
        self.make_face()
        self.face.draw(self.face_group)

    #####################################################
    def make_text_view_group(self):
        '''Creates a displayio.Group that shows the weather data as a bunch of text.'''
        group = displayio.Group()
        BASE_FONT_SIZE = 24
        font = bitmap_font.load_font(f"Junction-Regular-{BASE_FONT_SIZE}.pcf", displayio.Bitmap)
        font_scale = 1
        color = 0x0000FF
        text = [f"{self.datajson['date']}",
                f"Temp: {self.datajson['Outside Temperature'].split('&')[0]} deg",
                f"Humidity: {self.datajson['Humidity']}",
                f"Rain: {self.datajson['Rain']}",
                f"Wind: {self.datajson['Wind']}",
                f"UV: {self.datajson['UV Index']}",
                f"Radiation: {self.datajson['Radiation'].split('&')[0]}^2",
                f"AQI PM 2.5: {self.datajson['Current AQI PM 2.5']}"]
        text_areas = []
        down = 0
        for t in text:
            text_area = label.Label(font, text=t, color=color, scale=font_scale)
            text_area.x = 100
            text_area.y = 100 + down
            down += BASE_FONT_SIZE * (font_scale + 1)
            text_areas.append(text_area)
            group.append(text_area)

        self.text_group = group

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
        self.text_group = group
