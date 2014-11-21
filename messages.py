import struct
from models import GameObject

class Message():
    INPUT = 0
    CHAT = 1
    LIST = 2
    CONNECT = 3
    ENTITY = 4
    PING = 5
    REMOVE = 6
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
        self.mask = self.mask & (~(1 << btn))

    def setButton(self, btn):
        self.unsetButton(btn)
        self.mask = self.mask | (1 << btn)

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

class ChatMessage(Message):
    
    TYPE = chr(Message.CHAT)
    FORMAT = "II"
    FORMAT_SIZE = 8

    def __init__(self, msg="", id=0):
        Message.__init__(self, Message.CHAT)
        self.msg = msg
        self.id = id

    def toString(self):
        self.data = Message.toString(self) + \
                    struct.pack(self.FORMAT, self.id, len(self.msg)) +\
                    self.msg
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
        msg.msg = data[cls.HEADER+cls.FORMAT_SIZE:cls.HEADER+cls.FORMAT_SIZE+size]
        return msg

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

class EntityMessage(Message):

    TYPE = chr(Message.ENTITY)

    def __init__(self, entity=None):
        Message.__init__(self, Message.ENTITY)
        self.entity = entity

    def toString(self):
        data = self.entity.getState()
        self.data = Message.toString(self) + \
                    data
        return self.data

    @classmethod
    def fromString(cls, data):
        msg = EntityMessage()
        msg.getHead(data)
        msg.data = data[:cls.HEADER+GameObject.STATE_SIZE]
        msg.state = data[cls.HEADER:cls.HEADER+GameObject.STATE_SIZE]
        return msg

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

class PingMessage(Message):
    
    TYPE = chr(Message.PING)

    def __init__(self):
        Message.__init__(self, Message.PING)

    def toString(self):
        self.data = Message.toString(self)

    @classmethod
    def fromString(cls, data):
        msg = PingMessage()
        msg.getHead(data)
        msg.data = data

Message.registerType(InputMessage)
Message.registerType(ChatMessage)
Message.registerType(ListMessage)
Message.registerType(ConnectMessage)
Message.registerType(EntityMessage)
Message.registerType(PingMessage)
