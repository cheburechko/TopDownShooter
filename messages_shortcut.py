from messages.ConnectMessage import ConnectMessage
from messages.ChatMessage import ChatMessage
from messages.EntityMessage import EntityMessage
from messages.MetaMessage import MetaMessage
from messages.ListMessage import ListMessage
from messages.InputMessage import InputMessage
from messages.PingMessage import PingMessage
from messages.RemoveMessage import RemoveMessage
from messages.Message import Message

Message.registerType(InputMessage)
Message.registerType(ChatMessage)
Message.registerType(ListMessage)
Message.registerType(ConnectMessage)
Message.registerType(EntityMessage)
Message.registerType(PingMessage)
Message.registerType(RemoveMessage)
Message.registerType(MetaMessage)