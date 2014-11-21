import Queue, thread
from client_simulation import LocalSimulation, InputControl
from udp import UDPClient
from messages import *
import pygame

class Client():

    def __init__(self, address, nick):

        self.udpq = Queue.Queue()
        self.sim = LocalSimulation()
        self.client = UDPClient(address, self.udpq)
        self.sim.verbose = True
        self.ic = InputControl(self.client, self.sim)

        thread.start_new_thread(self.client.receive, ())
        thread.start_new_thread(self.client.keepAlive, ())
        thread.start_new_thread(self.sim.renderForever, ())
        thread.start_new_thread(self.ic.processInputForever, ())

        self.client.send(ConnectMessage(nick).toString())

        self.alive = True

    def kill(self):
        self.client.shutdown()
        self.sim.alive = False
        self.ic.alive = False
        self.alive = False
        print 'Client finished'

    def serve(self):
        while self.alive:
            udpMsg = self.udpq.get()
            if udpMsg.data == '':
                self.kill()
                break

            msg = Message.getMessage(udpMsg.data)
            # update offsets
            self.sim.timestamp_offset = msg.timestamp - pygame.time.get_ticks()
            #print "Offset:", self.ic.timestamp_offset


            self.sim.processInput(msg)

client = Client(('localhost', 7000), 'any')
try:
    client.serve()
except KeyboardInterrupt:
    client.kill()