__author__ = 'thepunchy'
import sys, math


def collide_circle_circle(circle1, circle2):
    return circle1.pos.get_distance(circle2.pos) < (circle1.radius + circle2.radius)


def intersect_circle_segment(circle, segment):
    a = segment.pos.get_dist_sqrd(segment.end)
    b = 2 * segment.vector.dot(segment.pos - circle.pos)
    c = segment.pos.get_dist_sqrd(circle.pos) - circle.radius**2
    d = b**2 - 4*a*c
    if d < 0:
        return []
    elif d < sys.float_info.epsilon:
        points = [b/2/a/c]
    else:
        t1 = (-b - math.sqrt(d)) / 2 / a
        t2 = (-b + math.sqrt(d)) / 2 / a
        points = [t1, t2]
    result = []
    for p in points:
        if 1 >= p >= 0:
            result += [segment.end.interpolate_to(segment.pos, p)]
    return result


def collide_circle_segment(circle, segment):
    return len(intersect_circle_segment(circle, segment)) > 0


def ccw(vec1, vec2):
    return vec1.cross(vec2) < 0


def collide_segment_segment(segment1, segment2):
    return ((ccw(segment1.vector, segment2.pos - segment1.pos) !=
        ccw(segment1.vector, segment2.end - segment1.pos)) and
        (ccw(segment2.vector, segment1.end - segment2.pos) !=
         ccw(segment2.vector, segment1.pos - segment2.pos)))


def collide_circle_wireframe(circle, wireframe):
    for segment in wireframe:
        if collide_circle_segment(circle, segment):
            return True
    return False


# TODO optimize if neccessary
def collide_segment_wireframe(segment, wireframe):
    for segment2 in wireframe:
        if collide_segment_segment(segment, segment2):
            return True
    return False


# TODO optimize if neccessary
def collide_wireframe_wireframe(wireframe1, wireframe2):
    for segment1 in wireframe1:
        for segment2 in wireframe2:
            if collide_segment_segment(segment1, segment2):
                return True
    return False


