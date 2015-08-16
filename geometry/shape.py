__author__ = 'thepunchy'

from libs.Vec2D import Vec2d
import math
import pygame

class NotShapeClassException(Exception):
    pass

class Shape:
    colliders = {}

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

    def move(self, vector=None, pos=None, angle=None, scale=1):
        if vector is not None:
            self.pos += Vec2d(vector) * scale
        elif angle is not None:
            self.pos += Vec2d.shift(angle, scale)
        elif pos is not None:
            self.pos = Vec2d(pos)

    def move_and_collide(self, shapes, revert=True, vector=None, pos=None, angle=None, scale=1):
        old_pos = self.pos
        self.move(vector=vector, pos=pos, angle=angle, scale=scale)
        collisions = self.get_collisions(shapes)
        if revert and len(collisions) > 0:
            self.move(pos=old_pos)
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
    def __init__(self, pos, angle, radius):
        Shape.__init__(self, pos, angle)
        self.radius = radius

    def draw(self, surface, camera, color):
        return pygame.draw.circle(surface,
                                  color,
                                  math.trunc(camera.transform(self.pos)),
                                  math.trunc(self.radius*camera.scale+0.5),
                                  1)


class Segment(Shape):
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


class Wireframe(Shape):
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