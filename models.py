from game_objects.game_object import GameObject
from game_objects.bullet import Bullet
from game_objects.mob import Mob
from game_objects.player import Player

GameObject.registerType(Mob)
GameObject.registerType(Player)
GameObject.registerType(Bullet)