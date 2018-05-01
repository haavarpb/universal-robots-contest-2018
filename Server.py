import bluetooth
import threading
import time
import socket
import Queue
import binascii
import pygatt


class Server:
    """A multiprotocol server class supporting TCP/IP and Bluetooth."""

    # Bluetooth addresses
    AGV_1_LILA = "34:15:13:1C:AF:0B"
    AGV_2_GREEN = "34:15:13:1C:6C:E6"

    # Bluetooth messages and commands
    AGV1_AT_P10 = 0
    AGV1_AT_P11 = 1
    COMMAND_MOVE_AGV1 = bytearray([0x32])
    AGV1_MOVING = 3
    AGV2_AT_P20 = 4
    AGV2_AT_P21 = 5
    COMMAND_MOVE_AGV2 = bytearray([0x36])
    AGV2_MOVING = 7

    # Bluetooth address type
    ADDRESS_TYPE = pygatt.BLEAddressType.public

    # TCP/IP messages and commands
    R1_PICK_READY = 8
    COMMAND_PICK_R1 = 9
    R1_FOTO_READY = 10
    COMMAND_R1_FOTO_DONE = 11
    R1_PLACE_READY = 12
    COMMAND_PLACE_R1 = 13
    R2_PICK_READY = 14
    COMMAND_PICK_R2 = 15
    R2_ORDER_READY = 16

    def __init__(self):
        #self.initBluetooth()
        self.initTCP()
        self.initAGVs(True,False)

        # State variables
        self.stateAGV1 = self.AGV1_AT_P10
        self.stateAGV2 = self.AGV2_AT_P20
        self.stateR1 = self.R1_FOTO_READY
        self.stateR2 = self.R2_PICK_READY


    def initTCP(self):
        """ Initialize TCP listener.
            - ip hardcoded here, port is arbitrary
        """

        self._ip = "192.168.5.197"
        self._tcp_port = 8887

        self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_socket.bind(("", self._tcp_port))

        self._tcp_thread = threading.Thread(target = self.listenTCPIncoming, name = "TCP listener")
        self._tcp_thread.daemon = True

        print "Initiating TCP listener at address/port [%s / %s]" %(self._ip, self._tcp_port)
        self._tcp_thread.start()


    def listenTCPIncoming(self):
        """ Handles a all incoming TCP connections and starts a new thread for each """

        self._tcp_socket.listen(5)
        while True:
            client_sock, address = self._tcp_socket.accept()
            client_thread = threading.Thread(target = self.listenTCPClient, name = address[0], args = [client_sock, address])
            client_thread.daemon = True
            client_thread.start()


    def listenTCPClient(self, client_sock, address):
        """ Handles a single TCP connection """

        print client_sock
        print address
        print "New client ", address
        data = client_sock.recv(1024)
        print data


    def initAGVs(self, init_AGV1, init_AGV2):
        """ Creates the Bluetooth connections to AGV1 & AGV2"""
        
        # Initialise connections and subscribe to the information stream
        if init_AGV1:
            self.adapter1 = pygatt.GATTToolBackend(hci_device="hci0")
            self.adapter1.start()
            self.AGV1 = self.adapter1.connect(self.AGV_1_LILA, address_type=self.ADDRESS_TYPE)
            self.AGV1.subscribe("0000ffe1-0000-1000-8000-00805f9b34fb",callback=self.handle_AGV1)
        
        if init_AGV2:
            self.adapter2 = pygatt.GATTToolBackend(hci_device="hci1")
            self.adapter2.start()
            self.AGV2 = self.adapter2.connect(self.AGV_2_GREEN, address_type=self.ADDRESS_TYPE)
            self.AGV2.subscribe("0000ffe1-0000-1000-8000-00805f9b34fb",callback=self.handle_AGV2)


    def handle_AGV1(self, handle, value):
        """handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification"""

        print("[BT]: Received data adapt.1 : HEX %s, ASCII %s" % (binascii.hexlify(value), value.decode("utf-8")))

        # Get the data as ASCII and take the last value
        data_str = value.decode("utf-8")
        newest_value = int(data_str[-1])

        # Change the state according to the received data
        if newest_value == self.AGV1_AT_P10:
            print("[BT]: AGV1 at P10.")
            self.stateAGV1 = self.AGV1_AT_P10

        elif newest_value == self.AGV1_AT_P11:
            print("[BT]: AGV1 at P11.")
            self.stateAGV1 = self.AGV1_AT_P11

        elif newest_value == self.AGV1_MOVING:
            print("[BT]: AGV1 moving.")
            self.stateAGV1 = self.AGV1_MOVING

        else:
            print("[BT]: Unknown message received.")


    def handle_AGV2(self, handle, value):
        """handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification"""

        print("[BT]: Received data adapt.2 : HEX %s, ASCII %s" % (binascii.hexlify(value), value.decode("utf-8")))

        # Get the data as ASCII and take the last value
        data_str = value.decode("utf-8")
        newest_value = int(data_str[-1])

        # Change the state according to the received data
        if newest_value == self.AGV2_AT_P20:
            print("[BT]: AGV2 at P20.")
            self.stateAGV2 = self.AGV2_AT_P20

        elif newest_value == self.AGV2_AT_P21:
            print("[BT]: AGV2 at P21.")
            self.stateAGV2 = self.AGV2_AT_P21

        elif newest_value == self.AGV2_MOVING:
            print("[BT]: AGV2 moving.")
            self.stateAGV2 = self.AGV2_MOVING

        else:
            print("[BT]: Unknown message received.")




s = Server()
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break

# device.char_write('0000ffe1-0000-1000-8000-00805f9b34fb', COMMAND_MOVE_AGV1)
# print("Sent data: (HEX) %s, ASCII %s" % (binascii.hexlify(COMMAND_MOVE_AGV1), COMMAND_MOVE_AGV1.decode("utf-8")))