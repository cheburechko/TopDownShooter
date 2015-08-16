__author__ = 'thepunchy'

from messages.Message import Message
import struct

class RemoveMessage(Message):

    TYPE = chr(Message.REMOVE)

    def __init__(self, type=0, id=0):
        Message.__init__(self, Message.REMOVE)
        self.id = id
        self.objType = type

    def toString(self):
        data = struct.pack("IB", self.id, self.objType)
        self.data = Message.toString(self) + \
                    data
        return self.data

    @classmethod
    def fromString(cls, data):
        msg = RemoveMessage()
        msg.getHead(data)
        msg.data = data[:cls.HEADER+5]
        data = struct.unpack("IB", data[cls.HEADER:cls.HEADER+5])
        msg.id = data[0]
        msg.objType = data[1]
        return msg
