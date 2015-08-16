__author__ = 'thepunchy'

from messages.Message import Message
import struct

class ChatMessage(Message):

    TYPE = chr(Message.CHAT)
    FORMAT = "II"
    FORMAT_SIZE = 8

    def __init__(self, msg="", id=0):
        Message.__init__(self, Message.CHAT)
        self.msg = msg
        self.id = id

    def toString(self):
        data = self.msg.encode('utf-8')
        self.data = Message.toString(self) + \
                    struct.pack(self.FORMAT, self.id, len(data)) +\
                    data
        return self.data

    @classmethod
    def fromString(cls, data):
        msg = ChatMessage()
        msg.getHead(data)
        parts = struct.unpack(cls.FORMAT,
                              data[cls.HEADER:cls.HEADER+cls.FORMAT_SIZE])
        msg.id = parts[0]
        size = parts[1]
        msg.data = data[:cls.HEADER+cls.FORMAT_SIZE+size]
        msg.msg = data[cls.HEADER+cls.FORMAT_SIZE:cls.HEADER+cls.FORMAT_SIZE+size].decode('utf-8')
        return msg