__author__ = 'thepunchy'

class BoundingBox(object):
    def __init__(self, left, right, up, down):
        self.left = left
        self.right = right
        self.up = up
        self.down = down

    def collide(self, bbox):
        # Note that down > up
        return not (self.left > bbox.right or
                    self.right < bbox.left or
                    self.up > bbox.bottom or
                    self.down < bbox.up)

    def __add__(self, bbox):
        return BoundingBox(min(self.left, bbox.left),
                           max(self.right, bbox.right),
                           min(self.up, bbox.up),
                           max(self.down, bbox.down))
    __radd__ = __add__

    def __iadd__(self, bbox):
        self.left = min(self.left, bbox.left)
        self.right = max(self.right, bbox.right)
        self.up = min(self.up, bbox.up)
        self.down = max(self.down, bbox.down)