# Guy
# chernoff.py
# Copyright 2025, Jonathan Koren
# Licensed under the Gnu Public License v3

import sys

CIRCUIT_PYTHON = 'CircuitPython' in sys.version

if CIRCUIT_PYTHON:
    from adafruit_display_shapes.arc import Arc
    from adafruit_display_shapes.circle import Circle
    from adafruit_display_shapes.filled_polygon import FilledPolygon
    from adafruit_display_shapes.line import Line
    from adafruit_display_shapes.roundrect import RoundRect

from math import pi, sin, cos, atan, radians, pi

from scale import euclid

class Emotion:
    HAPPY = HAPPY_3 = 3
    HAPPY_2 = 2
    HAPPY_1 = 1
    NEUTRAL = 0
    SAD_1 = -1
    SAD_2 = -2
    SAD = SAD_3 = -3
    ANGRY = 10
    SCARED = -10
    MISCHEVIOUS = 11
    CONFUSED = -11

def reduce(l, s):
    '''Repeatedly applys l to pairs in s and returns the result'''
    it = iter(s)
    value = next(it)
    for e in it:
        value = l(value, e)
    return value

class Eye:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.radius = 1
        self.color = 0xffffff
        self.stroke = 1
        self.fill = None

    def describe(self):
        return f'EYE: center ({self.x}, {self.y}), r={self.radius} stroke: {self.stroke} 0x{self.color:x}'

    def draw(self, displayio_group):
        if CIRCUIT_PYTHON:
            displayio_group.append(Circle(x0=self.x, y0=self.y, r=self.radius, fill=self.fill, outline=self.color, stroke=self.stroke))
        else:
            print(self.describe())

class EyeBrow:
    def __init__(self):
        self.color = 0xffffff
        self.stroke = 1
        self.x = 0
        self.y = 0
        self.angle = 0 # degrees
        self.width = 2
        self.height = 2

    def _rotate(self, point):
        return (round((point[0] * cos(radians(self.angle))) - (point[1] * sin(radians(self.angle)))),
                round((point[0] * sin(radians(self.angle))) + (point[1] * cos(radians(self.angle)))))

    def _generate_points(self):
            hh = self.height // 2
            ww = self.width // 2
            points = [ (-ww, hh), (ww, hh), (ww, -hh), (-ww, -hh) ]
            return list(map(lambda p: (p[0] + self.x, p[1] + self.y), map(lambda p: self._rotate(p), points)))

    def describe(self):
        return f'EYEBROW center: {self.x}, {self.y} angle: {self.angle} h: {self.height} w: {self.width} points: {self._generate_points()} stroke: {self.stroke} color: {self.color}'

    def update(self):
        if self.angle > 30:
            self.angle = 30
        if self.angle < -30:
            self.angle = -30

    def draw(self, displayio_group):
        self.update()
        if CIRCUIT_PYTHON:
            displayio_group.append(FilledPolygon(points=self._generate_points(), fill=self.color, stroke=self.stroke))
        else:
            print(self.describe())

def bound_pupil_to_eye(eye, pupil):
    # cap the pupil's size
    pupil.radius = min(pupil.radius, eye.radius)

    # don't let the pupil move past the eye
    dist_pupil_edge = euclid(eye.x, eye.y, pupil.x, pupil.y) + pupil.radius

    if dist_pupil_edge > eye.radius:
        overage = dist_pupil_edge - eye.radius
        angle = pi / 2
        if pupil.x - eye.x > 0:
            rat = (pupil.y - eye.y) / (pupil.x - eye.x)
            angle = atan(rat)
            pupil.x -= round(cos(angle) * overage)
        elif eye.x - pupil.x != 0:
            rat = (pupil.y - eye.y) / (eye.x - pupil.x)
            angle = atan(rat)
            pupil.x += round(cos(angle) * overage)
        pupil.y -= round(sin(angle) * overage)

class Nose:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.height = 1
        self.width = 1
        self.color = 0xffffff
        self.stroke = 1
        self.fill = None

    def describe(self):
        return f'NOSE: x: {self.x} y: {self.y} w: {self.width} h: {self.height} stroke: {self.stroke} 0x{self.color:x} fill: {self.fill}'

    def draw(self, displayio_group):
        if CIRCUIT_PYTHON:
            left = self.x - (self.width // 2)
            top = self.y - (self.height // 2)
            radius = min(self.height, self.width) // 2
            displayio_group.append(RoundRect(x=left, y=top, width=self.width, height=self.height, r=radius, fill=None, outline=self.color, stroke=self.stroke))
        else:
            print(self.describe())

class Mouth:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.radius = 100
        self.arc_angle = 100
        self.direction = 90
        self.color = 0xffffff
        self.segments = 10
        self.stroke = 1
        self.emotion = Emotion.NEUTRAL
        self.HALF_WIDTH = 105
        self.NEUTRAL_Y_OFFSET = 100

    def describe(self):
        return f'MOUTH: {self.__dict__}'

    def draw(self, displayio_group):
        if not CIRCUIT_PYTHON:
            print(self.describe())
            return

        ###################################
        # HAPPY
        if self.emotion == Emotion.HAPPY_3:
            y = self.y
            direction = 270
            arc = 120
            radius = 100
            BASE_RADIUS = 100
            displayio_group.append(Arc(x=self.x, y=y, radius=radius, angle=arc, direction=direction, segments=self.segments, arc_width=self.stroke * 2, fill=self.color))
        elif self.emotion == Emotion.HAPPY_2:
            y = self.y - 100
            direction = 270
            arc = 60
            radius = 200
            displayio_group.append(Arc(x=self.x, y=y, radius=radius, angle=arc, direction=direction, segments=self.segments, arc_width=self.stroke * 2, fill=self.color))
        elif self.emotion == Emotion.HAPPY_1:
            y = self.y - 300
            direction = 270
            arc = 30
            radius = 400
            displayio_group.append(Arc(x=self.x, y=y, radius=radius, angle=arc, direction=direction, segments=self.segments, arc_width=self.stroke * 2, fill=self.color))

        ####################################
        # NEUTRAL
        elif self.emotion == Emotion.NEUTRAL:
            y = self.y + self.NEUTRAL_Y_OFFSET
            displayio_group.append(Line(x0=self.x - self.HALF_WIDTH, y0=y, x1=self.x + self.HALF_WIDTH, y1=y, color=self.color))

        ####################################
        # SAD
        elif self.emotion == Emotion.SAD_3:
            radius = 100
            y = self.y + (2 * radius)
            direction = 90
            arc = 120
            BASE_RADIUS = 100
            displayio_group.append(Arc(x=self.x, y=y, radius=radius, angle=arc, direction=direction, segments=self.segments, arc_width=self.stroke * 2, fill=self.color))
        elif self.emotion == Emotion.SAD_2:
            y = self.y + 300
            direction = 90
            arc = 60
            radius = 200
            displayio_group.append(Arc(x=self.x, y=y, radius=radius, angle=arc, direction=direction, segments=self.segments, arc_width=self.stroke * 2, fill=self.color))
        elif self.emotion == Emotion.SAD_1:
            y = self.y + 500
            direction = 90
            arc = 30
            radius = 400
            displayio_group.append(Arc(x=self.x, y=y, radius=radius, angle=arc, direction=direction, segments=self.segments, arc_width=self.stroke * 2, fill=self.color))

        ####################################
        # SCARED / ANGRY
        elif self.emotion == Emotion.SCARED or self.emotion == Emotion.ANGRY:
            width = 2 * self.HALF_WIDTH
            height = 40
            left = self.x - self.HALF_WIDTH
            y = self.y + self.NEUTRAL_Y_OFFSET
            top = y - (height // 2)
            radius = height // 2
            displayio_group.append(RoundRect(x=left, y=top, width=width, height=height, r=radius, fill=None, outline=self.color, stroke=self.stroke))

            # horiz teeth line
            displayio_group.append(Line(x0=self.x - self.HALF_WIDTH, y0=y, x1=self.x + self.HALF_WIDTH, y1=y, color=self.color))

            # vert teeth lines
            NUM_TEETH = 6
            teeth_width = width // NUM_TEETH
            for i in range(1, NUM_TEETH):
                x = left + (teeth_width * i)
                displayio_group.append(Line(x0=x, y0=top, x1=x, y1=top + height, color=self.color))

class Face:
    def __init__(self, diameter):
        '''The face is a circle of the specified diameter located within a
        square of size diameter x diameter. 0,0 is located in the upper left of
        the circle.'''
        self.diameter = diameter
        self.radius = diameter // 2
        self.x = self.y = self.radius
        self.emotion = None
        self.color = 0xffffff

        # setup eyes, pupils, and eyebrows
        self.eyes = [ Eye(), Eye() ]
        self.pupils = [ Eye(), Eye() ]
        self.eyebrows = [ EyeBrow(), EyeBrow() ]

        eye_radius = round(self.radius * 0.1667)
        pupil_radius = eye_radius // 4
        for i in range(len(self.eyes)):
            self.eyes[i].radius = eye_radius
            self.pupils[i].radius = pupil_radius

        self.eye_space = eye_radius * 5
        self.eye_height = self.eye_space // 2
        half_eye_space = self.eye_space // 2

        self.eyes[0].x = self.pupils[0].x = self.eyebrows[0].x = self.x - half_eye_space
        self.eyes[1].x = self.pupils[1].x = self.eyebrows[1].x = self.x + half_eye_space

        self.eyes[0].y = self.pupils[0].y = self.eyes[1].y = self.pupils[1].y = self.y - self.eye_height

        brow_y = self.eyes[0].y - self.eyes[0].radius - self.pupils[0].radius
        self.eyebrows[0].y = self.eyebrows[1].y = brow_y
        self.eyebrows[0].width = self.eyebrows[1].width = self.eyes[0].radius * 2

        # setup nose
        self.nose = Nose()
        self.nose.width = round(pupil_radius * 2.5)
        self.nose.height = self.nose.width * 3
        self.nose.x = self.x
        self.nose.y = self.y

        # setup mouth
        self.mouth = Mouth()
        self.mouth.x = self.x
        self.mouth.y = self.y
        self.mouth.direction = 90

    def is_complex_emotion(self):
        return self.emotion in [Emotion.SCARED, Emotion.MISCHEVIOUS, Emotion.CONFUSED,
            Emotion.SAD_1, Emotion.SAD_2, Emotion.SAD_3, Emotion.SAD]

    def describe(self):
        s = f'FACE: d: {self.diameter} {self.emotion}' + "\n"
        for i in range(len(self.eyes)):
            s += self.eyes[i].describe() + "\n"
            s += self.pupils[i].describe() + "\n"
            s += self.eyebrows[i].describe() + "\n"
        s += self.nose.describe() + "\n"
        s += self.mouth.describe()
        return s

    def reset_pupils(self):
        for i in range(len(self.eyes)):
            self.pupils[i].x = self.eyes[i].x
            self.pupils[i].y = self.eyes[i].y

    def reset_eyebrows(self):
        for eyebrow in self.eyebrows:
            eyebrow.angle = 0

    def reset_color(self):
        if self.color is None:
            self.color = 0xffffff
        for i in range(len(self.eyes)):
            self.pupils[i].color = self.color
            self.eyes[i].color = self.color
            self.eyebrows[i].color = self.color
        self.nose.color = self.color
        self.mouth.color = self.color

    def update(self):
        if self.emotion is None:
            bound_pupil_to_eye(self.eyes[0], self.pupils[0])
            bound_pupil_to_eye(self.eyes[1], self.pupils[1])
            return

        if self.emotion == Emotion.MISCHEVIOUS:
            self.mouth.emotion = Emotion.HAPPY
            self.eyebrows[0].angle = 30
            self.eyebrows[1].angle = -30
            self.pupils[0].x = self.eyes[0].x + self.eyes[0].radius
            self.pupils[1].x = self.eyes[1].x - self.eyes[1].radius
            self.pupils[0].y = self.eyes[0].y + self.eyes[0].radius
            self.pupils[1].y = self.eyes[1].y + self.eyes[1].radius


        elif self.emotion == Emotion.CONFUSED:
            self.mouth.emotion = Emotion.SAD_1
            self.pupils[0].x = self.eyes[0].x
            self.pupils[1].x = self.eyes[1].x + 20
            self.pupils[0].y = self.eyes[0].y
            self.pupils[1].y = self.eyes[1].y
            self.eyebrows[0].angle = -15
            self.eyebrows[1].angle = 0

        else:
            self.mouth.emotion = self.emotion
            if self.is_complex_emotion():
                if self.emotion < Emotion.NEUTRAL:
                    self.eyebrows[0].angle = 10 * self.emotion
                    self.eyebrows[1].angle = -10 * self.emotion

        bound_pupil_to_eye(self.eyes[0], self.pupils[0])
        bound_pupil_to_eye(self.eyes[1], self.pupils[1])


    def draw(self, displayio_group):
        self.update()
        for i in range(len(self.eyes)):
            self.eyes[i].draw(displayio_group)
            self.pupils[i].draw(displayio_group)
            self.eyebrows[i].draw(displayio_group)
        self.nose.draw(displayio_group)
        self.mouth.draw(displayio_group)
