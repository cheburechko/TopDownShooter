import struct

class Message():
    INPUT = 0
    CHAT = 1
    LIST = 2
    MSG_TYPES = {}

    def __init__(self, type)
        self.type = type
        self.data = None

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

    TYPE = chr(Message.INPUT)

    def __init__(self):
        Message.__init__(self, Message.INPUT)
        self.mask = 0
        self.cursorX = self.cursorY = .0
        self.msecs = 0
        self.timestamp = 0

    def unsetButton(self, btn):
        self.mask = self.mask & (~(1 << btn))

    def setButton(self, btn):
        self.unsetButton(btn)
        self.mask = self.mask | (1 << btn)

    def isSet(self, btn):
        return (self.mask & (1 << btn)) != 0

    def toString(self):
        self.data = self.TYPE + struct.pack(self.FORMAT, \
                self.cursorX, self.cursorY, self.timestamp, self.msecs, self.mask)
        return self.data

    @classmethod
    def fromString(cls, data):
        msg = InputMessage()
        msg.data = data
        parts = struct.unpack(cls.FORMAT, data[1:])
        msg.cursorX = parts[0]
        msg.cursorY = parts[1]
        msg.timestamp = parts[2]
        msg.msecs = parts[3]
        msg.mask = parts[4]
        return msg

class ChatMessage(Message):
    
    TYPE = chr(Message.CHAT)

    def __init__(self, msg=""):
        Message.__init__(self, Message.CHAT)
        self.msg = msg

    def toString(self):
        self.data = self.TYPE + struct.pack("I", len(self.msg)) + self.data
        return self.data

    @classmethod
    def fromString(cls, data):
        msg = ChatMessage()
        msg.data = data
        size = struct.unpack("I", data[1:5])
        msg.msg = data[5:5+size]
        return msg

class ListMessage(Message):

    TYPE = chr(Message.LIST)

    def __init__(self)
        Message.__init__(self, Message.LIST)
        self.msgs = []

    def add(self, msg)
        self.msgs += [msg]

    def toString(self):
        self.data = self.TYPE + chr(len(self.msgs))
        for msg in self.msgs:
            self.data += msg.toString()
        return self.data

    @classmethod
    def fromString(cls, data):
        msg = ListMessage()
        msg.data = data
        size = ord(data[1])
        start = 2
        for i in range(size):
            newMsg = Message.getMessage(data[start:])
            start += len(newMsg.data)
            msg.msgs += [newMsg]
        return msg


Message.registerType(InputMessage)
Message.registerType(ChatMessage)
Message.registerType(ListMessage)
