__author__ = 'thepunchy'

from libs.Vec2D import Vec2d
from libs.Delaunay2d import Delaunay2d
import random
from EncircledRoomGenerator import EncircledRoomGenerator
from RandomWalkCorridorGenerator import RandomWalkCorridorGenerator
from geometry.merger import WireframeMerger
from GenerationDebugger import GenerationDebugger

from geometry_shortcut import *

class SparseLevelGenerator(object):
    def __init__(self):
        self.area = ((0, 0), (200, 200))
        self.roomNumber = 10
        self.minRoomSize = 10
        self.points = []
        self.roomGenerator = EncircledRoomGenerator()
        self.corridorGenerator = RandomWalkCorridorGenerator()

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


    def generate(self, debug=GenerationDebugger()):
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

        circles = []
        for i in range(len(points)):
            roomSizes[i] = random.uniform(self.minRoomSize, maxSize[i])
            for j in edges[i]:
                maxSize[j] = min(maxSize[j],
                                 points[i].get_distance(points[j]) - roomSizes[i])
            circles += [Circle(points[i], 0, roomSizes[i])]

        old_edges = edges
        edges = {}

        for p1 in old_edges:
            edges[p1] = []
            for p2 in old_edges[p1]:
                segment = Segment(points[p1], end=points[p2])
                if len(segment.get_collisions(circles)) == 2:
                    edges[p1] += [p2]

        #Reduce number of edges
        connected = True
        while connected:
            random_point = random.randint(0, len(points)-1)
            random_edge = random.randint(0, len(edges[random_point])-1)
            edge_end = edges[random_point][random_edge]
            edge = (random_point, edges[random_point][random_edge])
            del edges[random_point][random_edge]
            for i in range(len(edges[edge_end])):
                if edges[edge_end][i] == random_point:
                    break
            del edges[edge_end][i]

            q = [0]
            i = 0
            # TODO? slow and lazy
            while i < len(q):
                for p in edges[q[i]]:
                    if p not in q:
                        q += [p]
                i += 1
            if len(q) < len(points):
                connected = False
                edges[edge[0]] += [edge[1]]
                edges[edge[1]] += [edge[0]]


        rooms = []
        for circle in circles:
            rooms += [self.roomGenerator.generate(circle)]

        # Add corridors
        corridors = {i: dict() for i in edges}
        for p1 in edges:
            for p2 in edges[p1]:
                if p2 > p1:
                    corridors[p1][p2] = self.corridorGenerator.generate_corridor(
                        rooms[p1], rooms[p2], rooms,
                    )

        # Merge the shapes in a single wireframe
        q = [edges.keys()[0]]
        level = rooms[q[0]]
        merger = WireframeMerger()
        i = 0
        debug.debug_output(level)
        while i < len(q):
            for p in corridors[q[i]]:
                debug.debug_output([level, corridors[q[i]][p], rooms[p]])
                level = merger.merge_exterior(level, corridors[q[i]][p])
                debug.debug_output([level, rooms[p]])
                if p not in q:
                    q += [p]
                    level = merger.merge_exterior(level, rooms[p])
                debug.debug_output([level])

            i += 1

        return circles+[level]


