__author__ = 'thepunchy'

from messages.Message import Message
import struct

class ConnectMessage(Message):

    TYPE = chr(Message.CONNECT)

    def __init__(self, name=''):
        Message.__init__(self, Message.CONNECT)
        self.name = name

    def toString(self):
        self.data = Message.toString(self) + struct.pack("I", len(self.name))\
                    + self.name
        return self.data

    @classmethod
    def fromString(cls, data):
        msg = ConnectMessage()
        msg.getHead(data)
        size = struct.unpack("I", data[cls.HEADER:cls.HEADER+4])[0]
        msg.data = data[:cls.HEADER+4+size]
        msg.name = data[cls.HEADER+4:cls.HEADER+4+size]
        return msg