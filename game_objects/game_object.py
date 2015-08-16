import struct, math
from libs.Vec2D import Vec2d

class GameObject():

    ID = 0
    STATE_FMT = "Ifffff"
    STATE_SIZE = 25
    OBJECT_TYPES = {}

    @classmethod
    def getID(cls):
        cls.ID += 1
        return cls.ID - 1

    def __init__(self, position, angle, size, objType, objId=None, solid=True,
            area=None, solids=None):
        self.pos = Vec2d(position)
        self.angle = angle
        self.size = size
        self.solid = solid
        self.speedx = 0
        self.speedy = 0

        # Movement limiters
        self.area = area
        self.solids = solids

        if objId is None:
            self.id = GameObject.getID()
        else:
            self.id = objId

        self.type = objType
        self.alive = True

    def hitTest(self, obj):
        print self.type, self.id, self.pos
        print obj.type, obj.id, obj.pos
        print self.pos.get_distance(obj.pos)
        print (self.size + obj.size)
        if self.pos.get_distance(obj.pos) < (self.size + obj.size):
            return True
        return False

    def collisions(self, obj_list):
        ans = []
        for obj in obj_list:
            if (self.id != obj.id) and self.hitTest(obj):
                ans += [obj]
        return ans

    def move(self, vector=None, scale=None, angle=None, position=None):
        oldPos = Vec2d(self.pos)
        resultingScale = 1
        if scale is not None:
            resultingScale = scale

        if vector is not None:
            self.pos += Vec2d(vector) * resultingScale
        elif angle is not None:
            self.pos += Vec2d.shift(angle,resultingScale)
        elif position is not None:
            self.pos = Vec2d(position)

        if self.solid:
            if self.solids is not None:
                cols = self.collisions(self.solids.values())
                if len(cols) > 0:
                    self.pos = oldPos
            # Boundaries
            if self.area is not None:
                if self.pos.x < self.area[0] or self.pos.x > self.area[1]:
                    self.pos.x = oldPos[0]
                if self.pos.y < self.area[2] or self.pos.y > self.area[3]:
                    self.pos.y = oldPos[1]

    def rotate(self, angle=None, vector=None):
        if vector is not None:
            self.angle = (vector - self.pos).get_angle()
        elif angle is not None:
            self.angle = angle

    @classmethod
    def getState(cls, self):
        return cls.OBJECT_TYPES[self.type].getState(self)

    @classmethod
    def getStateSize(cls, data):
        return cls.OBJECT_TYPES[ord(data[0])].STATE_SIZE

    @classmethod
    def unpackState(cls, data):
        return (ord(data[0]),) + struct.unpack(
            cls.OBJECT_TYPES[ord(data[0])].STATE_FMT, data[1:])

    @classmethod
    def fromState(cls, state):
        return cls.OBJECT_TYPES[state[0]].fromState(state)

    @classmethod
    def registerType(cls, type):
        cls.OBJECT_TYPES[type.TYPE] = type