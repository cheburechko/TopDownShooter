__author__ = 'thepunchy'

from messages.Message import Message
from game_objects.game_object import GameObject

class EntityMessage(Message):

    TYPE = chr(Message.ENTITY)

    def __init__(self, entity=None):
        Message.__init__(self, Message.ENTITY)
        self.entity = entity

    def toString(self):
        data = GameObject.getState(self.entity)
        self.data = Message.toString(self) + data
        return self.data

    @classmethod
    def fromString(cls, data):
        msg = EntityMessage()
        msg.getHead(data)
        stateSize = GameObject.getStateSize(data[cls.HEADER:])
        msg.data = data[:cls.HEADER+stateSize]
        msg.state = data[cls.HEADER:cls.HEADER+stateSize]
        return msg
