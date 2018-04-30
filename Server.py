import bluetooth
import threading
import time
import socket
#import message
#import json

class Server:
    """A multiprotocol server class supporting TCP/IP and Bluetooth."""

    def __init__(self):
        print "Initiating server"
        self.initBluetooth()
        self.initTCP()


    def initBluetooth(self):
        self._MAC = "7C:67:A2:A3:75:63"
        self._bt_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self._bt_thread = threading.Thread(target = self.listenBluetoothIncoming, name = "Bluetooth listener")
        self._bt_thread.daemon = True

        self._bt_port = 9
        self._bt_socket.bind(("", self._bt_port))

        print "Initiating Bluetooth listener at address/port [%s / %s]" %(self._MAC, self._bt_port)
        self._bt_thread.start()


    def listenBluetoothIncoming(self):
        self._bt_socket.listen(5)
        while True:
            client_sock, address = self._bt_socket.accept()
            client_thread = threading.Thread(target = self.listenBluetoothClient, name = address[0], args = [client_sock, address])
            client_thread.daemon = True
            client_thread.start()


    def listenBluetoothClient(self, client_sock, address):
        print "New client ", address
        while True:
            data = client_sock.recv(1024)
            print data


    def shutdown(self):
        self._bt_socket.close()

    def initTCP(self):
        self._ip = "192.168.1.101"
        self._tcp_port = 8888

        self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_socket.bind(("", self._tcp_port))

        self._tcp_thread = threading.Thread(target = self.listenTCPIncoming, name = "TCP listener")
        self._tcp_thread.daemon = True

        print "Initiating TCP listener at address/port [%s / %s]" %(self._ip, self._tcp_port)
        self._tcp_thread.start()

    def listenTCPIncoming(self):
        self._tcp_socket.listen(5)
        while True:
            client_sock, address = self._tcp_socket.accept()
            client_thread = threading.Thread(target = self.listenTCPClient, name = address[0], args = [client_sock, address])
            client_thread.daemon = True
            client_thread.start()

    def listenTCPClient(self, client_sock, address):
        print "New client ", address
        while True:
            data = client_sock.recv(1024)
            print data


s = Server()
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break

s.shutdown()
