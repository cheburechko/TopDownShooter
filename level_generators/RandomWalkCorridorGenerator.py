__author__ = 'thepunchy'
import random
from geometry_shortcut import *
from libs.Vec2D import Vec2d
from pygame.locals import *
import pygame

class RandomWalkCorridorGenerator(object):
    def __init__(self):
        self.min_deviation = 0
        self.max_deviation = 30
        self.min_segments = 1
        # Segments per distance unit
        self.max_curvature = 1. / 100.
        self.min_width = 20
        self.max_width = 40
        # Size relative to distance between rooms divided by segments
        self.min_segment_size = 0.5
        self.max_segment_size = 1.5

        self.retries = 10

    def center_points(self, points):
        center = sum(points, Vec2d(0,0)) / len(points)
        points[:] = map(lambda x: x-center, points)
        return center

    def check_segments(self, segments):
        for shape in self.solids + reduce(lambda x,y: x+y, self.segments, []):
            if shape == self.origin or shape == self.destination:
                continue
            collisions = shape.get_collisions(segments)
            if len(collisions) > 0:
                if len(self.segments) > 0:
                    if shape == self.segments[-1][0] and len(collisions) == 1:
                        continue
                    elif shape == self.segments[-1][1] and len(collisions) == 1:
                        continue
                print segments
                print shape
                return False
        return True

    def make_segments(self, next_pos, offset):
        p1 = next_pos + offset*random.uniform(0, self.max_width)
        p2 = p1 - offset*random.uniform(self.min_width, self.max_width)
        return [Segment(self.last_points[0], end=p1),
                Segment(self.last_points[1], end=p2)]

    def generate_segment(self, debug=None):
        direction =  self.destination.pos - self.cur_pos
        distance = random.uniform(self.distance*self.min_segment_size,
                                  self.distance*self.max_segment_size)
        a = distance*(distance+math.sin(math.radians(self.max_deviation))) + direction.get_length_sqrd()
        b = direction.get_length() * (2*distance + math.sin(math.radians(self.max_deviation)))
        max_deviation = 90 - math.degrees(math.acos(b/a))

        next_direction = direction.rotated(random.uniform(-max_deviation, max_deviation)).normalized()
        print max_deviation
        print direction.get_angle() - next_direction.get_angle()
        next_pos = self.cur_pos + next_direction*distance
        offset = next_direction.rotated(90).normalized()

        segments = self.make_segments(next_pos, offset)
        retries = self.retries
        while not self.check_segments(segments) and retries > 0:
            self.debug_output(debug, segments,
                              "Failed attempt " + str(self.retries - retries))
            segments = self.make_segments(next_pos, offset)
            retries -= 1

        if not self.check_segments(segments):
            return False

        self.last_pos += [self.cur_pos]

        self.segments += [segments]
        self.last_points = (segments[0].end, segments[1].end)
        self.cur_pos = next_pos
        return True

    def rollback_segment(self):
        self.last_points = (self.segments[-1][0].pos,
                            self.segments[-1][1].pos)
        del self.segments[-1]
        self.cur_pos = self.last_pos[-1]
        del self.last_pos[-1]


    def final_segment(self, debug=None):
        direction =  self.destination.pos - self.cur_pos
        next_pos = self.destination.pos
        offset = direction.rotated(90).normalized()

        segments = self.make_segments(next_pos, offset)
        retries = self.retries
        print segments
        while not self.check_segments(segments) and retries > 0:
            self.debug_output(debug, segments,
                              "Failed attempt " + str(self.retries - retries))
            segments = self.make_segments(next_pos, offset)
            retries -= 1

        if not self.check_segments(segments):
            return False

        self.segments += [segments]
        return True

    def debug_output(self, debug, additional_shapes, message=""):
        if debug is not None:
            debug['screen'].fill(debug['BACKGROUND'])
            for shape in self.solids + reduce(lambda x,y: x+y, self.segments, []) + additional_shapes:
                shape.draw(debug['screen'], debug['camera'], debug['COLOR'])
            pygame.display.flip()
            print message
            run = True
            while run:
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONDOWN:
                        run = False

    def get_wireframe(self):
        points = [None] * (self.total_segments * 2 + 2)
        for i in range(self.total_segments):
            points[i] = self.segments[i][0].pos
            points[-i-1] = self.segments[i][1].pos
        points[self.total_segments] = self.segments[self.total_segments-1][0].end
        points[self.total_segments+1] = self.segments[self.total_segments-1][1].end
        center = self.center_points(points)
        return Wireframe(center, 0, points)

    def generate_corridor(self, room1, room2, solid_shapes, debug=None):
        self.distance = (room2.pos - room1.pos).get_length()
        self.total_segments = random.randint(self.min_segments, int(self.distance*self.max_curvature))
        self.distance /= self.total_segments
        self.segments = []
        self.solids = solid_shapes
        self.origin = room1
        self.cur_pos = room1.pos
        self.destination = room2
        self.last_pos = []
        # Generate starting points
        width = random.uniform(self.min_width, self.max_width)
        direction =  self.destination.pos - self.cur_pos
        self.last_points = (self.cur_pos + direction.rotated(90).normalized()*(width/2),
                            self.cur_pos - direction.rotated(90).normalized()*(width/2))
        i = 0
        print 'Begin:', self.total_segments
        while i < self.total_segments:
            print i
            self.debug_output(debug, [], "Step " + str(i))
            if i == self.total_segments - 1:
                if self.final_segment(debug):
                    i += 1
                elif i > 0:
                    i -= 1
                    self.rollback_segment()
            elif not self.generate_segment(debug):
                if i > 0:
                    i -= 1
                    self.rollback_segment()
            else:
                i += 1
        return self.get_wireframe()