__author__ = 'thepunchy'

from messages.Message import Message
from metadata import PlayerEntry
import struct

class MetaMessage(Message):

    TYPE = chr(Message.META)
    FORMAT = "IIIII"
    FORMAT_SIZE = 20

    def __init__(self, entry=None):
        Message.__init__(self, Message.META)
        self.entry = entry

    def toString(self):
        self.data = Message.toString(self) + struct.pack(
            self.FORMAT,
            self.entry.id,
            self.entry.score,
            self.entry.deaths,
            self.entry.latency,
            len(self.entry.name)
            ) + self.entry.name
        return self.data

    @classmethod
    def fromString(cls, data):
        msg = MetaMessage()
        msg.getHead(data)
        parts = struct.unpack(cls.FORMAT, data[cls.HEADER:cls.HEADER+cls.FORMAT_SIZE])
        msg.entry = PlayerEntry(
            parts[0],
            data[cls.HEADER+cls.FORMAT_SIZE:cls.HEADER+cls.FORMAT_SIZE+parts[4]],
            score=parts[1], deaths=parts[2], latency=parts[3])
        msg.data = data[:cls.HEADER+cls.FORMAT_SIZE+parts[4]]
        return msg