import bluetooth
import threading

class Server:
    """A multiprotocol server class supporting TCP/IP and Bluetooth."""

    def __init__(self):
        print "Initiating server"
        self.initBluetooth()


    def initBluetooth(self):
        self._MAC = "7c:67:a2:a3:75:5f"
        self._bt_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self._bt_thread = threading.Thread(target = self.listenBluetoothIncoming, name = "Bluetooth listener")

        self._bt_port = 0
        self._bt_socket.bind(("", self._bt_port))

        print "Initiating Bluetooth listener at address/port [%s / %s]" %(self._MAC, self._bt_port)
        self._bt_thread.start()
        print "Current threads: %s" %threading.enumerate()

    def listenBluetoothIncoming(self):
        self._bt_socket.listen(5)
        while True:
            client_sock, address = self._bt_socket.accept()
            print "New connection made with ", address
            client_thread = threading.Thread(target = listenBluetoothClient, name = "Client", args = [client_sock])
            client_thread.start()

    def listenBluetoothClient(self, client_sock):
        print "%s", client_sock.recv(1024)

    def shutdown(self):
        self._bt_socket.close()

s = Server()
