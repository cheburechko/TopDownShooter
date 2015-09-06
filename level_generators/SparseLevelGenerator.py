__author__ = 'thepunchy'

from libs.Vec2D import Vec2d
from libs.Delaunay2d import Delaunay2d
import random

from geometry_shortcut import *

class SparseLevelGenerator(object):
    def __init__(self):
        self.area = None
        self.roomNumber = None
        self.minRoomSize = None
        self.points = []

    def generate_random_point(self):
        while True:
            p = Vec2d(random.uniform(self.area[0][0], self.area[1][0]),
                      random.uniform(self.area[0][1], self.area[1][1]))
            repick = False
            for point in self.points:
                if p.get_distance(point) < 2*self.minRoomSize:
                    repick = True
                    break
            if not repick:
                return p

    def generate(self):
        self.points = []
        for i in range(self.roomNumber):
            self.points += [self.generate_random_point()]
        delaunay = Delaunay2d(self.points)

        segments = []
        points = delaunay.points
        maxSize = [2**32] * len(points)
        roomSizes = [0] * len(points)
        edges = {key: list() for key in range(len(points))}
        for edge in delaunay.getEdges():
            dropEdge = False
            # check if edge if far enough from all points
            for i in range(len(points)):
                if i in edge:
                    continue
                vertex = points[i] - points[edge[0]]
                base = points[edge[1]] - points[edge[0]]
                # check if point projects on edge
                proj = vertex.dot(base) / base.get_length_sqrd()
                if proj < 0 or proj > 1:
                    continue
                # check if edge is to close to the point
                if (vertex - base*proj).get_length() < self.minRoomSize:
                    dropEdge = True
                    break

            if dropEdge:
                continue

            d = points[edge[0]].get_distance(points[edge[1]])
            edges[edge[0]] += [edge[1]]
            edges[edge[1]] += [edge[0]]
            maxSize[edge[0]] = min(maxSize[edge[0]], d - self.minRoomSize)
            maxSize[edge[1]] = min(maxSize[edge[1]], d - self.minRoomSize)
            segments += [Segment(points[edge[0]], end=points[edge[1]])]

        rooms = []
        for i in range(len(points)):
            roomSizes[i] = random.uniform(self.minRoomSize, maxSize[i])
            for j in edges[i]:
                maxSize[j] = min(maxSize[j],
                                 points[i].get_distance(points[j]) - roomSizes[i])
            rooms += [Circle(points[i], 0, roomSizes[i])]

        result = []
        for segment in segments:
            if len(segment.get_collisions(rooms)) == 2:
                result += [segment]

        return result+rooms


