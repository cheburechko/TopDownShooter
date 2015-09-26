import Queue, threading, sys
from client_simulation import LocalSimulation, InputControl
from udp import UDPClient
from registry import *
import pygame
import yappi

class Client():

    def __init__(self, address, nick):

        self.udpq = Queue.Queue()
        self.sim = LocalSimulation()
        self.client = UDPClient(address, self.udpq)
        #self.client.verbose = True
        #self.sim.verbose = True
        self.ic = InputControl(self.client, self.sim)

        threading.Thread(target=self.client.receive,
                         name="UDPClient").start()
        #thread.start_new_thread(self.client.keepAlive, ())
        threading.Thread(target=self.ic.processInputForever,
                      name="InputControl").start()
        threading.Thread(target=self.sim.renderForever,
                         name="Rendering").start()

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
                print 'Server disconnected'
                self.kill()
                break

            msg = Message.getMessage(udpMsg.data)
            if msg.type == Message.PING:
                self.client.send(PingMessage().toString())
                continue
            # update offsets
            self.sim.timestamp_offset = msg.timestamp - pygame.time.get_ticks()
            #print "Offset:", self.ic.timestamp_offset


            self.sim.processInput(msg)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'Usage: client.py ip port nickname'
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    nickname = sys.argv[3]

    yappi.start()
    client = Client((ip, port), nickname)
    try:
        client.serve()
    except KeyboardInterrupt:
        client.kill()
    finally:
        yappi.stop()
        yappi.get_func_stats().save("client_profile.bin")
        f = open("client_profile.txt", "w")
        yappi.get_thread_stats().print_all(f)
        f.close()
        print "Done."