import struct, SocketServer, Queue

class UDPPacket():
    """
    Structure:
    [CONN_ID][MSG_ID][PACKETS][SUBID][DATA]
    0        2       6        8      10    1400
    ID - message id 0..2**32
    PACKETS - amount of packets for this message 1..2**16
    SUBID - packet id 0..2**16
    DATA - data itself
    """
    PACK_SIZE = 1400
    HEAD_SIZE = 10
    DATA_SIZE = PACK_SIZE - HEAD_SIZE
    HEAD_FMT = "HIHH"

    def __init__(self, packet=None):
        if packet is not None:
            self.data = packet[self.HEAD_SIZE:]
            header = struct.unpack(self.HEAD_FMT, packet[:self.HEAD_SIZE])
            self.connId = header[0]
            self.msgId = header[1]
            self.packets = header[2]
            self.subid = header[3]
            self.packet = packet
    
    @classmethod
    def splitInPackets(cls, data, connId, msgId):
        """
        Constructs packets from data
        """
        packets = []
        amount = (len(data) - 1) / (cls.DATA_SIZE) + 1
        for i in range(amount):
            item = cls()
            item.connId = connId
            item.msgId = msgId
            item.packets = amount
            item.subid = i
            item.data = data[i*cls.DATA_SIZE:(i+1)*DATA_SIZE]
            item.packet = struct.pack(cls.HEAD_FMT, connId, msgId, amount, i) + item.data
            packets.append(item)

        return packets

class UDPMessage():
    """
    An incomplete UDP message
    """

    def __init__(self, packet):
        self.packets = [(packet.subid, packet)]
        self.amount = packet.amount

    def compile(self):
        if self.amount != len(self.packets):
            return None

        return ''.join(x[1].data for x in sorted(self.packets, key=lambda x: x[0]))

    def add(self, packet):
        self.packets += [(packet.subid, packet)]

class UDPConnection():
    """
    A very insecure connection between 2 servers
    """
    def __init__(self, remoteAddr, remoteID, packet=None):
        self.remoteAddr = remoteAddr
        self.remoteID = remoteID
        self.messages = {}
        self.msgID = 0
        self.localID = 0
        if packet is not None:
            self.localID = int(packet.data)

        # Initialize/acknowledge conncetion
        send(str(remoteID))

    def acknowledge(self, packet, addr):
        self.localID = int(packet.data)
        self.remoteAddr = addr
    
    def send(self, data):
        packets = [UDPPacket.splitInPackets(data, self.localID, self.msgID)]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for packet in packets:
            s.sendto(packet, remoteAddr)

    def receive(self, packet, addr):
        self.remoteAddr = addr
        if packet.msgID in self.messages:
            msg = self.messages[packet.msgID].add(packet)
        else:
            self.message[packet.msgID] = UDPMessage(packet)

        msg = self.messages[packet.msgID].compile()

        if msg is not None:
            del self.messages[packet.msgID]

        return msg

class UDPHandler(SocketServer.BaseRequestHandler):
    """
    Basically gives received packets to server.
    """
    def handle(self):
        packet = UDPPacket(self.request[0])
        #Connection request
        if packet.connID == 0:
            self.server.createConnection(packet, self.client_address)
        #Connection acknowledge
        elif packet.msgID == 0:
            self.server.acknowledgeConnection(packet, self.clien_address)
        else
            self.server.addPacket(packet, self.client_address)

class UDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    
    def __init__(self, output):
        self.outputQ = output
        self.connections = {}
        self.connNum = 0

    def createConnection(packet, addr):
        self.connNum += 1
        self.connections[self.connNum] = UDPConnection(addr, self.connNum, packet)

    def acknowledgeConnection(packet, addr):
        self.connections[packet.connID].acknowledge(packet, addr)

    def addPacket(packet, addr):
        data = self.connections[packet.connID].receive(packet, addr)
        if data is not None:
            outputQ.put(data)

    def send(data, connID):
        self.connections[connID].send(data)

