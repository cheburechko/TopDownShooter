__author__ = 'thepunchy'
from messages.Message import Message
import struct

class InputMessage(Message):

    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    FIRE = 4
    FORMAT = "ffIHB"
    FORMAT_SIZE = 15

    TYPE = chr(Message.INPUT)

    def __init__(self):
        Message.__init__(self, Message.INPUT)
        self.mask = 0
        self.cursorX = self.cursorY = .0
        self.msecs = 0

    def unsetButton(self, btn):
        self.mask &= ~(1 << btn)

    def setButton(self, btn):
        self.unsetButton(btn)
        self.mask |= 1 << btn

    def isSet(self, btn):
        return (self.mask & (1 << btn)) != 0

    def setCursor(self, pos):
        self.cursorX = pos[0]
        self.cursorY = pos[1]

    def toString(self):
        self.data = Message.toString(self) + struct.pack(self.FORMAT,
                self.cursorX, self.cursorY, self.timestamp, self.msecs, self.mask)
        return self.data

    @classmethod
    def fromString(cls, data):
        msg = InputMessage()
        msg.getHead(data)
        msg.data = data[:cls.HEADER+cls.FORMAT_SIZE]
        parts = struct.unpack(cls.FORMAT, data[cls.HEADER:cls.HEADER+cls.FORMAT_SIZE])
        msg.cursorX = parts[0]
        msg.cursorY = parts[1]
        msg.timestamp = parts[2]
        msg.msecs = parts[3]
        msg.mask = parts[4]
        return msg