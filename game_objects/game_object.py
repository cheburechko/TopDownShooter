import struct, math
from libs.Vec2D import Vec2d

class GameObject(object):

    ID = 0
    STATE_FMT = "Ifffff"
    STATE_SIZE = 25
    OBJECT_TYPES = {}

    @classmethod
    def getID(cls):
        cls.ID += 1
        return cls.ID - 1

    def __init__(self, shape, objType, objId=None, solid=True,
            solids=None):
        self.shape = shape
        self.solid = solid
        self.speedx = 0
        self.speedy = 0

        # Movement limiters
        self.solids = solids

        if objId is None:
            self.id = GameObject.getID()
        else:
            self.id = objId

        self.type = objType
        self.alive = True

    @property
    def pos(self):
        return self.shape.pos

    @pos.setter
    def pos(self, newp):
        self.shape.move(pos=newp)

    @property
    def angle(self):
        return self.shape.angle

    @angle.setter
    def angle(self, a):
        self.shape.rotate(angle=a)

    def hit_test(self, obj):
        return self.shape.hit_test(obj.shape)

    def collisions(self, obj_list):
        ans = []
        for obj in obj_list:
            if (self.id != obj.id) and self.hit_test(obj):
                ans += [obj]
        return ans

    def move(self, **kwargs):
        if self.solid and self.solids is not None:
            return self.shape.move_and_collide(self.solids.values(), True, **kwargs)
        else:
            self.shape.move(**kwargs)

    def rotate(self, **kwargs):
        self.shape.rotate(**kwargs)

    @classmethod
    def getState(cls, self):
        return chr(self.TYPE) + struct.pack("I", self.id) + cls.OBJECT_TYPES[self.type].getState(self)

    @classmethod
    def getStateSize(cls, data):
        return cls.OBJECT_TYPES[cls.get_type(data)].get_state_size(cls.get_body(data))+5

    @classmethod
    def get_id(cls, data):
        return struct.unpack("I", data[1:5])[0]

    @classmethod
    def get_type(cls, data):
        return ord(data[0])

    @classmethod
    def get_body(cls, data):
        return data[5:]

    @classmethod
    def fromState(cls, state):
        return cls.OBJECT_TYPES[cls.get_type(state)].fromState(cls.get_body(state), cls.get_id(state))

    @classmethod
    def registerType(cls, type):
        cls.OBJECT_TYPES[type.TYPE] = type