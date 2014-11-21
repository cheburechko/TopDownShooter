import struct, math

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
        self.x = position[0]
        self.y = position[1]
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
        if (self.x - obj.x) ** 2 + (self.y - obj.y) ** 2 < (self.size + obj.size) ** 2:
            return True
        return False

    def collisions(self, obj_list):
        ans = []
        for obj in obj_list:
            if (self.id != obj.id) and self.hitTest(obj):
                ans += [obj]
        return ans

    def move(self, vector=None, scale=None, angle=None, position=None):
        oldPos = (self.x, self.y)
        resultingScale = 1
        if scale is not None:
            resultingScale = scale

        if vector is not None:
            self.x += vector[0] * resultingScale
            self.y += vector[1] * resultingScale
        elif angle is not None:
            self.x += math.cos(angle) * resultingScale
            self.y += math.sin(angle) * resultingScale
        elif position is not None:
            self.x = position[0]
            self.y = position[1]

        if self.solid:
            if self.solids is not None:
                cols = self.collisions(self.solids.values())
                if len(cols) > 0:
                    self.x = oldPos[0]
                    self.y = oldPos[1]
            # Boundaries
            if self.area is not None:
                if self.x < self.area[0] or self.x > self.area[1]:
                    self.x = oldPos[0]
                if self.y < self.area[2] or self.y > self.area[3]:
                    self.y = oldPos[1]

    def rotate(self, angle=None, vector=None):
        if vector is not None:
            self.angle = math.atan2(vector[1] - self.y, vector[0] - self.x)
        elif angle is not None:
            self.angle = angle


    def getState(self):
        state = chr(self.type) + struct.pack(self.STATE_FMT, self.id,
                self.x, self.y, self.speedx, self.speedy, self.angle)
        return state

    @classmethod
    def unpackState(cls, data):
        state = (ord(data[0]),) + struct.unpack(cls.STATE_FMT, data[1:])
        return state

    def setState(self, state):
        self.x = state[2]
        self.y = state[3]
        self.speedx = state[4]
        self.speedy = state[5]
        self.angle = state[6]

    @classmethod
    def fromState(cls, state):
        return cls.OBJECT_TYPES[state[0]].fromState(state)

    @classmethod
    def registerType(cls, type):
        cls.OBJECT_TYPES[type.TYPE] = type