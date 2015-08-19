__author__ = 'thepunchy'
from messages_shortcut import *
from geometry_shortcut import *
from models import *

Message.registerType(InputMessage)
Message.registerType(ChatMessage)
Message.registerType(ListMessage)
Message.registerType(ConnectMessage)
Message.registerType(EntityMessage)
Message.registerType(PingMessage)
Message.registerType(RemoveMessage)
Message.registerType(MetaMessage)

Shape.register_shape(Circle)
Shape.register_shape(Segment)
Shape.register_shape(Wireframe)

Shape.register_collider(collide_circle_circle, Circle, Circle)
Shape.register_collider(collide_segment_segment, Segment, Segment)
Shape.register_collider(collide_circle_segment, Circle, Segment)
Shape.register_collider(collide_circle_wireframe, Circle, Wireframe)
Shape.register_collider(collide_segment_wireframe, Segment, Wireframe)
Shape.register_collider(collide_wireframe_wireframe, Wireframe, Wireframe)

GameObject.registerType(Mob)
GameObject.registerType(Player)
GameObject.registerType(Bullet)
GameObject.registerType(Walls)