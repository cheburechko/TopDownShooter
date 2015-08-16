__author__ = 'thepunchy'

from messages.Message import Message

class PingMessage(Message):

    TYPE = chr(Message.PING)

    def __init__(self):
        Message.__init__(self, Message.PING)

    def toString(self):
        self.data = Message.toString(self)
        return self.data

    @classmethod
    def fromString(cls, data):
        msg = PingMessage()
        msg.getHead(data)
        msg.data = data[:cls.HEADER]
        return msg