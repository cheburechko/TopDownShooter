__author__ = 'thepunchy'

from messages.Message import Message

class ListMessage(Message):

    TYPE = chr(Message.LIST)

    def __init__(self):
        Message.__init__(self, Message.LIST)
        self.msgs = []

    def add(self, msg):
        self.msgs += [msg]

    def toString(self):
        self.data = Message.toString(self) + chr(len(self.msgs))
        for msg in self.msgs:
            self.data += msg.toString()
        return self.data

    @classmethod
    def fromString(cls, data):
        msg = ListMessage()
        msg.getHead(data)
        msg.data = data
        size = ord(data[cls.HEADER])
        start = cls.HEADER+1
        for i in range(size):
            newMsg = Message.getMessage(data[start:])
            start += len(newMsg.data)
            msg.msgs += [newMsg]
        return msg