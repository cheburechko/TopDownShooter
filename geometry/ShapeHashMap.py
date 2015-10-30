__author__ = 'thepunchy'

from collections import defaultdict

class NonStaticShape(Exception):
    pass


class StaticShapeHashMap(object):
    def __init__(self, cell_size, bbox):
        self.bbox = bbox
        self.cell_size = cell_size
        self.map = defaultdict(list)
        self.shapes = []

    def generate_keys(self, bbox):
        keys = []
        for x in range(int(bbox.left / self.cell_size), int(bbox.right / self.cell_size) + 1):
            for y in range(int(bbox.up / self.cell_size), int(bbox.down / self.cell_size) + 1):
                keys += [(x, y)]
        return keys

    def add_shape(self, shape):
        if not shape.static:
            raise NonStaticShape()
        self.bbox += shape.bbox
        self.shapes += [shape]
        keys = self.generate_keys(shape.bbox)
        for key in keys:
            self.map[key] += [len(self.shapes) - 1]

    def add_shapes(self, shapes):
        for shape in shapes:
            self.add_shape(shape)

    def get_shapes(self, bbox):
        keys = self.generate_keys(bbox)
        shape_flags = [False] * len(self.shapes)
        for key in keys:
            if not key in self.map:
                continue
            for i in self.map[key]:
                shape_flags[i] = True
        return (self.shapes[x] for x in filter(
            lambda i: shape_flags[i], xrange(len(self.shapes))
        ))

    def hit_test(self, shape):
        if not self.bbox.collide(shape.bbox):
            return False
        collisions = self.get_shapes(shape.bbox)
        for other in collisions:
            if shape.hit_test(other):
                return True
        return False