__author__ = 'thepunchy'

from libs.Vec2D import Vec2d
import math
import pygame
import struct

class NotShapeClassException(Exception):
    pass

class Shape:
    colliders = {}
    shapes = {}

    def __init__(self, pos, angle):
        self.pos = Vec2d(pos)
        self.angle = angle
        pass

    @classmethod
    def get_collider_key(self, cls1, cls2):
        if not issubclass(cls1, Shape) or not issubclass(cls2, Shape):
            raise NotShapeClassException
        return cls1, cls2

    @classmethod
    def register_shape(cls, shape):
        cls.shapes[shape.TYPE] = shape

    @classmethod
    def serialize(cls, self):
        return chr(self.TYPE)+cls.shapes[self.TYPE].serialize(self)

    @classmethod
    def deserialize(cls, data):
         return cls.shapes[ord(data[0])].deserialize(data[1:])

    @classmethod
    def serialized_size(cls, data):
        return cls.shapes[ord(data[0])].serialized_size(data[1:])

    @classmethod
    def register_collider(cls, collider, shape1, shape2):
        cls.colliders[cls.get_collider_key(shape1, shape2)] = collider
        cls.colliders[cls.get_collider_key(shape2, shape1)] = lambda x, y: collider(y, x)

    def hit_test(self, shape):
        key = Shape.get_collider_key(self.__class__, shape.__class__)
        if key not in Shape.colliders:
            return False
        return Shape.colliders[key](self, shape)

    def get_collisions(self, shapes):
        ans = []
        for shape in shapes:
            if self.hit_test(shape):
                ans += [shape]
        return ans

    def move(self, vector=None, position=None, angle=None, scale=1):
        if vector is not None:
            self.pos += Vec2d(vector) * scale
        elif angle is not None:
            self.pos += Vec2d.shift(angle, scale)
        elif position is not None:
            self.pos = Vec2d(position)

    def move_and_collide(self, shapes, revert=True, vector=None, position=None, angle=None, scale=1):
        old_pos = self.pos
        self.move(vector=vector, position=position, angle=angle, scale=scale)
        collisions = self.get_collisions(shapes)
        if revert and len(collisions) > 0:
            self.move(position=old_pos)
        return collisions

    def rotate(self, angle=None, vector=None, diff_angle=None, max_rot_speed=None):
        new_angle = self.angle
        if angle is not None:
            new_angle = angle
        elif vector is not None:
            new_angle = Vec2d(vector).get_angle()
        elif diff_angle is not None:
            new_angle += diff_angle

        if max_rot_speed is None:
            self.angle = new_angle
        elif abs(int(new_angle-self.angle)) % 180 < max_rot_speed:
            self.angle = new_angle
        elif math.sin(new_angle-self.angle) > 0:
            self.angle -= max_rot_speed
        else:
            self.angle += max_rot_speed

    def rotate_and_collide(self, shapes, revert=True, angle=None, vector=None, diff_angle=None, max_rot_speed=None):
        old_angle = self.angle
        self.rotate(angle=angle, vector=vector, diff_angle=diff_angle, max_rot_speed=max_rot_speed)
        collisions = self.get_collisions(shapes)
        if revert and len(collisions) > 0:
            self.rotate(angle=old_angle)
        return collisions

    def draw(self, surface, camera, color):
        return pygame.Rect(0, 0, 0, 0)


class Circle(Shape):
    TYPE = 1
    SER_FMT = "ffff"
    SER_SIZE = 16
    def __init__(self, pos, angle, radius):
        Shape.__init__(self, pos, angle)
        self.radius = radius

    def draw(self, surface, camera, color):
        return pygame.draw.circle(surface,
                                  color,
                                  math.trunc(camera.transform(self.pos)),
                                  math.trunc(self.radius*camera.scale+0.5),
                                  1)

    def serialize(self):
        return struct.pack(self.SER_FMT, self.pos.x, self.pos.y, self.angle, self.radius)

    @classmethod
    def deserialize(cls, ser):
        data = struct.unpack(cls.SER_FMT, ser)
        return Circle(Vec2d(data[0], data[1]), data[2], data[3])

    @classmethod
    def serialized_size(cls, data):
        return cls.SER_SIZE


class Segment(Shape):
    TYPE = 2
    SER_FMT = "ffff"
    SER_SIZE = 16
    def __init__(self, pos, angle=None, length=None, vector=None, end=None):
        if end is not None:
            vector = Vec2d(end) - Vec2d(pos)
        if angle is not None:
            vector = Vec2d.shift(angle, length)
        else:
            angle = vector.get_angle()

        self.vector = vector
        Shape.__init__(self, pos, angle)

    def get_end(self):
        return self.pos + self.vector
    
    def set_end(self, newend):
        self.vector = newend - self.pos

    end = property(get_end, set_end)

    def rotate(self, angle=None, vector=None, diff_angle=None, max_rot_speed=None):
        old_angle = self.angle
        Shape.rotate(self, angle, vector, diff_angle, max_rot_speed)
        self.vector.rotate(self.angle - old_angle)

    def draw(self, surface, camera, color):
       return pygame.draw.aaline(surface, color, camera.transform(self.pos), camera.transform(self.end))

    def serialize(self):
        return struct.pack(self.SER_FMT, self.pos.x, self.pos.y, self.end.x, self.end.y)

    @classmethod
    def deserialize(cls, ser):
        data = struct.unpack(cls.SER_FMT, ser)
        return Segment(Vec2d(data[0], data[1]), end=Vec2d(data[2], data[3]))

    @classmethod
    def serialized_size(cls, data):
        return cls.SER_SIZE


class Wireframe(Shape):
    TYPE = 3
    SER_FMT = "fffI"
    SER_SIZE = 16
    SER_POINT_FMT = "ff"
    SER_POINT_SIZE = 8
    def __init__(self, pos, angle, points):
        Shape.__init__(self, pos, angle)
        self.segments = []
        points += [points[0]]
        for i in range(len(points)-1):
            self.segments += [Segment(points[i], end=points[i+1])]

    def __getitem__(self, item):
        s = self.segments[item]
        return Segment(s.pos.rotated(self.angle) + self.pos, vector = s.vector.rotated(self.angle))

    def draw(self, surface, camera, color):
        return pygame.draw.aalines(surface, color, True, [camera.transform(s.pos) for s in self])

    def serialize(self):
        head = struct.pack(self.SER_FMT, self.pos.x, self.pos.y, self.angle, len(self.segments))
        for s in self.segments:
            head += struct.pack(self.SER_POINT_FMT, s.pos.x, s.pos.y)
        return head

    @classmethod
    def deserialize(cls, ser):
        data = struct.unpack(cls.SER_FMT, ser[:cls.SER_SIZE])
        points = []
        for i in range(data[3]):
            points += [Vec2d(struct.unpack(cls.SER_POINT_FMT,
                                          ser[cls.SER_SIZE+i*cls.SER_POINT_SIZE:cls.SER_SIZE+(
                                              i+1)*cls.SER_POINT_SIZE]))]
        return Wireframe(Vec2d(data[0], data[1]), data[2], points)

    @classmethod
    def serialized_size(cls, data):
        size = struct.unpack("I", data[cls.SER_SIZE-4:cls.SER_SIZE])
        return cls.SER_SIZE + cls.SER_POINT_SIZE*size