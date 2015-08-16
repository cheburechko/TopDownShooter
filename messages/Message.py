__author__ = 'thepunchy'
import struct

class Message():
    INPUT = 0
    CHAT = 1
    LIST = 2
    CONNECT = 3
    ENTITY = 4
    PING = 5
    REMOVE = 6
    META = 7
    TYPE = None

    HEADER = 5
    MSG_TYPES = {}

    def __init__(self, type):
        self.type = type
        self.data = None
        self.timestamp = 0

    def toString(self):
        self.data = self.TYPE + struct.pack("I", self.timestamp)
        return self.data

    def getHead(self, data):
        self.timestamp = struct.unpack("I", data[1:5])[0]

    @classmethod
    def registerType(cls, msgClass):
        cls.MSG_TYPES[msgClass.TYPE] = msgClass

    @classmethod
    def getMessage(cls, data):
        return cls.MSG_TYPES[data[0]].fromString(data)
