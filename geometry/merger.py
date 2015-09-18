__author__ = 'thepunchy'

from geometry_shortcut import *
from libs.Vec2D import Vec2d

class WireframeMerger(object):
    def __init__(self):
        pass

    def merge_exterior(self, shape1, shape2):
        segments = self.__add_exterior_points(shape1, shape2) +\
            self.__add_exterior_points(shape2, shape1)
        segments = self.__sort_segments(segments)
        pos = self.__make_center(segments)
        return Wireframe(pos, 0, self.__get_points(segments, pos))

    def __is_segment_inside(self, p1, p2, shape):
        return shape.encloses_point((p1+p2)/2)

    def __sort_intersections(self, segment, intersections):
        if segment.pos.x == segment.end.x:
            return sorted(intersections,
                          key=lambda a: a.pos.y if isinstance(a, Segment) else a.y,
                          reverse=segment.pos.y > segment.end.y)
        else:
            return sorted(intersections,
                          key=lambda a: a.pos.x if isinstance(a, Segment) else a.x,
                          reverse=segment.pos.x > segment.end.x)

    def __add_exterior_points(self, shape1, shape2):
        points = []
        for s in shape1:
            intersection = self.__sort_intersections(s, shape2.intersect_segment(s)) + [s.end]
            last_point = s.pos
            for s1 in intersection:
                if isinstance(s1, Segment):
                    #TODO make proper algorithm
                    inside = self.__is_segment_inside(last_point, s1.pos, shape2)
                    if not inside:
                        points += [Segment(last_point, end=s1.pos)]
                    # Check whether segment lies inside
                    p1 = s1.pos + s1.vector.rotated(0.1) / 2
                    p2 = s1.pos + s1.vector.rotated(-0.1) / 2
                    if shape1.encloses_point(p1) and shape2.encloses_point(p1) or \
                       shape1.encloses_point(p2) and shape2.encloses_point(p2):
                        points += [s1]
                    last_point = s1.end
                else:
                    inside = self.__is_segment_inside(last_point, s1, shape2)
                    if not inside:
                        points += [Segment(last_point, end=s1)]
                    last_point = s1

        return points

    def __sort_segments(self, segments):
        result = [segments[0]]
        del segments[0]
        i = 0
        while len(segments) > 0:
            found = False
            for j in range(len(segments)):
                if result[i].end == segments[j].pos:
                    result += [segments[j]]
                    found = True
                    break
                elif result[i].end == segments[j].end and \
                                result[i].pos != segments[j].pos:
                    result += [Segment(segments[j].end, end=segments[j].pos)]
                    found = True
                    break
            if not found:
                #raise "Segments can't be sorted"
                break
            else:
                del segments[j]
            i += 1
        return result

    def __make_center(self, segments):
        v = Vec2d(0,0)
        for s in segments:
            v += s.pos
        return v / len(segments)

    def __get_points(self, segments, center):
        result = []
        for s in segments:
            result += [s.pos - center]
        return result