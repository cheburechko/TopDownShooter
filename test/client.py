from udp import UDPClient
from Queue import Queue
import sys, thread

def print_msgs(queue):
    while 1:
        print "#:", queue.get().data

if __name__ == "__main__":
    queue = Queue()
    client = None

    thread.start_new_thread(print_msgs, (queue,))
    while 1:

        msg = raw_input('> ')
        words = msg.split()
        if len(words) == 0:
            continue

        command = words[0]

        if command == 'q':
            if client is not None:
                client.shutdown()
            break
        elif command == 'connect':
            client = UDPClient((words[1], int(words[2]),), queue)
            thread.start_new_thread(client.receive, ())
            thread.start_new_thread(client.keepAlive, ())
        else:
            client.send(msg)
