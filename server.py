from udp import UDPServer
import Queue, thread, sys
from server_simulation import ServerSimulation
from registry import *
import pygame
import yappi

class Server():

    MSGS_PER_SECOND = 20
    META_PERIOD = 1000
    DROP_PERIOD = 300

    def __init__(self, address, level=None):
        self.msgQ = Queue.Queue()
        self.server = UDPServer(address, self.msgQ)
        #self.server.verbose = True

        thread.start_new_thread(self.server.serve_forever, ())
        #thread.start_new_thread(self.server.keepAlive, ())

        self.sim = ServerSimulation(level)
        # Save level
        f = open("last_server_level.dat", "w")
        f.write(self.sim.getLevelState().toString())
        f.close()

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

    # Load level
    level = None
    if len(sys.argv) > 3:
        f = open("last_server_level.dat", "r")
        level = Message.getMessage(f.read())
        f.close()

    yappi.start()
    server = Server((ip, port), level)
    try:
        server.broadcastState()
    except KeyboardInterrupt:
        print 1
        yappi.stop()
        print 2
        server.kill()
        print 3
        yappi.get_func_stats().save("server_profile.bin")
        print 4
        f = open("server_profile.txt", "w")
        yappi.get_thread_stats().print_all(f)
        f.close()
        print 5
