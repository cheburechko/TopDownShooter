import struct, SocketServer, Queue, socket, time

class UDPPacket():
    """
    Structure:
    [CONN_ID][MSG_ID][PACKETS][SUBID][DATA]
    0        4        8      10      16    1400
    CONN_ID - connection ID
    MSG_ID - message ID 0..2**32
    PACKETS - amount of packets for this message 1..2**16
    SUBID - packet ID 0..2**16
    DATA - data itself
    """
    PACKET_SIZE = 1400
    HEAD_SIZE = 12
    DATA_SIZE = PACKET_SIZE - HEAD_SIZE
    HEAD_FMT = "IIHH"

    def __init__(self, packet=None):
        if packet is not None:
            self.data = packet[self.HEAD_SIZE:]
            header = struct.unpack(self.HEAD_FMT, packet[:self.HEAD_SIZE])
            self.connID = header[0]
            self.msgID = header[1]
            self.packets = header[2]
            self.subID = header[3]
            self.packet = packet
    
    @classmethod
    def splitInPackets(cls, data, connID, msgID):
        """
        Constructs packets from data
        """
        packets = []
        amount = (len(data) - 1) / (cls.DATA_SIZE) + 1
        for i in range(amount):
            item = cls()
            item.connID = connID
            item.msgID = msgID
            item.packets = amount
            item.subID = i
            item.data = data[i*cls.DATA_SIZE:(i+1)*cls.DATA_SIZE]
            item.packet = struct.pack(cls.HEAD_FMT, connID, msgID, amount, i) + item.data
            #print 'New packet(', len(item.packet), ')', item.packet
            packets.append(item)

        return packets

class UDPMessage():
    """
    A complete UDP message
    """

    def __init__(self, packet):
        self.packets = [(packet.subID, packet)]
        self.amount = packet.packets
        self.connID = packet.connID
        self.msgID = packet.msgID
        self.data = None
        self.complete()


    def add(self, packet):
        self.packets += [(packet.subID, packet)]
        self.complete()

    def complete(self):
        if self.amount == len(self.packets):
            self.data = ''.join(x[1].data for x in sorted(self.packets, key=lambda x: x[0]))

class UDPConnection():
    """
    A very insecure connection between 2 servers
    """
    INITIAL_MSG = '!'
    KEEP_ALIVE = '#'
    DISCONNECT = ''

    def __init__(self, connID, remoteAddr, newsocket=None, timeout=0):
        self.connID = connID
        self.messages = {}
        self.msgID = 0
        self.addr = remoteAddr
        self.lastTime = time.time()

        # initialize connection
        if newsocket is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.connect(remoteAddr)
            self.send(self.INITIAL_MSG)
        else:
            self.socket = newsocket
            self.send(str(self.connID))

        self.socket.settimeout(timeout)

    def send(self, data):
        packets = UDPPacket.splitInPackets(data, self.connID, self.msgID)
        for packet in packets:
            #print "Sending: ", packet.packet
            #print "To: ", self.addr
            self.socket.sendto(packet.packet, self.addr)
        self.msgID += 1

    def receivePacket(self, packet):
        if packet.data == self.KEEP_ALIVE:
            self.lastTime = time.time()
            return None

        if packet.msgID in self.messages:
            self.messages[packet.msgID].add(packet)
        else:
            self.messages[packet.msgID] = UDPMessage(packet)

        msg = self.messages[packet.msgID]
        self.lastTime = time.time()

        if msg.data is not None:
            del self.messages[packet.msgID]
            return msg
        return None

    def receive(self):
        while True:
            #print 'Receiving...'
            packet = UDPPacket(self.socket.recv(UDPPacket.PACKET_SIZE))
            #print packet.msgID, packet.packets, packet.subID, packet.data

            msg = self.receivePacket(packet)
            if msg is not None:
                return msg



class UDPHandler(SocketServer.BaseRequestHandler):
    """
    Basically gives received packets to server.
    """
    def handle(self):
        #print 'Received:', self.request[0], self.client_address
        #print len(self.request[0])
        packet = UDPPacket(self.request[0])

        if packet.data == UDPConnection.INITIAL_MSG:
            self.server.createConnection(self.client_address, self.request[1])
        elif packet.data == UDPConnection.DISCONNECT:
            self.server.disconnect(packet)
        else:
            self.server.addPacket(packet)

class UDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    
    def __init__(self, addr, output, timeout=30):
        SocketServer.UDPServer.__init__(self, addr, UDPHandler)
        self.outputQ = output
        self.connections = {}
        self.timeout = timeout
        self.connNum = 0
        self.alive = True

    def createConnection(self, addr, socket):
        self.connNum += 1
        self.connections[self.connNum] = UDPConnection(\
                self.connNum, addr, socket, self.timeout)
        return self.connections[self.connNum]

    def addPacket(self, packet):
        msg = self.connections[packet.connID].receivePacket(packet)
        if msg is not None:
            self.outputQ.put(msg)

    def send(self, data, connID):
        try:
            self.connections[connID].send(data)
        except:
            self.disconnect(id=connID)

    def sendToAll(self, data):
        for connection in self.connections:
            self.send(data, connection)

    def disconnect(self, packet=None, id=None):
        if packet is None:
            if id is None:
                return
            packet = UDPPacket()
            packet.connID=id
            packet.data=UDPConnection.DISCONNECT
            packet.msgID=0
            packet.subID=0
        try:
            self.connections[packet.connID].send(UDPConnection.DISCONNECT)
        except:
            pass
        del self.connections[packet.connID]
        packet.packets = 1
        self.outputQ.put(UDPMessage(packet))

    def keepAlive(self):
        while self.alive:
            time.sleep(self.timeout / 3)
            stamp = time.time()
            disconnected = []
            for key in self.connections:
                if (stamp - self.connections[key].lastTime) > self.timeout:
                    disconnected += [key]
            for key in disconnected:
                self.disconnect(id=key)

            self.sendToAll(UDPConnection.KEEP_ALIVE)
    
    def shutdown(self):
        self.sendToAll(UDPConnection.DISCONNECT)
        self.alive = False
        SocketServer.UDPServer.shutdown(self)

class UDPClient():

    def __init__(self, address, outputQ, timeout=30):
        self.timeout = timeout
        self.connection = UDPConnection(\
                0, address, timeout=self.timeout)
        msg = self.connection.receive()
        self.connection.connID = int(msg.data)
        self.outputQ = outputQ
        self.alive = True

    def keepAlive(self):
        while self.alive:
            time.sleep(self.timeout / 3)
            self.send(UDPConnection.KEEP_ALIVE)

    def send(self, data):
        try:
            self.connection.send(data)
        except:
            self.handle_exceptions()

    def receive(self):
        try:
            while self.alive:
                msg = self.connection.receive()
                if msg.data == UDPConnection.DISCONNECT:
                    break
                self.outputQ.put(msg)
        except:
            self.handle_exceptions()

    def handle_exceptions(self):
        self.alive = False
        packet = UDPPacket()
        packet.data = ''
        packet.connID = self.connection.connID
        packet.packets = 1
        packet.subID = 0
        self.outputQ.put(UDPMessage(packet))

    def shutdown(self):
        self.connection.send(UDPConnection.DISCONNECT)
        self.alive = False
