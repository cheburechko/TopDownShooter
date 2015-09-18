from udp import UDPServer
import Queue, thread, sys
from server_simulation import ServerSimulation
from registry import *
import pygame

class Server():

    MSGS_PER_SECOND = 20
    META_PERIOD = 1000
    DROP_PERIOD = 300

    def __init__(self, address):
        self.msgQ = Queue.Queue()
        self.server = UDPServer(address, self.msgQ)
        self.server.verbose = True

        thread.start_new_thread(self.server.serve_forever, ())
        thread.start_new_thread(self.server.keepAlive, ())

        self.sim = ServerSimulation()
        self.sim.verbose = False
        thread.start_new_thread(self.sim.simulate, ())

        self.players = {}
        self.alive=True
        self.lastPing = 0

        thread.start_new_thread(self.serve, ())

    def kill(self):
        self.server.shutdown()
        self.sim.alive = False
        self.alive= False

    def broadcastState(self):
        clock = pygame.time.Clock()
        timer = 0
        while self.alive:
            timer += clock.tick(self.MSGS_PER_SECOND)
            self.server.sendToAll(self.sim.getWorldState().toString())
            if timer > self.META_PERIOD:
                timer -= self.META_PERIOD
                self.server.sendToAll(self.sim.getMeta().toString())
                msg = PingMessage()
                self.lastPing = pygame.time.get_ticks()
                msg.timestamp = self.lastPing
                self.server.sendToAll(msg.toString())

    def serve(self):
        while self.alive:
            udpMsg = self.msgQ.get()
            if udpMsg.data == '':
                self.sim.removePlayer(self.players[udpMsg.connID])
                continue

            msg = Message.getMessage(udpMsg.data)

            if msg.type == Message.CONNECT:
                self.players[udpMsg.connID] = self.sim.addPlayer(msg)
                self.server.send(ConnectMessage(str(self.players[udpMsg.connID])).toString(),
                                 udpMsg.connID)
                self.server.send(self.sim.getLevelState().toString(),
                                 udpMsg.connID)
            elif (pygame.time.get_ticks() - msg.timestamp > self.DROP_PERIOD):
                continue
            elif msg.type == Message.CHAT:
                self.server.sendToAll(udpMsg.data)
            elif msg.type == Message.INPUT:
                if (udpMsg.connID in self.players):
                    self.sim.receiveInput(self.players[udpMsg.connID], msg)
            elif msg.type == Message.PING:
                if (udpMsg.connID in self.players):
                    self.sim.updateLatency(self.players[udpMsg.connID],
                                           (pygame.time.get_ticks() - self.lastPing)/2)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: client.py ip port'
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    if ip == 'any':
        ip = ''

    server = Server((ip, port))
    try:
        server.broadcastState()
    except KeyboardInterrupt:
        server.kill()
