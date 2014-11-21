from udp import UDPServer
import Queue, thread
from server_simulation import ServerSimulation
from messages import *
import pygame

class Server():

    MSGS_PER_SECOND = 20

    def __init__(self, address):
        self.msgQ = Queue.Queue()
        self.server = UDPServer(address, self.msgQ)
        thread.start_new_thread(self.server.serve_forever, ())
        thread.start_new_thread(self.server.keepAlive, ())

        self.sim = ServerSimulation()
        thread.start_new_thread(self.sim.simulate, ())

        self.players = {}
        self.alive=True

        thread.start_new_thread(self.serve, ())

    def kill(self):
        self.server.shutdown()
        self.sim.alive = False
        self.alive= False

    def broadcastState(self):
        clock = pygame.time.Clock()
        while self.alive:
            clock.tick(self.MSGS_PER_SECOND)
            self.server.sendToAll(self.sim.getWorldState().toString())

    def serve(self):
        while self.alive:
            udpMsg = self.msgQ.get()
            if udpMsg.data == '':
                self.sim.removePlayer(self.players[udpMsg.connID])

            msg = Message.getMessage(udpMsg.data)
            if msg.type == Message.CONNECT:
                self.players[udpMsg.connID] = self.sim.addPlayer(msg)
                self.server.send(ConnectMessage(str(self.players[udpMsg.connID])).toString(),
                                 udpMsg.connID)
            elif msg.type == Message.CHAT:
                self.server.sendToAll(udpMsg.data)
            elif msg.type == Message.INPUT:
                self.sim.receiveInput(self.players[udpMsg.connID], msg)

server = Server(('localhost', 7000))
try:
    server.broadcastState()
except KeyboardInterrupt:
    server.kill()
