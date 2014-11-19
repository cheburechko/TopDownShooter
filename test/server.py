from udp import UDPServer
import Queue, sys, thread

def printMsgs(queue, server):
    while True:
        msg = queue.get()
        print msg.data
        server.send('OK', msg.connID)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'Usage:script.py ip port'

    queue = Queue.Queue()

    try:
        server = UDPServer((sys.argv[1], int(sys.argv[2])), queue)
        thread.start_new_thread(printMsgs, (queue,server,))
        thread.start_new_thread(server.keepAlive, ())
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
