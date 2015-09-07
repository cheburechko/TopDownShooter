from messages import *
from models import *

epsilon = 10**-6

assert "Input message:"
inputMsg = InputMessage()
inputMsg.setButton(InputMessage.DOWN)
inputMsg.setButton(InputMessage.LEFT)
inputMsg.setButton(InputMessage.FIRE)
inputMsg.cursorX = 15.6
inputMsg.cursorY = 22.4
inputMsg.msecs = 15
inputMsg.timestamp = 1000

data = inputMsg.toString()

print "Input message"
newMsg = Message.getMessage(data)
assert newMsg.type == inputMsg.type, 'type'
assert newMsg.timestamp == inputMsg.timestamp, 'timestamp'
assert abs(newMsg.cursorX-inputMsg.cursorX)<epsilon, 'cursorX'
assert abs(newMsg.cursorY-inputMsg.cursorY)<epsilon, 'cursorY'
assert newMsg.msecs == inputMsg.msecs, 'msecs'

assert newMsg.isSet(InputMessage.DOWN) == inputMsg.isSet(InputMessage.DOWN), 'down'
assert newMsg.isSet(InputMessage.LEFT) == inputMsg.isSet(InputMessage.LEFT), 'left'
assert newMsg.isSet(InputMessage.FIRE) == inputMsg.isSet(InputMessage.FIRE), 'fire'
assert newMsg.isSet(InputMessage.RIGHT) == inputMsg.isSet(InputMessage.RIGHT), 'right'
assert newMsg.isSet(InputMessage.UP) == inputMsg.isSet(InputMessage.UP), 'up'

print "Chat message"
chatMessage = ChatMessage("hello", 10)
chatMessage.timestamp = 1000
data = chatMessage.toString()

newMsg = Message.getMessage(data)
assert newMsg.timestamp == chatMessage.timestamp, 'timestamp'
assert newMsg.msg == chatMessage.msg, 'msg'
assert newMsg.id == chatMessage.id, 'id'

print "Connect message:"
connectMessage = ConnectMessage('King')
connectMessage.timestamp = 1000
data = connectMessage.toString()

newMsg = Message.getMessage(data)
assert newMsg.timestamp == connectMessage.timestamp, 'timestamp'
assert newMsg.name == connectMessage.name, 'name'

print "Entity message:"
player = Player((100, 100,), 27, (0, 0, 100, 100), {})
player.speedx = 27
player.speedy = 43
entityMessage = EntityMessage(player)
data = entityMessage.toString()


newMsg = Message.getMessage(data)
newPlayer = Player((0, 0), 0, (0), {})
state = GameObject.unpackState(newMsg.state)
newPlayer.setState(state)
assert state[0] == player.type, 'type'
assert state[1] == player.id, 'id'
assert abs(player.x-newPlayer.x)<epsilon, 'x'
assert abs(player.y-newPlayer.y)<epsilon, 'y'
assert abs(player.speedx-newPlayer.speedx)<epsilon, 'speedx'
assert abs(player.speedy-newPlayer.speedy)<epsilon, 'speedy'
assert abs(player.angle-newPlayer.angle)<epsilon, 'angle'

print "List message"
listMessage = ListMessage()
listMessage.add(inputMsg)
listMessage.add(chatMessage)
listMessage.add(connectMessage)
listMessage.add(entityMessage)
data = listMessage.toString()

newListMsg = Message.getMessage(data)
newMsg = newListMsg.msgs[0]

print "Input message"
assert newMsg.type == inputMsg.type, 'type'
assert newMsg.timestamp == inputMsg.timestamp, 'timestamp'
assert abs(newMsg.cursorX-inputMsg.cursorX)<epsilon, 'cursorX'
assert abs(newMsg.cursorY-inputMsg.cursorY)<epsilon, 'cursorY'
assert newMsg.msecs == inputMsg.msecs, 'msecs'

assert newMsg.isSet(InputMessage.DOWN) == inputMsg.isSet(InputMessage.DOWN), 'down'
assert newMsg.isSet(InputMessage.LEFT) == inputMsg.isSet(InputMessage.LEFT), 'left'
assert newMsg.isSet(InputMessage.FIRE) == inputMsg.isSet(InputMessage.FIRE), 'fire'
assert newMsg.isSet(InputMessage.RIGHT) == inputMsg.isSet(InputMessage.RIGHT), 'right'
assert newMsg.isSet(InputMessage.UP) == inputMsg.isSet(InputMessage.UP), 'up'

print "Chat message"
newMsg = newListMsg.msgs[1]
assert newMsg.timestamp == chatMessage.timestamp, 'timestamp'
assert newMsg.msg == chatMessage.msg, 'msg'
assert newMsg.id == chatMessage.id, 'id'

print "Connect message:"
newMsg = newListMsg.msgs[2]
assert newMsg.timestamp == connectMessage.timestamp, 'timestamp'
assert newMsg.name == connectMessage.name, 'name'

print "Entity message:"
newMsg = newListMsg.msgs[3]
newPlayer = Player((0, 0), 0, "", (0), {})
state = GameObject.unpackState(newMsg.state)
newPlayer.setState(state)
assert state[0] == player.type, 'type'
assert state[1] == player.id, 'id'
assert abs(player.x-newPlayer.x)<epsilon, 'x'
assert abs(player.y-newPlayer.y)<epsilon, 'y'
assert abs(player.speedx-newPlayer.speedx)<epsilon, 'speedx'
assert abs(player.speedy-newPlayer.speedy)<epsilon, 'speedy'
assert abs(player.angle-newPlayer.angle)<epsilon, 'angle'
