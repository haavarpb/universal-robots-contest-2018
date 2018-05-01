import bluetooth
import threading
import time
import socket
import Queue
import binascii
import pygatt


class Server:
    """A multiprotocol server class supporting TCP/IP and Bluetooth."""

    def __init__(self):
        self.initBluetooth()
        self.initTCP()
        self.initAGVs()


    def initBluetooth(self):
        """ Initialize bluetooth listener.
            - To find your device's address enter the following in bash: hciconfig
            - Bluetooth port has to be under 25 """

        self._MAC = "7C:67:A2:A3:75:63"
        self._bt_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self._bt_thread = threading.Thread(target = self.listenBluetoothIncoming, name = "Bluetooth listener")
        self._bt_thread.daemon = True

        self._bt_port = 9
        self._bt_socket.bind(("", self._bt_port))

        print "Initiating Bluetooth listener at address/port [%s / %s]" %(self._MAC, self._bt_port)
        self._bt_thread.start()


    def listenBluetoothIncoming(self):
        """ Handles a all incoming Bluetooth connections and starts a new thread for each """

        self._bt_socket.listen(5)
        while True:
            client_sock, address = self._bt_socket.accept()
            client_thread = threading.Thread(target = self.listenBluetoothClient, name = address[0], args = [client_sock, address])
            client_thread.daemon = True
            client_thread.start()


    def listenBluetoothClient(self, client_sock, address):
        """ Handles a single Bluetooth connection """

        print "New client ", address
        data = client_sock.recv(1024)
        print data

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

    def initAGVs(self):
        self.AGV_1_LILA = "34:15:13:1C:AF:0B"
        self.AGV_2_GREEN = "34:15:13:1C:6C:E6"

        self.AGV_AT_P10 = 0
        self.AGV_AT_P11 = 1
        self.COMMAND_MOVE = bytearray([0x32])

        self.ADDRESS_TYPE = pygatt.BLEAddressType.public
        self.adapter = pygatt.GATTToolBackend()
        self.adapter.start()
        self.AGV1 = adapter.connect(AGV_1_LILA, address_type=ADDRESS_TYPE)
        # self.AGV2 .........

        self.AGV1.subscribe("0000ffe1-0000-1000-8000-00805f9b34fb",callback=handle_AGV1)
        # self.AGV2 .........

    def handle_AGV1(handle, value):
        """handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification"""
        print("Received data: (HEX) %s, ASCII %s" % (binascii.hexlify(value), value.decode("utf-8")))
        data_str = value.decode("utf-8")
        newest_value = int(data_str[-1])
        if newest_value == AGV_AT_P10:
            print("AGV at P10. Waiting 2 secs.")
            time.sleep(2)
            # device.char_write('0000ffe1-0000-1000-8000-00805f9b34fb', COMMAND_MOVE)
            # print("Sent data: (HEX) %s, ASCII %s" % (binascii.hexlify(COMMAND_MOVE), COMMAND_MOVE.decode("utf-8")))
        elif newest_value == AGV_AT_P11:
            print("AGV at P11. Waiting 4 secs.")
            time.sleep(4)




s = Server()
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break
