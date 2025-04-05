import displayio

from chernoff import *

EMOTIONS = [ Emotion.ANGRY, 
             Emotion.HAPPY_3, Emotion.HAPPY_2, Emotion.HAPPY_1, 
             Emotion.NEUTRAL, 
             Emotion.SAD_1, Emotion.SAD_2, Emotion.SAD_3, Emotion.SAD_4, Emotion.SCARED,
             Emotion.MISCHEVIOUS, Emotion.CONFUSED]

COLORS = [ 0xffffff, 0xffff00, 0xff00ff, 0x00ffff, 0xff0000, 0x00ff00, 0x0000ff ]

TTL = 1 # seconds

class FaceAnimation:
    '''Displays a series of faces.'''
    def __init__(self, face_size):
        self.emotion_index = 0
        self.color_index = 0
        self.face = Face(face_size)

    def draw(self, timestamp):
        '''Takes a timestamp, and returns a TTL in seconds for next drawing
        update and a displayio.Group .'''
        print(f'FACEANIMATION draw {self.emotion_index} {self.color_index}')
        self.face.emotion = EMOTIONS[self.emotion_index]
        self.face.color = COLORS[self.color_index]
        self.face.reset_color()

        if not self.face.is_complex_emotion():
            self.face.reset_pupils()
            self.face.reset_eyebrows()

        # draw
        main = displayio.Group()
        self.face.draw(main)

        self.emotion_index = (self.emotion_index + 1) % len(EMOTIONS)
        return (TTL, main)

    def tap(self, x, y):
        '''Takes an x,y coordinate of a tap on the touch screen and returns a
        TTL in seconds for next drawing update and a displayio.Group .'''
        print('FACEANIMATION tap')
        self.color_index = (self.color_index + 1) % len(COLORS)
        return self.draw(0)

