__author__ = 'thepunchy'

from libs.Vec2D import Vec2d
import math
import pygame
import struct
from graphics.Camera import Camera
from BoundingBox import BoundingBox
from ShapeHashMap import StaticShapeHashMap

class NotShapeClassException(Exception):
    pass

class Shape(object):
    colliders = {}
    shapes = {}

    def __init__(self, pos, angle, static=False):
        self.pos = Vec2d(pos)
        self.angle = angle
        self.static = static
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
        return cls.shapes[ord(data[0])].serialized_size(data[1:])+1

    @classmethod
    def register_collider(cls, collider, shape1, shape2):
        cls.colliders[cls.get_collider_key(shape1, shape2)] = collider
        cls.colliders[cls.get_collider_key(shape2, shape1)] = lambda x, y: collider(y, x)

    def hit_test(self, shape):
        key = Shape.get_collider_key(self.__class__, shape.__class__)
        if key not in Shape.colliders:
            return False
        return Shape.colliders[key](self, shape)

    def _bounding_box(self):
        return BoundingBox(self.pos.x, self.pos.x, self.pos.y, self.pos.y)

    @property
    def bbox(self):
        if hasattr(self, "_bbox"):
            return self._bbox
        if not self.static:
            return self._bounding_box()
        self._bbox = self._bounding_box()
        return self._bbox

    def get_collisions(self, shapes):
        ans = []
        for shape in shapes:
            if shape is not self and self.hit_test(shape):
                ans += [shape]
        return ans

    def move(self, vector=None, position=None, angle=None, scale=1):
        if vector is not None:
            self.pos += Vec2d(vector) * scale
        elif angle is not None:
            self.pos += Vec2d.shift(angle, scale)
        elif position is not None:
            self.pos = Vec2d(position)

    def move_and_collide(self, shapes, revert=True, scale=1, **kwargs):
        old_pos = Vec2d(self.pos)
        self.move(scale=scale, **kwargs)
        collisions = self.get_collisions(shapes)
        if revert and len(collisions) > 0:
            self.move(position=old_pos)
        return collisions

    def rotate(self, angle=None, vector=None, diff_angle=None, max_rot_speed=None):
        new_angle = self.angle
        if angle is not None:
            new_angle = angle
        elif vector is not None:
            new_angle = (vector - self.pos).get_angle()
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

    def rotate_and_collide(self, shapes, revert=True, **kwargs):
        old_angle = self.angle
        self.rotate(**kwargs)
        collisions = self.get_collisions(shapes)
        if revert and len(collisions) > 0:
            self.rotate(angle=old_angle)
        return collisions

    def encloses_point(self, point):
        return False

    def encloses_shape(self, shape):
        return not self.hit_test(shape) & self.encloses_point(shape.pos)

    def hit_test_with_interior(self, shape):
        return self.hit_test(shape) | \
               self.encloses_point(shape.pos) | \
               shape.encloses_point(self.pos)

    def draw(self, surface, camera, color):
        return pygame.Rect(0, 0, 0, 0)

    def bake_sprite(self):
        return None

    def make_static(self):
        self.static = True



class Circle(Shape):
    TYPE = 1
    SER_FMT = "ffff"
    SER_SIZE = 16
    def __init__(self, pos, angle, radius, static=False):
        Shape.__init__(self, pos, angle, static)
        self.radius = radius

    def draw(self, surface, camera, color):
        return pygame.draw.circle(surface,
                                  color,
                                  math.trunc(camera.transform(self.pos)),
                                  math.trunc(self.radius*camera.scale+0.5),
                                  1)

    def bake_sprite(self):
        surface = pygame.Surface([self.radius*2, self.radius*2])
        surface.set_alpha(0)
        self.draw(surface, Camera(surface.get_rect(), 0, 1), (0, 0, 0))
        return surface

    def serialize(self):
        return struct.pack(self.SER_FMT, self.pos.x, self.pos.y, self.angle, self.radius)

    def encloses_point(self, point):
        return self.pos.get_distance(point) < self.radius

    def _bounding_box(self):
        return BoundingBox(self.pos.x - self.radius,
                           self.pos.x + self.radius,
                           self.pos.y - self.radius,
                           self.pos.y + self.radius)

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
    def __init__(self, pos, angle=None, length=None, vector=None, end=None, static=False):
        if end is not None:
            vector = Vec2d(end) - Vec2d(pos)
        if angle is not None:
            vector = Vec2d.shift(angle, length)
        else:
            angle = vector.get_angle()

        self.__length = vector.get_length()
        self.__vector = vector
        self.__end = pos+vector
        Shape.__init__(self, pos, angle, static)

    @property
    def vector(self):
        return self.__vector

    @vector.setter
    def vector(self, other):
        self.__vector = Vec2d(other)
        self.__length = self.__vector.get_length()

    @property
    def end(self):
        return self.pos + self.vector

    @end.setter
    def end(self, newend):
        self.vector = newend - self.pos

    @property
    def length(self):
        return self.__length

    def rotate(self, angle=None, vector=None, diff_angle=None, max_rot_speed=None):
        old_angle = self.angle
        Shape.rotate(self, angle, vector, diff_angle, max_rot_speed)
        self.vector.rotate(self.angle - old_angle)

    def draw(self, surface, camera, color):
       return pygame.draw.line(surface, color, camera.transform(self.pos), camera.transform(self.end))

    def bake_sprite(self):
        surface = pygame.Surface([int(self.vector.get_length()), 1])
        surface.fill(0)
        return surface

    def encloses_point(self, point):
        return False

    def _bounding_box(self):
        end = self.end
        return BoundingBox(min(self.pos.x, end.x),
                           max(self.pos.x, end.x),
                           min(self.pos.y, end.y),
                           max(self.pos.y, end.y))

    def intersect(self, segment):
        if segment.length == 0 or self.length == 0:
            return None
        a = (segment.pos - self.pos).cross(self.vector)
        b = self.vector.cross(segment.vector)
        if a == 0 and b == 0:
            t0 = (segment.pos - self.pos).dot(self.vector) / self.length ** 2
            t1 = t0 + self.vector.dot(segment.vector) / self.length ** 2
            if self.vector.dot(segment.vector) < 0:
                tb = t0
                t0 = t1
                t1 = tb
            left = max(0, t0)
            right = min(1, t1)
            if t1 > 0 and t0 < 1:
                return Segment(self.pos + left*self.vector, end=self.pos + right*self.vector)
            elif t0 == 1:
                return self.end
            elif t1 == 0:
                return self.pos
        elif b != 0:
            t = (segment.pos - self.pos).cross(segment.vector) / b
            u = a/b
            if 0 <= t <= 1 and 0 <= u <= 1:
                return segment.pos + u*segment.vector
            else:
                return None
        else:
            return None

    def serialize(self):
        return struct.pack(self.SER_FMT, self.pos.x, self.pos.y, self.end.x, self.end.y)

    @classmethod
    def deserialize(cls, ser):
        data = struct.unpack(cls.SER_FMT, ser)
        return Segment(Vec2d(data[0], data[1]), end=Vec2d(data[2], data[3]))

    @classmethod
    def serialized_size(cls, data):
        return cls.SER_SIZE

    def __repr__(self):
        return "Segment(%s, %s)" % (self.pos, self.end)


class Wireframe(Shape):
    TYPE = 3
    SER_FMT = "fffI"
    SER_SIZE = 16
    SER_POINT_FMT = "ff"
    SER_POINT_SIZE = 8

    def __init__(self, pos, angle, points=None, segments=None, abs_segments=None, static=False):
        Shape.__init__(self, pos, angle)
        if abs_segments is not None:
            self.segments = abs_segments[:]
        elif segments is not None:
            self.segments = []
            for s in segments:
                self.segments += [Segment(s.pos + self.pos, end=s.end+self.pos, static=static)]
        else:
            self.segments = []
            points += [points[0]]
            for i in range(len(points)-1):
                self.segments += [Segment(points[i]+self.pos,
                                          end=points[i+1]+self.pos, static=static)]
        if self.static:
            self.make_static()

    def make_static(self):
        self.static = True
        for s in self:
            s.make_static()
        avg = reduce(lambda x,y: x + abs(y.vector), self, Vec2d(0,0))
        avg /= len(self)
        cell_size = max(avg.x, avg.y) * 2
        self.map = StaticShapeHashMap(cell_size, self.bbox)
        self.map.add_shapes(self.segments)
        self.sprite = self.bake_sprite()

    def __getitem__(self, item):
        return self.segments[item]
        #return Segment(s.pos.rotated(self.angle) + self.pos, vector = s.vector.rotated(self.angle))

    def __len__(self):
        return len(self.segments)


    def move(self, **kwargs):
        for s in self:
            s.move(**kwargs)
        Shape.move(self, **kwargs)

    def rotate(self, **kwargs):
        old_angle = self.angle
        Shape.rotate(self, **kwargs)
        for s in self:
            s.rotate(**kwargs)
            s.pos = (s.pos - self.pos).rotated(self.angle-old_angle) + self.pos

    def draw(self, surface, camera, color):
        if self.static:
            surface.blit(self.sprite, camera.transform((self.bbox.left, self.bbox.up)))
            # segments = self.map.get_shapes(BoundingBox.from_rect(camera.viewport))
            # for segment in segments:
            #     segment.draw(surface, camera, color)
            # return None
        else:
            for segment in self:
                segment.draw(surface, camera, color)

    def bake_sprite(self):
        # Determine sprite size
        surface = pygame.Surface((int(self.bbox.right-self.bbox.left),
                                  int(self.bbox.down-self.bbox.up)),
                                  flags=pygame.SRCALPHA)
        surface.set_alpha(0)
        for segment in self:
            pygame.draw.line(surface, (0,0,0,255),
                             segment.pos - (self.bbox.left, self.bbox.up),
                             segment.end - (self.bbox.left, self.bbox.up))
        return surface

    def encloses_point(self, point):
        vector = ((self[0].pos + self[1].pos + self[1].end) / 3 - point) * 2**32
        line = Segment(point, vector=vector)
        return len(self.intersect_segment(line)) % 2 == 1

    def _bounding_box(self):
        xs = reduce(lambda x,y: x+[y.pos.x, y.end.x], self, [])
        ys = reduce(lambda x,y: x+[y.pos.y, y.end.y], self, [])
        return BoundingBox(min(xs), max(xs), min(ys), max(ys))

    def intersect_segment(self, segment):
        result = []
        for s in self:
            buf = s.intersect(segment)
            if buf is not None:
                if len(result) > 0 and \
                    isinstance(buf, Vec2d) and \
                    isinstance(result[-1], Vec2d) and \
                    buf in result:
                    continue
                result += [buf]
        return result

    def serialize(self):
        head = struct.pack(self.SER_FMT, self.pos.x, self.pos.y, self.angle, len(self.segments))
        for s in self.segments:
            head += struct.pack(self.SER_POINT_FMT, s.pos.x, s.pos.y)
            head += struct.pack(self.SER_POINT_FMT, s.end.x, s.end.y)
        return head

    @classmethod
    def deserialize(cls, ser):
        data = struct.unpack(cls.SER_FMT, ser[:cls.SER_SIZE])
        segments = []
        for i in range(data[3]):
            point1 = Vec2d(struct.unpack(cls.SER_POINT_FMT,
                                           ser[cls.SER_SIZE+i*2*cls.SER_POINT_SIZE:cls.SER_SIZE+(
                                              2*i+1)*cls.SER_POINT_SIZE]))
            point2 = Vec2d(struct.unpack(cls.SER_POINT_FMT,
                                           ser[cls.SER_SIZE+(2*i+1)*cls.SER_POINT_SIZE:cls.SER_SIZE+(
                                              i+1)*2*cls.SER_POINT_SIZE]))
            segments += [Segment(point1, end=point2)]
        return Wireframe(Vec2d(data[0], data[1]), data[2], abs_segments=segments)

    @classmethod
    def serialized_size(cls, data):
        size = struct.unpack("I", data[cls.SER_SIZE-4:cls.SER_SIZE])
        return cls.SER_SIZE + cls.SER_POINT_SIZE*size[0]*2