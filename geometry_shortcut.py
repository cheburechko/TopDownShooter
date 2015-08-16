__author__ = 'thepunchy'

from geometry.shape import Shape, Circle, Segment, Wireframe
from geometry.collisions import *

Shape.register_collider(collide_circle_circle, Circle, Circle)
Shape.register_collider(collide_segment_segment, Segment, Segment)
Shape.register_collider(collide_circle_segment, Circle, Segment)
Shape.register_collider(collide_circle_wireframe, Circle, Wireframe)
Shape.register_collider(collide_segment_wireframe, Segment, Wireframe)
Shape.register_collider(collide_wireframe_wireframe, Wireframe, Wireframe)